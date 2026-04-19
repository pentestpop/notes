
**VLANs** (**V**irtual **LAN**) are used to segment portions of a network at layer two and differentiate devices. 
VLANs are configured on a switch by adding a "tag" to a frame. The **802.1q** or **dot1q** tag will designate the VLAN that the traffic originated from.
The **Native VLAN** is used for any traffic that is not tagged and passes through a switch. To configure a native VLAN, we must determine what interface and tag to assign them, then set the interface as the default native VLAN. Below is an example of adding a native VLAN in Open vSwitch.