#$language = "Python"
#$interface = "1.0"

import os

#################################################################
####                  VARIABLES SECTION                      ####
#################################################################

# Enter variables bellow which will be used by the script.
# ALL values must be between the " "

# Hostname should match the As-Built on the switches tab
# Timezone will be where the property location is located E.I Pacific, Mountain, Central, Eastern

hostname = "value"
prop_code = "value"
timezone = "value"
admin_pw = "aerwavetemp!"
aernoc_pw = "aerwavetemp!"
aertech_pw = "aerwavetemp!"
aertikauvik_pw = "aerwavetemp!"
aertik_auvik_snmpv3 = "aerwavetemp!"
# eth13 is the management port and should not change from 192.168.15.5/24
# upgrade_start variable must be in the format "YYY-MM-DD"
upgrade_start = "YYYY-MM-DD"
dns_prim = "1.1.1.1"
dns_second = "8.8.8.8"
wan_gw_add = "value"
wan_add_w_mask = "value/x"
wan_sub_no_mask = "value"
wan_vlan = "value"
vlan_15_ip_w_mask = "value/x"
vlan_15_sub_no_mask = "value"
vlan_16_ip_w_mask = "value/x"
vlan_16_ip_no_mask = "value"
vlan_16_sub_w_mask = "value/x"
vlan_16_sub_no_mask = "value"
vlan_17_ip_w_mask = "value/x"
# APs will get ip addressing via dhcp from the above controller the range always excludes 
# the first and last 5 addresses of the pool I.E. 100.97.24.5-100.97.27.250
ap_dhcp_range = "value-value"
# Vanity vlans usually start at 1000 unless a router is being configured for a legacy site
vanity_vlan_start = "1000"
vanity_vlan_end = "value"
# DHCP option code will eith be 43 or 138 depending on hardware vendor.
# DHCP option name usually take s the form PROPERYCODE_VSZ I.E. TORR_VSZ
# DHCP option value is a hex representation of the controller's IP address preceded by "0x"
dhcp_opt_code = "value"
dhcp_opt_name = "value"
dhcp_opt_value = "value"
# Enter the SNMP server to send logs to
location = "City, ST"
router_ip = "100.x.x.x" # Router vlan 15 IP
snmp_server = "172.x.x.x" # Regional Auvik Collector

#Enter interfaces to monitor for net-flow and SNMP:
#List is comma seperated.
#For OOB: WAN-sfp1, sfp-plus3, LAN-sfp4
#For DC WAN: ISP-WAN-sfp28-1, sfp28-7, sfp28-11, sfp28-12, PO1
#For MDU: WAN-sfp1, LAN-sfp4
interfaces = ["WAN-sfp1,","LAN-sfp4,","ISP-sfp1"]

##################################################################################
#########################       SCRIPT BEGINS HERE       #########################
##################################################################################

def main():
# Update basic system info such as hostname, users, timezone, and neighbor discovery among others.
    crt.Screen.Synchronous = True
    crt.Screen.Send(
        # Config Hostname
        "/system identity \r"
        "set name=" + hostname + "\r"
    )
    crt.Sleep(500)

    crt.Screen.Send(
        # Config Users and PWs, more can be added in later iterations of the script.
        "/user \r"
        """set number=0 comment="system default user" group=full name=admin password=""" + admin_pw + "\r"
        """add comment="NOC Engineers" group=full name=aernoc password=""" + aernoc_pw + "\r"
        """add comment="Field Engineers" group=full name=aertech password=""" + aertech_pw + "\r"
        """add comment="Auvik Monitoring" group=full name=aertik-auvik password=""" + aertikauvik_pw + "\r"
    )
    crt.Sleep(500)

    crt.Screen.Send(
        # Config timezone
        "/system clock \r"
        "set time-zone-name=US/" + timezone + "\r"
        # Config DNS
        "/ip dns \r" 
        "set allow-remote-requests=no \r" 
        "set servers=" + dns_prim + "," + dns_second + "\r"
        "/system ntp client set enabled=yes servers=time.nist.gov,0.north-america.pool.ntp.org,1.north-america.pool.ntp.org \r"
    )
    crt.Sleep(500)

    crt.Screen.Send(
        # Config Neighbor Discovery
        "/ip neighbor discovery-settings \r"
        "set protocol=cdp,lldp \r"
        # Config Interfaces
        "/interface ethernet \r"
        "set [ find default-name=ether13 ] name=MGMT-e13 \r"
        "set [ find default-name=sfp-sfpplus4 ] advertise=1000M-full,10000M-full name=LAN-sfp4 speed=1Gbps \r"
        "set [ find default-name=sfp-sfpplus1 ] advertise=1000M-full,10000M-full name=WAN-sfp1 speed=1Gbps \r"
        "/interface ethernet switch \r"
        "set 0 l3-hw-offloading=yes \r"
    )
    crt.Sleep(500)
