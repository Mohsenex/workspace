import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.pdk import get_active_pdk
from gdsfactory.add_pins import add_instance_label


@gf.cell
def Main_AMF_Die4() -> Component:
    pdk = get_active_pdk()
    c = Component()

    # Create instances
    instance1 = c.add_ref(pdk.get_component('die_frame_full', size=(7000, 3500)), name='instance1'

    # Add instance labels
    add_instance_label(c, instance1, instance_name='instance1')

    return c