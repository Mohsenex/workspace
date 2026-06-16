"""Pack."""

import gdsfactory as gf
from amf.chp import cells


@gf.cell
def sample3_grid():
    t1 = cells.text_rectangular("1")
    t2 = cells.text_rectangular("2")
    t3 = cells.text_rectangular("3")
    t4 = cells.text_rectangular("4")
    t5 = cells.text_rectangular("5")
    t6 = cells.text_rectangular("6")

    return gf.grid([t1, t2, t3, t4, t5, t6], shape=(2, 3), spacing=(10, 10))
