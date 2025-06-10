#!/usr/bin/env python3
"""
Optimized ML-Based Spacing Prediction for a 4-Element Radar Array

This script implements:
  - Synthetic DOA data generation using realistic phase-LUT + CRT unwrapping
  - A multi-frequency CRT-based phase unwrapping routine
  - A neural-network (MLP) regressor mapping target RMS AOA error → optimal spacings
  - CLI interface: train or load model, predict spacings for a given target error,
    enforce CRT ambiguity bounds, and verify achieved RMS error.

Dependencies:
  - Python 3.7+
  - numpy
  - scipy
  - tensorflow (2.x)
  - joblib
  - tqdm

Usage:
  # First run (trains model and saves to 'spacing_predictor.h5'):
    $ python spacing_predictor.py --train --num_samples 2000

  # Subsequent runs (loads saved model and predicts spacings):
    $ python spacing_predictor.py --target_error 0.1

  # To force retraining from scratch:
    $ python spacing_predictor.py --train --num_samples 5000 --force

Author: [Your Name]
Date: 2025-06-02
"""

import os
import argparse
import numpy as np
import joblib
from tqdm import tqdm
from scipy import optimize
from tensorflow import keras
from tensorflow.keras import layers

# Speed of light (m/s)
C = 3e8

# Design frequencies (Hz)
FREQS = np.array([1.8e9, 1.4e9, 1.0e9])  # Sorted descending for CRT
LAMS = C / FREQS

# Synthesis of maximum unambiguous spacing
F_MIN, F_MAX = 1.0e9, 1.8e9
SYNTH_LAMBDA = C / abs(F_MAX - F_MIN)           # Synthetic wavelength
MAX_SPACING = SYNTH_LAMBDA / 2.0                 # d_m ≤ Λ/2 to avoid ambiguity

# Noise standard deviation for phase measurements (radians)
NOISE_STD = 0.01


def wrap_to_2pi(angle):
    """
    Wrap an angle (in radians) into [0, 2π).
    """
    return angle % (2 * np.pi)


def crt_unwrap_baseline(phi_meas, freqs, dist, k_max=5):
    """
    Multi-frequency CRT unwrapping for a single baseline.

    Given:
      phi_meas: measured wrapped phases [phi_high, phi_mid, phi_low] (radians)
      freqs: corresponding frequencies [f_high, f_mid, f_low] (Hz), sorted descending
      dist: inter-element distance for this baseline (meters)
      k_max: maximum integer offset to search (±k_max)

    Returns:
      gamma_hat: estimate of gamma = (phi_true_i / f_i), often proportional to sin(theta)

    Approach:
      Solve for integers k_i such that unwrapped phases phi_i_unwrapped = phi_meas_i + 2π·k_i
      satisfy phi_i_unwrapped / f_i ≈ constant (γ). We minimize residual:
        ∑_{i} [ (phi_un_i / f_i - γ)² ], where γ = average(phi_un_i / f_i).
      We search over k_high ∈ [-k_max, k_max], k_mid ∈ [-k_max, k_max], k_low ∈ [-k_max, k_max]
      (3 nested loops, but k_max small → total combinations = (2·k_max+1)^3 ≈ 11^3 = 1331 max).
      Choose (k_i) minimizing residual. Then γ = mean(phi_un_i / f_i).

    Note: For performance, we can reduce search dimensionality. Here we do full brute force
    since k_max is small (e.g. 3 or 5) and we have only three frequencies.
    """
    best_gamma = None
    min_res = np.inf

    # Pre-allocate arrays for efficiency
    phi_meas_arr = np.array(phi_meas)
    freqs_arr = np.array(freqs)

    # Precompute 2π
    two_pi = 2.0 * np.pi

    # Loop over possible integer offsets
    for k_high in range(-k_max, k_max + 1):
        phi_high_un = phi_meas_arr[0] + two_pi * k_high

        for k_mid in range(-k_max, k_max + 1):
            phi_mid_un = phi_meas_arr[1] + two_pi * k_mid

            for k_low in range(-k_max, k_max + 1):
                phi_low_un = phi_meas_arr[2] + two_pi * k_low

                # Stack the three unwrapped phases
                phis_un = np.array([phi_high_un, phi_mid_un, phi_low_un])
                # Compute gamma candidates = phi_i / f_i
                gamma_cands = phis_un / freqs_arr
                # Mean gamma
                gamma_hat = np.mean(gamma_cands)
                # Compute residual sum of squares
                res = np.sum((gamma_cands - gamma_hat) ** 2)

                if res < min_res:
                    min_res = res
                    best_gamma = gamma_hat

    return best_gamma  # (rad·s/Hz)


