"""Write GDS with sample errors."""

import gdsfactory as gf
import numpy as np
from amf.chp.tech import LAYER
from gdsfactory.component import Component
from gdsfactory.typings import Float2, Layer

layer = LAYER.WG
layer1_separation = LAYER.WG
layer2_separation = LAYER.WG_SIN
layer1_enclosing = LAYER.VIA2
layer2_enclosing = LAYER.MT2


@gf.cell
def _width_min(size: Float2 = (0.1, 0.1)) -> Component:
    """Width minimum error."""
    return gf.components.rectangle(size=size, layer=layer)


@gf.cell
def _area_min() -> Component:
    """Area minimum error."""
    size = (0.2, 0.2)
    return gf.components.rectangle(size=size, layer=layer)


@gf.cell
def _gap_min(gap: float = 0.1) -> Component:
    """Gap minimum error."""
    c = gf.Component()
    r1 = c << gf.components.rectangle(size=(1, 1), layer=layer)
    r2 = c << gf.components.rectangle(size=(1, 1), layer=layer)
    r1.dxmax = 0
    r2.dxmin = gap
    return c


@gf.cell
def _separation(
    gap: float = 0.1,
    layer1: Layer = layer1_separation,
    layer2: Layer = layer2_separation,
) -> Component:
    """Separation error."""
    c = gf.Component()
    r1 = c << gf.components.rectangle(size=(1, 1), layer=layer1)
    r2 = c << gf.components.rectangle(size=(1, 1), layer=layer2)
    r1.dxmax = 0
    r2.dxmin = gap
    return c


@gf.cell
def _enclosing(
    enclosing: float = 0.1,
    layer1: Layer = layer1_enclosing,
    layer2: Layer = layer2_enclosing,
) -> Component:
    """Layer1 must be enclosed by layer2 by value.

    checks if layer1 encloses (is bigger than) layer2 by value
    """
    w1 = 1
    w2 = w1 + enclosing
    c = gf.Component()
    _ = c << gf.components.rectangle(size=(w1, w1), layer=layer1, centered=True)
    r2 = c << gf.components.rectangle(size=(w2, w2), layer=layer2, centered=True)
    r2.movex(0.5)
    return c


@gf.cell
def sample_drc_errors() -> Component:
    """Combine sample errors."""
    components = [_width_min(), _gap_min(), _separation(), _enclosing()]
    components += [_gap_min(spacing) for spacing in np.linspace(0.1, 0.2, 5)]
    c = gf.pack(components, spacing=3.5)

    c = gf.add_padding_container(c[0], layers=(LAYER.FLOORPLAN,), default=5)
    return c
