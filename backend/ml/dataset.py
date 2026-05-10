import numpy as np
from tqdm import tqdm
from backend.ml.constants import C, FREQS, MAX_SPACING, DEFAULT_SNR_DB

def wrap_to_2pi(angle):
    """Wrap an angle (in radians) into [0, 2pi)."""
    return angle % (2 * np.pi)

def crt_unwrap_baseline(phi_meas, freqs, dist):
    """
    Robust Hierarchical CRT (Difference-Frequency Unwrapping).
    Instead of brute-force loop, we use the difference between adjacent frequencies
    to create a synthetic coarse wavelength, which provides an unambiguous coarse
    estimate of gamma, which is then used to resolve ambiguities of the fine frequencies.
    """
    phi_meas_arr = np.array(phi_meas)
    freqs_arr = np.array(freqs)
    
    # Sort frequencies descending just in case
    sort_idx = np.argsort(freqs_arr)[::-1]
    f_sorted = freqs_arr[sort_idx]
    phi_sorted = phi_meas_arr[sort_idx]
    
    # 1. Compute difference frequency (lowest ambiguity)
    f_diff = f_sorted[0] - f_sorted[-1]
    phi_diff = wrap_to_2pi(phi_sorted[0] - phi_sorted[-1])
    
    # 2. Coarse estimate of gamma = (t / c) or equivalent
    gamma_coarse = phi_diff / (2.0 * np.pi * f_diff)
    
    # 3. Use coarse estimate to unwrap the highest frequency (finest resolution)
    f_fine = f_sorted[0]
    phi_fine = phi_sorted[0]
    
    # Find integer ambiguity k for the fine frequency
    k_fine = np.round(gamma_coarse * f_fine - phi_fine / (2.0 * np.pi))
    
    # 4. Fine estimate of gamma
    gamma_fine = (phi_fine + 2.0 * np.pi * k_fine) / (2.0 * np.pi * f_fine)
    
    return gamma_fine

def doa_estimation(meas_phases, freqs, spacings):
    num_baselines = 3
    gamma_list = []
    d_cum = np.cumsum(spacings)

    for m in range(num_baselines):
        phi_meas_m = meas_phases[m, :]
        dist_m = d_cum[m]
        gamma_m = crt_unwrap_baseline(phi_meas_m, freqs, dist_m)
        gamma_list.append(gamma_m)

    gamma_array = np.array(gamma_list)
    # Solve sin(theta) = gamma * C / dist
    # Convert gamma back to phase scale (gamma * 2*pi is used in the regression matrix)
    A = (d_cum) / C
    sin_theta_hat = np.dot(A, gamma_array) / np.dot(A, A)
    sin_theta_hat = np.clip(sin_theta_hat, -1.0, 1.0)
    theta_est = np.degrees(np.arcsin(sin_theta_hat))

    return theta_est

def get_noise_std_from_snr(snr_db):
    """Calculate phase noise standard deviation from SNR."""
    snr_linear = 10 ** (snr_db / 10.0)
    return 1.0 / np.sqrt(2.0 * snr_linear)

def simulate_rms_error(spacings, angles, freqs, snr_db=DEFAULT_SNR_DB):
    noise_std = get_noise_std_from_snr(snr_db)
    errors = []
    pos = np.concatenate([[0.0], np.cumsum(spacings)])

    for theta_true in angles:
        phi_true = np.zeros((3, 3))
        sin_theta = np.sin(np.radians(theta_true))

        for idx_f, f in enumerate(freqs):
            lam = C / f
            phis_all = (2.0 * np.pi / lam) * pos * sin_theta
            phi_true[:, idx_f] = wrap_to_2pi(phis_all[1:])

        phi_meas = wrap_to_2pi(phi_true + np.random.normal(0.0, noise_std, phi_true.shape))
        theta_est = doa_estimation(phi_meas, freqs, spacings)

        err = theta_est - theta_true
        errors.append(err)

    errors = np.array(errors)
    rms_error = np.sqrt(np.mean(errors ** 2))
    return rms_error

def generate_synthetic_dataset(num_samples=1000, angles=np.linspace(-60, 60, 81), snr_db=DEFAULT_SNR_DB):
    X = np.zeros((num_samples, 1))
    Y = np.zeros((num_samples, 3))

    for i in tqdm(range(num_samples), desc="Generating dataset"):
        d1 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        d2 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        d3 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        spacings = np.array([d1, d2, d3])

        rms_err = simulate_rms_error(spacings, angles, FREQS, snr_db=snr_db)

        X[i, 0] = rms_err
        Y[i, :] = spacings

    return X, Y