def doa_estimation(meas_phases, freqs, spacings):
    """
    Estimate angle-of-arrival (theta_est) given measured wrapped phases,
    multi-frequency CRT unwrapping, and known spacings.

    Args:
      meas_phases: shape (num_baselines=3, num_freqs=3) array of wrapped phases (radians).
                   Ordering: meas_phases[m, i], where m=0..2 maps to baselines (d1, d1+d2, d1+d2+d3),
                   and i=0..2 maps to freqs sorted descending (1.8, 1.4, 1.0 GHz).
      freqs: array of frequencies (Hz) sorted descending, e.g. [1.8e9, 1.4e9, 1.0e9].
      spacings: array [d1, d2, d3] (meters).

    Returns:
      theta_est (degrees).
    """
    # Number of baselines = 3
    num_baselines = 3
    gamma_list = []

    # Cumulative distances for baselines: [d1, d1+d2, d1+d2+d3]
    d_cum = np.cumsum(spacings)

    # For each baseline m, extract its measured phases across frequencies,
    # call CRT unwrap to get gamma_m = phi_true_i/f_i
    for m in range(num_baselines):
        phi_meas_m = meas_phases[m, :]  # length-3 array
        dist_m = d_cum[m]

        # Call CRT unwrapping for this baseline
        gamma_m = crt_unwrap_baseline(phi_meas_m, freqs, dist_m, k_max=3)
        gamma_list.append(gamma_m)

    gamma_array = np.array(gamma_list)  # shape (3,)
    # Average gamma across baselines (mitigates noise)
    gamma_avg = np.mean(gamma_array)

    # Reconstruct sin(theta): gamma = (2π · dist · sinθ) / (C · 1/f)
    # Actually, phi_true_i = 2π · (dist · sinθ) / λ_i = 2π · (dist · sinθ) · (f_i / C)
    # => phi_true_i / f_i = (2π · dist · sinθ) / C = γ  (consistent across i)
    # Therefore, sinθ = (γ · C) / (2π · dist), but dist varies per baseline; we used average γ.
    # Use average dist? Actually, distance factor cancels because γ includes dist.
    # Since γ = (2π · dist_m · sinθ)/C => sinθ = (γ · C) / (2π · dist_m).
    # Different baselines give slightly different sinθ due to noise; thus compute sinθ_m for each
    # and average, or equivalently: use gamma_avg with an effective distance. Best practice:
    # Solve for sinθ in least-squares sense across baselines. I.e., minimimize ∑_m [ γ_m - (2π · d_cum[m] · sinθ)/C ]².

    def residual(sin_theta):
        """Cost function for least-squares fit of sinθ across baselines."""
        preds = (2.0 * np.pi * d_cum * sin_theta) / C
        return gamma_array - preds

    # Solve for sinθ via linear least squares: A sinθ = b, with A = (2π d_cum / C), b = gamma_array
    A = (2.0 * np.pi * d_cum) / C
    # Least-squares estimate: sinθ = (A·b) / (A·A)  (scalar, since A is vector)
    sin_theta_hat = np.dot(A, gamma_array) / np.dot(A, A)

    # Clamp sinθ_hat to [-1, 1]
    sin_theta_hat = np.clip(sin_theta_hat, -1.0, 1.0)
    theta_est = np.degrees(np.arcsin(sin_theta_hat))

    return theta_est


