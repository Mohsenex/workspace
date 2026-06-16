"""Sample PIC."""

import gdsfactory as gf
from amf.chp import LAYER, cells


@gf.cell
def die_with_edge_couplers(
    size: tuple[float, float] = (7000, 3500),
    pitch: float = 127,
    nfibers: int = 20,
) -> gf.Component:
    """Returns die with east west edge couplers.

    Args:
        size: of the die in um.
        pitch: of the edge couplers in um.
        nfibers: number of fibers. If None, it is computed from size and pitch.
    """
    c = gf.Component()
    fp = c << gf.c.rectangle(size=size, layer=LAYER.FLOORPLAN)
    fp.xmin = 0
    fp.ymin = 0

    nfibers = nfibers or int(size[1] / pitch)
    ecs = cells.edge_coupler_array(
        edge_coupler=cells.edge_coupler_nitride(angle=8),
        n=nfibers,
        pitch=pitch,
    )

    _ = west = c << ecs
    west.dmirror()
    west.xmin = fp.xmin
    west.ymin = fp.ymin + 60
    east = c << ecs
    east.xmax = fp.xmax
    east.ymin = fp.ymin + 60
    for i, port in enumerate(
        gf.port.get_ports_list(
            west.ports, clockwise=False, sort_ports=True, orientation=0
        )
    ):
        c.add_port(name=f"w{i + 1}", port=port)
    for i, port in enumerate(
        gf.port.get_ports_list(
            east.ports, clockwise=True, sort_ports=True, orientation=180
        )
    ):
        c.add_port(name=f"e{i + 1}", port=port)
    return c
