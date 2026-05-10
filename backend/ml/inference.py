import os
import numpy as np
from backend.ml.constants import MAX_SPACING, FREQS, NOISE_STD
from backend.ml.model import load_model, train_model
from backend.ml.dataset import generate_synthetic_dataset, simulate_rms_error

MODEL_PATH = os.path.join(os.path.dirname(__file__), "spacing_predictor.h5")

def enforce_crt_bounds(spacings):
    return np.minimum(spacings, MAX_SPACING)

def predict_spacings(target_error: float):
    # Ensure model exists, otherwise generate some quick dummy weights for dev (in prod you'd pre-train)
    if not os.path.exists(MODEL_PATH):
        print("Model not found, training a quick dummy model for demonstration...")
        X, Y = generate_synthetic_dataset(num_samples=100) # Quick train
        train_model(X, Y, model_path=MODEL_PATH, epochs=5)

    model = load_model(MODEL_PATH)
    target_err_arr = np.array([[target_error]], dtype=np.float32)
    
    pred_spacings = model.predict(target_err_arr, verbose=0).reshape(-1)
    
    # Enforce CRT-derived ambiguity bounds
    clipped_spacings = enforce_crt_bounds(pred_spacings)
    
    # Compute positions
    d1, d2, d3 = clipped_spacings
    positions = [0.0, float(d1), float(d1 + d2), float(d1 + d2 + d3)]

    return {
        "spacings": [float(d1), float(d2), float(d3)],
        "positions": positions
    }

def verify_spacings(spacings: list, target_error: float):
    d1, d2, d3 = spacings
    verify_angles = np.linspace(-75, 75, 151)
    rms_err_achieved = simulate_rms_error(
        [d1, d2, d3],
        verify_angles,
        FREQS,
        noise_std=NOISE_STD
    )
    
    return {
        "achieved_error": float(rms_err_achieved),
        "target_error": float(target_error),
        "acceptable": bool(rms_err_achieved <= target_error * 1.1)
    }
