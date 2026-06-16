import gdsfactory as gf
from amf.chp.cells.fixed import (
    AMF_300LSOI_Si1X2MMI_Cband_v5p0,
    AMF_300LSOI_Si2X2MMI_Cband_v5p0,
)


@gf.cell  # pyright: ignore[reportArgumentType]
def strip_MZI(
    gap: float = 100,
    dl: float = 62.017,
    cross_section: str = "strip",
) -> gf.Component:
    """MZI with two rectangular arms using explicit gf.Path quarter arcs.

    Upper arm (reference, +Y):
        → 15 µm east
        ↑ arc +90° (turn north)
        ↑ 20 µm north
        → arc -90° (turn east)
        → middle horizontal straight
        ↓ arc -90° (turn south)
        ↓ 20 µm south
        → arc +90° (turn east)
        → remaining straight to combiner o1

    Lower arm (longer by dl, -Y): same shape mirrored downward,
    with extra length added to the vertical legs to achieve dl.
    """
    c = gf.Component()
    xs = gf.get_cross_section(cross_section)
    R = xs.radius

    # ------------------------------------------------------------------ #
    # MMI placement                                                        #
    # ------------------------------------------------------------------ #
    splitter = c.add_ref(AMF_300LSOI_Si1X2MMI_Cband_v5p0())
    combiner = c.add_ref(AMF_300LSOI_Si2X2MMI_Cband_v5p0())

    # Place combiner gap µm east of splitter (port face to port face)
    combiner.movex(
        splitter.ports["o2"].center[0] + gap - combiner.ports["o1"].center[0]
    )
    # Align combiner so o1 is at the same Y as splitter o2
    # combiner.movey(
    #     splitter.ports["o2"].center[1] - combiner.ports["o1"].center[1]
    # )

    # ------------------------------------------------------------------ #
    # Port positions after placement                                       #
    # ------------------------------------------------------------------ #
    x0 = float(splitter.ports["o2"].center[0])   # splitter output face X
    x1 = float(combiner.ports["o1"].center[0])   # combiner input face X

    y_s2 = float(splitter.ports["o2"].center[1])  # upper arm start Y
    y_s3 = float(splitter.ports["o3"].center[1])  # lower arm start Y
    y_c1 = float(combiner.ports["o1"].center[1])  # upper arm end Y
    y_c2 = float(combiner.ports["o2"].center[1])  # lower arm end Y

    # Fixed stub and vertical leg lengths (as described)
    stub  = 15.0   # east stub before/after the vertical section
    vert  = 0.0   # vertical straight length for the reference (upper) arm

    # The 4 arcs take up 4*R of horizontal space; the rest is the middle straight
    middle = (x1 - x0) - 2 * stub - 4 * R

    # Extra vertical length needed on the lower arm to achieve dl
    # Lower arm natural vert length = vert (same shape mirrored)
    extra = dl / 2   # split equally between the two vertical legs

    # ------------------------------------------------------------------ #
    # Upper arm  (reference, extends +Y)                                  #
    # East → arc+90 → North → arc-90 → East → arc-90 → South → arc+90   #
    # The path starts heading East at (x0, y_s2)                         #
    # ------------------------------------------------------------------ #
    p_upper = gf.Path()
    p_upper += gf.path.straight(length=stub)          # → 15 µm east
    p_upper += gf.path.arc(radius=R, angle=90)        # ↑ turn north
    p_upper += gf.path.straight(length=vert)          # ↑ 20 µm north
    p_upper += gf.path.arc(radius=R, angle=-90)       # → turn east
    p_upper += gf.path.straight(length=middle)        # → middle horizontal
    p_upper += gf.path.arc(radius=R, angle=-90)       # ↓ turn south
    p_upper += gf.path.straight(length=vert + 0.233)          # ↓ 20 µm south
    p_upper += gf.path.arc(radius=R, angle=90)        # → turn east
    p_upper += gf.path.straight(length=stub)          # → 15 µm east to combiner

    upper_wg = p_upper.extrude(xs)
    upper_ref = c.add_ref(upper_wg)
    upper_ref.move((x0, y_s2))

    # ------------------------------------------------------------------ #
    # Lower arm  (longer by dl, extends -Y)                               #
    # East → arc-90 → South → arc+90 → East → arc+90 → North → arc-90   #
    # ------------------------------------------------------------------ #
    p_lower = gf.Path()
    p_lower += gf.path.straight(length=stub)          # → 15 µm east
    p_lower += gf.path.arc(radius=R, angle=-90)       # ↓ turn south
    p_lower += gf.path.straight(length=vert + extra )  # ↓ south (longer)
    p_lower += gf.path.arc(radius=R, angle=90)        # → turn east
    p_lower += gf.path.straight(length=middle)        # → middle horizontal
    p_lower += gf.path.arc(radius=R, angle=90)        # ↑ turn north
    p_lower += gf.path.straight(length=vert + extra + 0.233)  # ↑ north (longer)
    p_lower += gf.path.arc(radius=R, angle=-90)       # → turn east
    p_lower += gf.path.straight(length=stub)          # → 15 µm east to combiner

    lower_wg = p_lower.extrude(xs)
    lower_ref = c.add_ref(lower_wg)
    lower_ref.move((x0, y_s3))

    upper_length = stub + vert + middle + vert + stub + 4 * (3.14159 / 2 * R)
    lower_length = stub + (vert + extra) + middle + (vert + extra) + stub + 4 * (3.14159 / 2 * R)
    print(
        f"[strip_MZI] upper: {upper_length:.3f} µm | "
        f"lower: {lower_length:.3f} µm | "
        f"ΔL: {lower_length - upper_length:.3f} µm (target {dl:.3f} µm)"
    )

    #----- Ports----------------------
    term = c.add_ref(gf.components.terminator(doping_layers=[]))
    term.connect('o1', combiner.ports['o3'])

    c.add_port('o1', port = splitter.ports['o1'])
    c.add_port('o2', port = combiner.ports['o4'])
    return c
