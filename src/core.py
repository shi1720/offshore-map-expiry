"""Accounting operations for issuer-nationality maps (rows = residence)."""
import numpy as np


def project(weights, matrix):
    """Explicit contraction avoids platform BLAS floating-status artifacts."""
    result=np.einsum('i,ij->j',weights,matrix,optimize=False)
    if not np.isfinite(result).all():raise ArithmeticError('Nonfinite projection')
    return result


def validate_map(matrix, atol=1e-6):
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise ValueError('Map must be a finite matrix')
    if (matrix < -atol).any() or not np.allclose(matrix.sum(axis=1), 1, atol=atol, rtol=0):
        raise ValueError('Map rows must be probability vectors')
    return matrix


def tv(p, q):
    return float(np.abs(np.asarray(p)-np.asarray(q)).sum()/2)


def decompose(w0, w1, m0, m1):
    """Exact symmetric two-factor decomposition; outputs nationality vectors."""
    weight = project(np.asarray(w1)-w0, (np.asarray(m1)+m0)/2)
    mapping = project((np.asarray(w1)+w0)/2, np.asarray(m1)-m0)
    return weight, mapping


def error_envelope(weights, old_map, new_map):
    """Triangle-inequality upper bound on TV of aggregate nationality shares."""
    row_tv = np.abs(np.asarray(new_map)-old_map).sum(axis=1)/2
    return float(np.sum(np.asarray(weights)*row_tv))


def refresh(old_map, new_map, rows):
    result = np.array(old_map, copy=True)
    result[list(rows)] = np.asarray(new_map)[list(rows)]
    return result


def exposure_interval(weights, old_map, target_indices, radii):
    """Sharp target-share interval under independent row total-variation balls.

    Radii are user-supplied assumptions, not statistically calibrated guarantees.
    The target and its complement must both be nonempty.
    """
    matrix=validate_map(old_map)
    weights=np.asarray(weights,dtype=float);radii=np.asarray(radii,dtype=float)
    target=list(target_indices)
    if len(target)==0 or len(set(target))!=len(target) or len(target)>=matrix.shape[1]:
        raise ValueError('Target must be a proper, nonempty set of columns')
    if weights.shape!=(matrix.shape[0],) or radii.shape!=weights.shape:
        raise ValueError('Incompatible dimensions')
    if not np.isfinite(weights).all() or not np.isfinite(radii).all() or (weights<0).any() or abs(weights.sum()-1)>1e-8 or (radii<0).any() or (radii>1).any():
        raise ValueError('Weights must sum to one and radii must lie in [0,1]')
    p=matrix[:,target].sum(axis=1)
    lower=np.maximum(0,p-radii);upper=np.minimum(1,p+radii)
    return float(np.sum(weights*lower)),float(np.sum(weights*upper)),weights*(upper-lower)
