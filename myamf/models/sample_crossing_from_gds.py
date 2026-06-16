import jax.numpy as jnp
import sax


def sample_crossing_from_gds() -> sax.SDict:
    sdict = {
        ("in0", "out0"): jnp.array(3.0),
    }
    return sax.reciprocal(sdict)