def simulate_rms_error(spacings, angles, freqs, noise_std=NOISE_STD):
    """
    Simulate DOA estimation over many test angles for a given set of spacings [d1, d2, d3].
    Returns the RMS AOA estimation error (degrees).

    Args:
      spacings: list or array [d1, d2, d3] (meters).
      angles: 1D array of true angles (degrees) to test, e.g. np.linspace(-80, 80, 161).
      freqs: array of frequencies (Hz) sorted descending (length 3).
      noise_std: standard deviation of Gaussian noise added to wrapped phases (radians).

    Returns:
      rms_error: Root-Mean-Square of (theta_est − theta_true), in degrees.
    """
    errors = []

    # Cumulative positions: [0, d1, d1+d2, d1+d2+d3]
    pos = np.concatenate([[0.0], np.cumsum(spacings)])

    for theta_true in angles:
        # True (noise-free) phases for each baseline and frequency
        # Shape: (num_baselines=3, num_freqs=3)
        phi_true = np.zeros((3, 3))
        sin_theta = np.sin(np.radians(theta_true))

        for idx_f, f in enumerate(freqs):
            lam = C / f
            # Phase at each element (excluding reference at 0): phi = (2π/λ) · pos[j] · sinθ
            # We only store phase differences between element 0 and element m:
            phis_all = (2.0 * np.pi / lam) * pos * sin_theta  # length-4 array
            # Baseline phases = phis_all[1:] (phases at elements 1,2,3)
            phi_true[:, idx_f] = wrap_to_2pi(phis_all[1:])  # wrap each to [0,2π)

        # Add Gaussian noise to each measured baseline-phase (independently)
        phi_meas = wrap_to_2pi(phi_true + np.random.normal(0.0, noise_std, phi_true.shape))

        # Estimate DOA using CRT-based unwrapping
        theta_est = doa_estimation(phi_meas, freqs, spacings)

        err = theta_est - theta_true
        errors.append(err)

    errors = np.array(errors)
    rms_error = np.sqrt(np.mean(errors ** 2))
    return rms_error


def generate_synthetic_dataset(num_samples=1000, angles=np.linspace(-60, 60, 81)):
    """
    Generate synthetic (target_error → optimal spacings) dataset.

    For each sample:
      - Randomly pick spacing triple (d1, d2, d3) uniformly within [0.01 m, MAX_SPACING*1.2]
        (allow some overshoot beyond unambiguous bound to show clipping during prediction).
      - Compute RMS AOA error for that triple using simulate_rms_error().
      - Record (target_error = RMS_error, spacings = [d1, d2, d3]).

    Returns:
      X: np.ndarray shape (num_samples, 1) → target errors (degrees).
      Y: np.ndarray shape (num_samples, 3) → spacing triples (meters).
    """
    X = np.zeros((num_samples, 1))
    Y = np.zeros((num_samples, 3))

    for i in tqdm(range(num_samples), desc="Generating dataset"):
        # Uniformly sample d1,d2,d3 between 0.01 m and MAX_SPACING*1.2
        d1 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        d2 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        d3 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        spacings = np.array([d1, d2, d3])

        # Simulate RMS error over a grid of angles
        rms_err = simulate_rms_error(spacings, angles, FREQS, noise_std=NOISE_STD)

        X[i, 0] = rms_err
        Y[i, :] = spacings

    return X, Y


def build_mlp_model(input_shape=(1,)):
    """
    Build and compile the MLP regressor model: input → target_error; output → [d1, d2, d3].

    Architecture:
      - Input layer: shape (1,)
      - Dense 64 → BatchNorm → ReLU → Dropout(0.2)
      - Dense 64 → BatchNorm → ReLU → Dropout(0.2)
      - Dense 32 → BatchNorm → ReLU → Dropout(0.2)
      - Output Dense 3 → Softplus (ensures positivity)

    Returns:
      model: compiled keras Model
    """
    inputs = keras.Input(shape=input_shape, name="target_error_input")

    x = layers.Dense(64, name="dense_1")(inputs)
    x = layers.BatchNormalization(name="bn_1")(x)
    x = layers.Activation("relu", name="relu_1")(x)
    x = layers.Dropout(0.2, name="dropout_1")(x)

    x = layers.Dense(64, name="dense_2")(x)
    x = layers.BatchNormalization(name="bn_2")(x)
    x = layers.Activation("relu", name="relu_2")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)

    x = layers.Dense(32, name="dense_3")(x)
    x = layers.BatchNormalization(name="bn_3")(x)
    x = layers.Activation("relu", name="relu_3")(x)
    x = layers.Dropout(0.2, name="dropout_3")(x)

    outputs = layers.Dense(3, activation="softplus", name="spacings_output")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="SpacingPredictorMLP")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="mse",
        metrics=["mae"]
    )
    return model


