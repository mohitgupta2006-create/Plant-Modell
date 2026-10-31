"""Cause-first condition gating for NEW reviewer checkpoints; legacy decoding is unchanged."""
import numpy as np
from research_inputs import DEFICIENCIES

def gated_logits(logits, maps):
    meta, cs = maps['condition_meta'], maps['condition']
    x = np.asarray(logits['condition'], dtype=float).copy()
    for i in range(len(x)):
        healthy = maps['health'][int(np.argmax(logits['health'][i]))] == 'Healthy'
        crop = maps['crop'][int(np.argmax(logits['crop'][i]))]
        cause = maps['cause'][int(np.argmax(logits['cause'][i]))]
        both = set(maps.get('cause_trained_classes', [])) == {'Biotic', 'Abiotic'}
        allowed = [bool(meta[c][1]) == healthy and meta[c][0] == crop and
                   (healthy or not both or ('Abiotic' if c in DEFICIENCIES else 'Biotic') == cause)
                   for c in cs]
        # Unrepresented branch: fail closed rather than silently cross causes/crops.
        if not any(allowed):
            raise ValueError('unsupported diagnostic branch: no validated condition for predicted crop/health/cause')
        x[i, np.logical_not(allowed)] = -np.inf
    return x
