# import gdsfactory as gf
# from gdsfactory.path import spiral_archimedean
# from gdsfactory.typings import ComponentSpec, CrossSectionSpec
# from amf.chp.tech import LAYER

# # use amf PDK instead of the generic gpdk
# gf.gpdk.PDK.activate()

# @gf.cell
# def spiral_double2(
#     min_bend_radius: float = 10.0,
#     separation: float = 2.0,
#     number_of_loops: float = 3,
#     npoints: int = 1000,
#     cross_section: CrossSectionSpec = "strip",
#     bend: ComponentSpec = "bend_circular",
#     sbend: ComponentSpec = "bend_circular",
# ) -> gf.Component:
#     """Returns a spiral double (spiral in, and then out).

#     Args:
#         min_bend_radius: inner radius of the spiral.
#         separation: separation between the loops.
#         number_of_loops: number of loops per spiral.
#         npoints: points for the spiral.
#         cross_section: cross-section to extrude the structure with.
#         bend: factory for the bends in the middle of the double spiral.
#     """
#     component = gf.Component()

#     sbend = gf.get_component(
#         sbend, radius=min_bend_radius / 2, cross_section=cross_section
#     )
     

#     bend = gf.get_component(
#         bend, radius=min_bend_radius / 2, angle=90, cross_section=cross_section
#     )

#     bend1 = component.add_ref(bend)
#     bend2 = component.add_ref(bend)
#     bend2.mirror()
#     bend1.rotate(90)
#     sbend_ = component.add_ref(sbend) 
#     sbend_.move(origin=sbend_.center, destination=(0, 0))
#     # sbend_.mirror()

#     bend1.connect("o2", sbend_.ports["o2"])
#     bend2.connect("o1", sbend_.ports["o1"])
    
#     component.rotate(90, center=(0, 0))
#     component.mirror()
#     component.move(origin=sbend_.center, destination=(0, 0))

 
#     path = spiral_archimedean(
#         min_bend_radius=min_bend_radius,
#         separation=separation,
#         number_of_loops=number_of_loops,
#         npoints=npoints,
#     )
#     path.start_angle = 0
#     path.end_angle = 0

#     spiral = path.extrude(cross_section=cross_section)
#     spiral1 = component.add_ref(spiral)
#     spiral2 = component.add_ref(spiral)
#     spiral2.mirror()

#     spiral1.connect("o1", bend1.ports["o1"], mirror=True)
#     spiral2.connect("o1", bend2.ports["o2"])

#     component.add_port("o1", port=spiral1.ports["o2"])
#     component.add_port("o2", port=spiral2.ports["o2"])
#     component.info["length"] = float(path.length() + bend.info["length"] + sbend.info["length"]/2) * 2 
#     component.flatten()
#     return component


# l: float = 550 # distance between splitter and combiner
# gap: float = 0.35
# coupling_length: float = 16.8 
# coupling_radius: float = 50
# wg_width: float = 3
# taper_length: float = 30
# separation: float = 6.5
# min_bend_radius: float = 270 *2
# htr_length: float = 100
# htr_radius = 450
# number_of_loops: float = 27
# npoints: float = 20000
# xs_sin = gf.cross_section.strip(width=3, layer=LAYER.WG_SIN)

# print("min_bend_radius =", min_bend_radius, type(min_bend_radius))

# c = gf.Component()
# bend=dict(component='bend_euler', settings=dict(p=0))
# sbend=dict(component='bend_euler_s', settings=dict(p=0.9))

# spiral = c.add_ref(spiral_double2(min_bend_radius=min_bend_radius, separation=separation, number_of_loops=number_of_loops, npoints=npoints, cross_section=xs_sin, bend=bend, sbend=sbend))
# # c.write_gds("/workspace/myamf/gds/Delay_WL.gds")
# c.show()