def train_model(X_train, Y_train, model_path="spacing_predictor.h5",
                batch_size=32, epochs=200, validation_split=0.1):
    """
    Train the MLP model mapping target_error → [d1, d2, d3].

    If a saved model already exists at model_path, it will be overwritten.

    Returns:
      model: trained keras Model
    """
    model = build_mlp_model(input_shape=(1,))

    # Early stopping callback
    early_stop = keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=15, restore_best_weights=True
    )

    # Fit model
    history = model.fit(
        X_train,
        Y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_split=validation_split,
        callbacks=[early_stop],
        verbose=2
    )

    # Save the best model
    model.save(model_path)
    print(f"Model saved to '{model_path}'")
    return model


def load_model(model_path="spacing_predictor.h5"):
    """
    Load a saved Keras model from disk for inference (compile=False to avoid missing‐loss errors).
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_path}' not found.")
    model = keras.models.load_model(model_path, compile=False)
    return model



def enforce_crt_bounds(spacings):
    """
    Clip each spacing to be ≤ MAX_SPACING (Λ/2).

    Args:
      spacings: array [d1, d2, d3]
    Returns:
      clipped_spacings: array [d1', d2', d3']
    """
    return np.minimum(spacings, MAX_SPACING)


def main():
    parser = argparse.ArgumentParser(
        description="ML-based spacing predictor for 4-element radar array"
    )
    parser.add_argument(
        "--train", action="store_true",
        help="Generate synthetic dataset and train model from scratch."
    )
    parser.add_argument(
        "--num_samples", type=int, default=2000,
        help="Number of synthetic samples to generate when training."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="When training, force regeneration even if model file exists."
    )
    parser.add_argument(
        "--target_error", type=float, default=0.1,
        help="Desired RMS AOA error (degrees) for prediction."
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="After prediction, simulate to verify achieved RMS error."
    )
    args = parser.parse_args()

    model_path = "spacing_predictor.h5"

    # === TRAINING MODE ===
    if args.train:
        if os.path.exists(model_path) and not args.force:
            print(f"Model file '{model_path}' already exists. Use --force to retrain.")
            return

        print("Generating synthetic dataset...")
        X, Y = generate_synthetic_dataset(num_samples=args.num_samples)
        print("Dataset generation complete.")
        print("Training MLP model...")
        model = train_model(X, Y, model_path=model_path)
        print("Training complete.")
        return

    # === PREDICTION MODE ===
    # Load or prompt to train if missing
    if not os.path.exists(model_path):
        print(f"Model file '{model_path}' not found. Run with --train first.")
        return

    print(f"Loading model from '{model_path}'...")
    model = load_model(model_path)
    print("Model loaded successfully.\n")

    # Prepare input for prediction
    target_err = np.array([[args.target_error]], dtype=np.float32)

    # Predict spacings
    pred_spacings = model.predict(target_err, verbose=0).reshape(-1)
    d1_pred, d2_pred, d3_pred = pred_spacings

    # Enforce CRT-derived ambiguity bounds
    d1_clipped, d2_clipped, d3_clipped = enforce_crt_bounds(pred_spacings)

    # Compute cumulative antenna positions
    positions = np.array([0.0, d1_clipped, d1_clipped + d2_clipped, d1_clipped + d2_clipped + d3_clipped])

    # Output formatted results
    print(f"Target RMS AOA error: {args.target_error:.3f}°\n")
    print("Predicted inter-element spacings (meters):")
    print(f"  d1 = {d1_pred:.6f}   (clipped: {d1_clipped:.6f})")
    print(f"  d2 = {d2_pred:.6f}   (clipped: {d2_clipped:.6f})")
    print(f"  d3 = {d3_pred:.6f}   (clipped: {d3_clipped:.6f})")
    print("\nAntenna positions (cumulative, meters):")
    for idx, pos in enumerate(positions):
        print(f"  Element {idx}: {pos:.6f}")

    # Optional verification
    if args.verify:
        print("\nVerifying achieved RMS AOA error via simulation...")
        # Use a fine grid of angles for verification
        verify_angles = np.linspace(-75, 75, 151)
        rms_err_achieved = simulate_rms_error(
            [d1_clipped, d2_clipped, d3_clipped],
            verify_angles,
            FREQS,
            noise_std=NOISE_STD
        )
        print(f"Achieved RMS AOA error: {rms_err_achieved:.4f}° (target was {args.target_error:.3f}°)")
        if rms_err_achieved > args.target_error * 1.1:
            print("Warning: Achieved error significantly exceeds target. Consider retraining or adjusting model.")
        else:
            print("Verification passed: Achieved error is within acceptable range of target.")

    print("\nDone.")


if __name__ == "__main__":
    main()
