import numpy as np
from backend.ml.constants import C, FREQS, MAX_SPACING, NOISE_STD
from backend.ml.dataset import wrap_to_2pi, simulate_rms_error

def test_wrap_to_2pi():
    assert np.isclose(wrap_to_2pi(0), 0)
    assert np.isclose(wrap_to_2pi(2 * np.pi), 0)
    assert np.isclose(wrap_to_2pi(3 * np.pi), np.pi)
    assert np.isclose(wrap_to_2pi(-np.pi), np.pi)

def test_simulate_rms_error():
    spacings = [0.1, 0.1, 0.1]
    angles = np.array([-10, 0, 10])
    err = simulate_rms_error(spacings, angles, FREQS, noise_std=0.0)
    assert isinstance(err, float)
    assert err >= 0.0
    # Without noise, the error should be extremely small
    assert err < 1.0 
