import gdsfactory as gf


@gf.cell(check_instances=False)
def EC_SiN(
    ec_length: float = 150,
    ec_tip: float = 0.3,
    ec_end_width: float = 1,
    ec_constant_length: float = 50,
    ec_angle: float = 15,
    bend_radius: float = 50,
) -> gf.Component:
    c = gf.Component()

    ec_straight = c.add_ref(
        gf.components.taper(
            length=ec_constant_length,
            width1=ec_tip,
            width2=ec_tip,
            cross_section="nitride",
        )
    )
    # Rotate the constant section by -ec_angle so it points at angle -ec_angle from east
    ec_straight.rotate(-ec_angle)

    ec_taper = c.add_ref(
        gf.components.taper(
            length=ec_length,
            width1=ec_tip,
            width2=ec_end_width,
            cross_section="nitride",
        )
    )
    ec_taper.connect("o1", ec_straight.ports["o2"])

    # bend_euler_all_angle handles arbitrary angles cleanly.
    # Sweeping +ec_angle rotates the exit orientation back to 0° (east).
    ec_bend = c.add_ref_off_grid(
        gf.components.bend_euler_all_angle(
            radius=bend_radius,
            angle=ec_angle,
            cross_section="nitride",
            with_arc_floorplan=True,
        )
    )
    ec_bend.connect("o1", ec_taper.ports["o2"])

    c.add_port("o1", port=ec_straight.ports["o1"])
    c.add_port("o2", port=ec_bend.ports["o2"])
    return c
