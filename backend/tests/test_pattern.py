import numpy as np
from ml.pattern import calculate_array_factor

def test_calculate_array_factor():
    spacings = [0.1, 0.1, 0.1]
    angles_deg, af_db = calculate_array_factor(spacings)
    
    # We requested 361 points by default for -90 to 90
    assert len(angles_deg) == 361
    assert len(af_db) == 361
    
    # Max array factor should be at broadside (0 degrees)
    # The value at 0 deg should be 0 dB (normalized max)
    zero_deg_idx = angles_deg.index(0.0)
    assert np.isclose(af_db[zero_deg_idx], 0.0)
    
    # The rest of the values should be <= 0 dB
    assert all(val <= 0.0 for val in af_db)
