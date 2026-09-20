"""
Data Drift Detection Utilities for CampusPulse AI.
Calculates Population Stability Index (PSI) to identify feature distribution shifts
between training baseline and live inference data.
"""

import numpy as np

def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_buckets: int = 10) -> float:
    """
    Computes the Population Stability Index (PSI) between expected (baseline/training)
    and actual (current production inference) continuous feature distributions.
    
    Standard Interpretation:
      PSI < 0.10: No significant distribution change (Model is stable)
      0.10 <= PSI < 0.25: Moderate drift detected (Review / monitoring recommended)
      PSI >= 0.25: Significant drift detected (Action required / Retraining recommended)
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)

    # Remove NaNs
    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]

    if len(expected) < 10 or len(actual) < 10:
        return 0.0

    # Quantile bin edges based on expected baseline
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bin_edges = np.percentile(expected, percentiles)
    bin_edges[0] -= 1e-5
    bin_edges[-1] += 1e-5

    # Ensure strictly monotonic bin edges
    for i in range(1, len(bin_edges)):
        if bin_edges[i] <= bin_edges[i - 1]:
            bin_edges[i] = bin_edges[i - 1] + 1e-4

    # Count occurrences in each bin
    expected_counts, _ = np.histogram(expected, bins=bin_edges)
    actual_counts, _ = np.histogram(actual, bins=bin_edges)

    # Normalize to proportions with Laplace smoothing to prevent division by zero
    expected_pct = (expected_counts + 1e-4) / (len(expected) + 1e-4 * num_buckets)
    actual_pct = (actual_counts + 1e-4) / (len(actual) + 1e-4 * num_buckets)

    # Compute PSI formula: sum((Actual - Expected) * ln(Actual / Expected))
    psi_value = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(round(max(0.0, psi_value), 4))


def interpret_psi(psi_value: float) -> dict:
    if psi_value < 0.10:
        return {
            'status': 'STABLE',
            'alert': False,
            'description': 'No significant drift observed. Baseline distribution matches production.'
        }
    elif psi_value < 0.25:
        return {
            'status': 'MODERATE_DRIFT',
            'alert': False,
            'description': 'Moderate feature shift detected. Ongoing monitoring recommended.'
        }
    else:
        return {
            'status': 'SIGNIFICANT_DRIFT',
            'alert': True,
            'description': 'Significant data drift detected! Retraining and feature review recommended.'
        }
