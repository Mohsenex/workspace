import numpy as np
import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec
import amf.chp as pdk
from amf.chp.tech import LAYER, TECH


def _radius_from_fsr(
    fsr_nm: float = 100.0,
    wavelength_um: float = 1.55,
    ng: float = 2.0,
) -> float:
    """Return ring radius (µm) for a target FSR (nm)."""
    fsr_um = fsr_nm * 1e-3
    circumference = wavelength_um**2 / (ng * fsr_um)
    return circumference / (2 * np.pi)


def _add_deep_trench(
    c: gf.Component,
    ring: gf.ComponentReference,
    trench_gap: float = 5.0,
    trench_width: float = 4.0,
) -> None:
    """Add a deep-trench frame (DTR layer) around the ring bounding box."""
    bbox = ring.dbbox()  # returns pya.DBox with .left/.bottom/.right/.top

    x0 = bbox.left - trench_gap
    y0 = bbox.bottom - trench_gap
    x1 = bbox.right + trench_gap
    y1 = bbox.top + trench_gap

    ox0, oy0 = x0 - trench_width, y0 - trench_width
    ox1, oy1 = x1 + trench_width, y1 + trench_width

    # bottom bar
    c.add_polygon([[ox0, oy0], [ox1, oy0], [ox1, y0], [ox0, y0]], layer=LAYER.DTR)
    # top bar
    c.add_polygon([[ox0, y1], [ox1, y1], [ox1, oy1], [ox0, oy1]], layer=LAYER.DTR)
    # left bar
    c.add_polygon([[ox0, y0], [x0, y0], [x0, y1], [ox0, y1]], layer=LAYER.DTR)
    # right bar
    c.add_polygon([[x1, y0], [ox1, y0], [ox1, y1], [x1, y1]], layer=LAYER.DTR)


@gf.cell
def ring_sin_deeptrench(
    fsr_nm: float = 100.0,
    wavelength_um: float = 1.55,
    ng: float = 2.0,
    gap: float = 0.4,
    length_x: float = 4.0,
    length_y: float = 4.6,
    trench_gap: float = 5.0,
    trench_width: float = 4.0,
    cross_section: CrossSectionSpec = "nitride",
) -> gf.Component:
    """Single SiN ring resonator with deep-trench (DTR) isolation.

    The ring radius is derived from the target FSR:
        R = λ² / (ng · FSR · 2π)

    Note: AMF CHP enforces a minimum SiN bend radius of 25 µm.
    A 100 nm FSR at 1550 nm requires R ≈ 1.9 µm, which is below
    the PDK limit — the radius is clamped to TECH.radius_nitride (25 µm).

    Args:
        fsr_nm: target free spectral range in nm.
        wavelength_um: centre wavelength in µm.
        ng: SiN group index used for FSR calculation.
        gap: coupler gap in µm (PDK default 0.4 µm).
        length_x: coupler straight length in µm.
        length_y: ring vertical straight length in µm.
        trench_gap: clearance from ring bbox to inner trench edge in µm.
        trench_width: width of the DTR draw in µm.
        cross_section: waveguide cross-section (default "nitride").
    """
    c = gf.Component()

    radius = _radius_from_fsr(fsr_nm, wavelength_um, ng)
    radius = max(radius, TECH.radius_nitride)  # clamp to PDK minimum (25 µm)

    ring = c << gf.get_component(
        "ring_single",
        gap=gap,
        radius=radius,
        length_x=length_x,
        length_y=length_y,
        cross_section=cross_section,
    )

    _add_deep_trench(c, ring, trench_gap=trench_gap, trench_width=trench_width)

    c.add_port("o1", port=ring.ports["o1"])
    c.add_port("o2", port=ring.ports["o2"])

    return c


if __name__ == "__main__":
    pdk.activate()
    c = ring_sin_deeptrench()
    c.show()
