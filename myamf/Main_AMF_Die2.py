import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.pdk import get_active_pdk
from gdsfactory.add_pins import add_instance_label


@gf.cell
def Main_AMF_Die2([7000, 3500]) -> Component:
    pdk = get_active_pdk()
    c = Component()

    # Create instances
    instance1 = c.add_ref(pdk.get_component('die_frame_full'), name='instance1')

    # Place instances and make connections
    instance1.move((0.0 + -86.062, 0.0 + 50.925))

    # Add instance labels
    add_instance_label(c, instance1, instance_name='instance1')

    return c