# Update IP addresses, Routes, and VLAN interfaces
    crt.Screen.Send(
        # Config default route
        "/ip route \r"
        "add disabled=no distance=1 dst-address=0.0.0.0/0 gateway=" + wan_gw_add + " routing-table=main suppress-hw-offload=no \r"
        "add disabled=no distance=5 dst-address=0.0.0.0/0 gateway=192.168.15.1 routing-table=main suppress-hw-offload=no \r"
        "/interface vlan \r"
        "add interface=WAN-sfp1 name=ISP-SFP1 vlan-id=" + wan_vlan + """ comment="WAN" \r"""
        """add interface=LAN-sfp4 name=VLAN15 vlan-id=15 comment="NET MGMT" \r"""
        """add interface=LAN-sfp4 name=VLAN16 vlan-id=16 comment="AP MGMT" \r"""
        "add interface=LAN-sfp4 name=VLAN400 vlan-id=400 comment=" + """ " """ + prop_code + """ BoH" \r"""
        """add interface=LAN-sfp4 name=VLAN100 vlan-id=100 comment="AERWAVE WLAN" \r"""
        # This is a script to create interfaces
        ":for e from=" + vanity_vlan_start + " to=" + vanity_vlan_end + """ do={ add interface=LAN-sfp4 name=("VLAN" . $e) vlan-id=$e comment="UNIT WLAN"} \r"""
    )
    crt.Sleep(500)

    crt.Screen.Send(
        # Config IP ranges for vlans 15, 16, 100, 400, and the management port.
        "/ip address \r"
        "add address=" + wan_add_w_mask + """ interface=ISP-SFP1 comment="WAN IP" \r"""
        """add address=192.168.15.5/24 comment="MGMT INT" interface=MGMT-e13 \r"""
        "add address=" + vlan_15_ip_w_mask + " interface=VLAN15 network=" + vlan_15_sub_no_mask + """ comment="NET MGMT" \r"""
        "add address=" + vlan_16_ip_w_mask + " interface=VLAN16 network=" + vlan_16_sub_no_mask + """ comment="AP MGMT" \r"""
        """add address=10.40.0.1/24 interface=VLAN400 network=10.40.0.0 comment="CLIENT BoH" \r"""
        """add address=10.100.0.1/16 interface=VLAN100 network=10.100.0.0 comment="AERWAVE WLAN" \r"""
        # Addresses for UNIT VLANs
        # This is a script to create all the needed interfaces.
        ":global base 10.128.0.0 \r"
        ":for vlan from=" + vanity_vlan_start + " to=" + vanity_vlan_end + " do={ \r"
        ":local id ($vlan - 1000); \r"
        ":local ip ($base + ($id * 256) + 1) \r"
        """add address=("$ip/24") interface=("VLAN$vlan") network=("$ip") comment="UNIT ADDRESSES" \r"""
        "} \r"
    )
    crt.Sleep(500)
    # Config DHCP Option, DHCP Pools, DHCP Servers, and DHCP Server Networks
    crt.Screen.Send(
        # DHCP Option configs
        "/ip dhcp-server option \r"
        "add code=" + dhcp_opt_code + " name=" + dhcp_opt_name + " value=" + dhcp_opt_value + "\r"
        "/ip dhcp-server option sets \r"
        "add name=" + dhcp_opt_name + " options=" + dhcp_opt_name+ "\r"
    )
    crt.Sleep(500)

    crt.Screen.Send(
        # Config DHCP Server Pools
        "/ip pool \r"
        "add name=AP_MGMT ranges=" + ap_dhcp_range + "\r"
        "add name=AERWAVE_WLAN ranges=10.100.0.5-10.100.255.250 \r"
        "add name=" + prop_code + "_BoH ranges=10.40.0.5-10.40.0.250 \r"
        # DHCP for in unit end user devices.
        ":global base 10.128.0.0 \r"
        ":for vlan from=" + vanity_vlan_start + " to=" + vanity_vlan_end + " do={ \r"  
        ":local id ($vlan - 1000); \r"
        ":local ip ($base + ($id * 256) + 5) \r"
        ":local ip1 ($ip + 245) \r"
        """add name=("VLAN$vlan") ranges=("$ip-$ip1") \r"""
        "} \r"
    )
    crt.Sleep(500)

    crt.Screen.Send(
        # Config DHCP UNIT SERVERs
        "/ip dhcp-server \r"
        "add add-arp=yes address-pool=AP_MGMT dhcp-option-set=" + dhcp_opt_name + """ interface=VLAN16 lease-time=1d name=AP_MGMT comment="AP MGMT" \r"""
        """add add-arp=yes address-pool=AERWAVE_WLAN interface=VLAN100 lease-time=1d name=AERWAVE_WLAN comment="AERWAVE WLAN" \r"""
        "add add-arp=yes address-pool=" + prop_code + "_BoH interface=VLAN400 lease-time=1d name=" + prop_code + """_BoH comment=" """ + prop_code + """ BoH" \r"""
        # Config DHCP servers for Units.
        ":for e from=" + vanity_vlan_start + " to=" + vanity_vlan_end + """ do={ add add-arp=yes address-pool=("VLAN" . $e) disabled=no interface=("VLAN" . $e) name=("VLAN" . $e) lease-time=1d comment="UNIT DHCP"} \r"""
    )
    crt.Sleep(500)

    crt.Screen.Send(
        # Config DHCP Servers Networks
        "/ip dhcp-server network \r"
        "add address=" + vlan_16_ip_w_mask + " dns-server=" + dns_prim + "," + dns_second + " gateway=" + vlan_16_ip_no_mask + """ comment="AP MGMT" \r"""
        "add address=10.40.0.1/24 dns-server=" + dns_prim + "," + dns_prim + """ gateway=10.40.0.1 comment="CLIENT BoH" \r"""
        "add address=10.100.0.1/16 dns-server=" + dns_prim + "," + dns_second + """ gateway=10.100.0.1 comment="AERWAVE WLAN" \r"""
        # Config DHCP for UNIT VLANs
        # This is a script to create all the UNIT DHCP scopes.
        ":global base 10.128.0.0 \r"
        ":for vlan from=" + vanity_vlan_start + " to=" + vanity_vlan_end + " do={ \r" 
        ":local id ($vlan - 1000); \r"
        ":local ip ($base + ($id * 256)) \r"
        ":local ip1 ($base + ($id * 256) +1) \r"
        """add address=("$ip/24") dns-server=""" + dns_prim + "," + dns_second + """ gateway=("$ip1") comment="VLAN $vlan" \r"""
        "} \r"
    )
    crt.Sleep(500)
    # Config Firewall rules and disable unneeded services
    crt.Screen.Send(
        # Disable unnecessary services
        "/ip service \r"
        "set telnet disabled=yes \r"
        "set www disabled=yes \r"
        "/ip firewall service-port \r"
        "set ftp disabled=yes \r"
        "set h323 disabled=yes \r"
        # Config Firewall/NAT Rules
        "/ip firewall nat \r"
        "add action=masquerade chain=srcnat out-interface=ISP-SFP1 src-address=10.128.0.0/12 \r"
        "add action=masquerade chain=srcnat out-interface=ISP-SFP1 src-address=" + vlan_16_sub_w_mask + "\r"
        "/ip firewall filter \r"
        "add action=drop chain=forward dst-address=10.128.0.0/12 src-address=10.128.0.0/12 \r"
        "/ \r"
    )
    crt.Sleep(200)
    # Clean up default configs
    crt.Screen.Send(
        "/ip/address \r"
        "remove number=0 \r"
        "/\r\r"
        "/disk \r"
        "format-drive nvme1 filesystem=fat32 mbr-partition-table=no \r"
        "/system script\r"
        """add dont-require-permissions=no name="Upgrade Routerboard" owner=admin policy=ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source="/system routerboard upgrade"\r"""
        "/\r"
        "/system scheduler\r"
        """add interval=2w name="Package Upgrade" on-event="# Check Packages\r"""
        "\nsystem package update check-for-updates\r"
        "\n:global FWstatus [/system package update get status];\r"
        "\n \r"
        """\nif (\$FWstatus = \"New version is available\") do={system package update download; delay delay-time=300; system reboot} else={}" policy=ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon start-date=""" + upgrade_start + " start-time=02:00:00\r"""
        """add interval=2w name="RouterBOARD Upgrade" on-event="# Check bios firmware\r"""
        "\n \r"
        "\n:if ( [/system routerboard get current-firmware] != [/system routerboard get upgrade-firmware] ) do={\r"
        """\n:log error \"Bios firmware different! Need upgrade\"\r"""
        """\n/system script run \"Upgrade Routerboard\"\r"""
        "\n:delay 10\r"
        "\n/system reboot\r"
        "\n}\r"
        """\n" policy=ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon start-date=""" + upgrade_start + """ start-time=02:20:00\r"""
        "/\r"
    ) 
    crt.Sleep(200)

    # Configure Auvik Monitoring
    crt.Screen.Send(
        "\r"
        "/snmp community\r"
        "set [ find default=yes ] disabled=yes\r"
        "add addresses=::/0 authentication-protocol=SHA1 encryption-protocol=AES name=aertik-auvik-snmp security=authorized write-access=yes authentication-password=" + aertik_auvik_snmpv3 + " encryption-password="+ aertik_auvik_snmpv3 + "\r"
    )
    crt.Sleep(200)
    crt.Screen.Send(
        "/snmp\r"
        """set contact=aernoc@aerwave.com enabled=yes location=\" """ + location + """\" src-address=""" + router_ip + """ trap-community=aertik-auvik-snmp trap-generators=interfaces,start-trap trap-target=""" + snmp_server + """ trap-version=3\r"""
    )
    for interface in interfaces:
        crt.Screen.send(
            "set trap-interfaces=" + interface + "\r"
        )
        crt.Sleep(50)
    crt.Screen.send(
        "/system logging action\r"
        "set 3 remote=" + snmp_server +  " src-address=" + router_ip + "\r"
        "/system logging\r"
        "set 0 action=remote\r"
        "set 1 action=remote\r"
        "set 2 action=remote\r"
        "set 3 action=remote\r"
        "/ip traffic-flow\r"
        "set enabled=yes\r"
    )
    crt.Sleep(200)
    for interface in interfaces:
        crt.Screen.Send(
            "interfaces=" + interface + "\r"
        )
        crt.Sleep(50)
    crt.Screen.Send(
        "/ip traffic-flow target\r"
        "add dst-address=" + snmp_server + " src-address=" + router_ip + " version=5\r"
        "/\r"
    )
    crt.Sleep(200)
    

main()