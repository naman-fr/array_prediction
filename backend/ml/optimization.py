import numpy as np
from scipy.optimize import minimize
from ml.dataset import simulate_rms_error
from ml.constants import MAX_SPACING, FREQS, DEFAULT_SNR_DB
import logging

logger = logging.getLogger("sentinel-ml-optimizer")

def optimize_spacings(seed_spacings, target_error, snr_db=DEFAULT_SNR_DB):
    """
    Perform a local search around the ML-predicted spacings to find 
    the absolute most optimal configuration that satisfies the target error
    while minimizing the simulated RMS error.
    """
    
    # Validation angles for optimization (coarser for speed)
    opt_angles = np.linspace(-60, 60, 41)
    
    def objective(spacings):
        # We minimize the achieved RMS error
        # Penalize if it exceeds the target error significantly
        achieved = simulate_rms_error(spacings, opt_angles, FREQS, snr_db=snr_db)
        
        # Soft constraint: we want to be as close to or better than target_error
        # We use a weighted penalty if achieved > target_error
        penalty = 0
        if achieved > target_error:
            penalty = (achieved - target_error) * 10.0
            
        return achieved + penalty

    # Boundaries: spacings must be positive and within CRT limits
    bounds = [(0.01, MAX_SPACING * 1.5)] * 3
    
    logger.info(f"Starting physics-driven optimization with seed: {seed_spacings}")
    
    res = minimize(
        objective, 
        seed_spacings, 
        method='L-BFGS-B', 
        bounds=bounds,
        options={'maxiter': 20, 'eps': 0.01} # Keep it fast for real-time dashboard
    )
    
    if res.success:
        optimized_spacings = res.x.tolist()
        logger.info(f"Optimization successful. Refined spacings: {optimized_spacings}")
        return optimized_spacings
    else:
        logger.warning("Optimization did not converge, falling back to seed.")
        return seed_spacings
