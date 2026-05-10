import numpy as np
from tqdm import tqdm
from backend.ml.constants import C, FREQS, MAX_SPACING, NOISE_STD

def wrap_to_2pi(angle):
    """Wrap an angle (in radians) into [0, 2pi)."""
    return angle % (2 * np.pi)

def crt_unwrap_baseline(phi_meas, freqs, dist, k_max=5):
    best_gamma = None
    min_res = np.inf
    phi_meas_arr = np.array(phi_meas)
    freqs_arr = np.array(freqs)
    two_pi = 2.0 * np.pi

    for k_high in range(-k_max, k_max + 1):
        phi_high_un = phi_meas_arr[0] + two_pi * k_high
        for k_mid in range(-k_max, k_max + 1):
            phi_mid_un = phi_meas_arr[1] + two_pi * k_mid
            for k_low in range(-k_max, k_max + 1):
                phi_low_un = phi_meas_arr[2] + two_pi * k_low

                phis_un = np.array([phi_high_un, phi_mid_un, phi_low_un])
                gamma_cands = phis_un / freqs_arr
                gamma_hat = np.mean(gamma_cands)
                res = np.sum((gamma_cands - gamma_hat) ** 2)

                if res < min_res:
                    min_res = res
                    best_gamma = gamma_hat

    return best_gamma

def doa_estimation(meas_phases, freqs, spacings):
    num_baselines = 3
    gamma_list = []
    d_cum = np.cumsum(spacings)

    for m in range(num_baselines):
        phi_meas_m = meas_phases[m, :]
        dist_m = d_cum[m]
        gamma_m = crt_unwrap_baseline(phi_meas_m, freqs, dist_m, k_max=3)
        gamma_list.append(gamma_m)

    gamma_array = np.array(gamma_list)
    A = (2.0 * np.pi * d_cum) / C
    sin_theta_hat = np.dot(A, gamma_array) / np.dot(A, A)
    sin_theta_hat = np.clip(sin_theta_hat, -1.0, 1.0)
    theta_est = np.degrees(np.arcsin(sin_theta_hat))

    return theta_est

def simulate_rms_error(spacings, angles, freqs, noise_std=NOISE_STD):
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

def generate_synthetic_dataset(num_samples=1000, angles=np.linspace(-60, 60, 81)):
    X = np.zeros((num_samples, 1))
    Y = np.zeros((num_samples, 3))

    for i in tqdm(range(num_samples), desc="Generating dataset"):
        d1 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        d2 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        d3 = np.random.uniform(0.01, MAX_SPACING * 1.2)
        spacings = np.array([d1, d2, d3])

        rms_err = simulate_rms_error(spacings, angles, FREQS, noise_std=NOISE_STD)

        X[i, 0] = rms_err
        Y[i, :] = spacings

    return X, Y
