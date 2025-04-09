import os

#################################################################
####                  VARIABLES SECTION                      ####
#################################################################

# Enter variables bellow which will be used by the script.
# ALL values must be between the " "
# Hostname should match the As-Built on the switches tab
# Timezone will be where the property location is located E.I Pacific, Mountain, Central, Eastern
hostname = ""
prop_code = ""
timezone = ""
admin_pw = ""
*****_pw = ""
******_pw = ""
*******_pw = ""
********_snmpv3 = ""
dns_prim = ""
dns_second = ""
wan_gw_add = ""
wan_add_w_mask = ""
wan_vlan = ""
failover_gw_ip = ""
failover_ip_w_mask = ""
vlan_15_ip_w_mask = ""
vlan_15_sub_w_mask = ""
vlan_16_ip_w_mask = ""
vlan_16_ip_no_mask = ""
vlan_16_sub_w_mask = ""
vlan_16_sub_no_mask = ""

# Use vlan 17 for properties that have in unit TP-LINK switches, 
#if the property does not use comment out the following line.
#vlan_17_ip_w_mask = "value/x"
# APs will get ip addressing via dhcp from the above controller the range always excludes 
# the first and last 5 addresses of the pool I.E. 100.97.24.5-100.97.27.250
ap_dhcp_range = ""

# Vanity vlans usually start at 1000 unless a router is being configured for a legacy site
vanity_vlan_start = ""
vanity_vlan_end = ""

# DHCP option code will eith be 43 or 138 depending on hardware vendor.
# DHCP option name usually take s the form PROPERYCODE_VSZ I.E. TORR_VSZ
# DHCP option value is a hex representation of the controller's IP address preceded by "0x"
dhcp_opt_code = ""
dhcp_opt_name = prop_code + "_VSZ"
dhcp_opt_value = ""

# Enter the SNMP server to send logs to
location = "City, ST"
router_ip = "" # Router vlan 15 IP
snmp_server = "" # Regional Auvik Collector

#Enter interfaces to monitor for net-flow and SNMP:
#For OOB: WAN-sfp1, sfp-plus3, LAN-sfp4
#For DC WAN: ISP-WAN-sfp28-1, sfp28-7, sfp28-11, sfp28-12, PO1
#For MDU: WAN-sfp1, LAN-sfp4
dc_oob = ""
dc_code = ""
#wg_port = ""
wg_ip_add = ""
remote_add = ""
router_id = ""
interfaces = ["WAN-sfp1","LAN-sfp4","ISP-SFP1","ether1"]

##################################################################################
#########################       SCRIPT BEGINS HERE       #########################
##################################################################################

def Send(screen, command):
    screen.Send(command + "\r")
    crt.Sleep(10)


def Base_Config(screen, hostname, admin_pw, aernoc_pw, aertech_pw, aertikauvik_pw, timezone, dns_prim, dns_second):
    Send(screen, "/system identity set name={}".format(hostname))
    Send(screen, "/user")
    Send(screen, """set number=0 comment="System Default User" group=full name=admin password={}""".format(admin_pw))
    Send(screen, """add comment="NOC Engineers" group=full name=***** password={}""".format(*****_pw))
    Send(screen, """add comment="Field Engineers" group=full name=***** password={}""".format(******_pw))
    Send(screen, """add comment="Auvik Monitoring" group=full name=***** password={}""".format(*******_pw))
    Send(screen, "/system clock set time-zone-name=US/{}".format(timezone))
    Send(screen, "/ip dns")
    Send(screen, "set allow-remote-requests=no")
    Send(screen, "set servers={},{}".format(dns_prim,dns_second))
    Send(screen, "/system ntp client set enabled=yes servers=time.nist.gov,0.north-america.pool.ntp.org,1.north-america.pool.ntp.org")
    Send(screen, "/ip neighbor discovery-settings")
    Send(screen, "set protocol=cdp,lldp")
    Send(screen, "/interface ethernet")
    Send(screen, "set [ find default-name=ether13 ] name=MGMT-e13")
    Send(screen, """set [ find default-name=ether1 ] name=ether1 comment="WAN BACKUP" """)
    Send(screen, "set [ find default-name=sfp-sfpplus4 ] advertise=10G-baseSR-LR,1G-baseX name=LAN-sfp4 speed=1G-baseX")
    Send(screen, "set [ find default-name=sfp-sfpplus1 ] advertise=10G-baseSR-LR,1G-baseX name=WAN-sfp1 speed=1G-baseX")
    Send(screen, "/interface ethernet switch set 0 l3-hw-offloading=no")   


def Config_Subinterfaces(screen, wan_vlan, prop_code, vanity_vlan_start, vanity_vlan_end):
    Send(screen, "/interface vlan")
    Send(screen, """add interface=WAN-sfp1 name=ISP-SFP1 vlan-id={} comment="WAN" """.format(wan_vlan))
    Send(screen, """add interface=LAN-sfp4 name=VLAN15 vlan-id=15 comment="NET MGMT" """)
    Send(screen, """add interface=LAN-sfp4 name=VLAN16 vlan-id=16 comment="AP MGMT" """)
    Send(screen, """add interface=LAN-sfp4 name=VLAN100 vlan-id=100 comment="AERWAVE WLAN" """)
    Send(screen, """add interface=LAN-sfp4 name=VLAN400 vlan-id=400 comment="{}_BoH" """.format(prop_code))
    Send(screen, """add interface=LAN-sfp4 name=VLAN401 vlan-id=401 comment="{}_IoT" """.format(prop_code))
    for vlan in range(int(vanity_vlan_start), (int(vanity_vlan_end)+1)):
        Send(screen, """add interface=LAN-sfp4 name=("VLAN" . {}) vlan-id={} comment="UNIT WLAN" """.format(str(vlan),str(vlan)))


def Config_IP_Addressing(screen, wan_add_w_mask, failover_ip_w_mask, vlan_15_ip_w_mask, vlan_16_ip_w_mask, prop_code, vanity_vlan_start, vanity_vlan_end):
    Send(screen, "/ip address")
    Send(screen, """add address={} interface=ISP-SFP1 comment="WAN IP" """.format(wan_add_w_mask))
    Send(screen, """add address={} interface=ether1 comment="WAN FAILOVER IP" """.format(failover_ip_w_mask))
    Send(screen, """add address={} interface=VLAN15 comment="NET MGMT" """.format(vlan_15_ip_w_mask))
    Send(screen, """add address={} interface=VLAN16 comment="AP MGMT" """.format(vlan_16_ip_w_mask))
    Send(screen, """add address=10.100.0.1/16 interface=VLAN100 network=10.100.0.0 comment="AERWAVE WLAN" \r""")
    Send(screen, """add address=10.40.0.1/24 interface=VLAN400 network=10.40.0.0 comment="{} BoH" """.format(prop_code))
    Send(screen, """add address=10.42.0.1/16 interface=VLAN401 network=10.42.0.0 comment="{} IoT" """.format(prop_code))
    Send(screen, ":global base 10.128.0.0") 
    for vlan in range(int(vanity_vlan_start), (int(vanity_vlan_end)+1)): 
        Send(screen, "{")
        Send(screen, ":local id ({} - 1000);".format(str(vlan)))
        Send(screen, ":local ip ($base + ($id * 256) + 1)")
        Send(screen, """add address=("$ip/24") interface=("VLAN{}") network=("$ip") comment="UNIT ADDRESSES" """.format(str(vlan)))
        Send(screen, "}")       
    

def Config_Routing(screen, wan_gw_add, failover_gw_ip):
    Send(screen, "/ip route")
    Send(screen, "add disabled=no distance=1 dst-address=0.0.0.0/0 gateway={} routing-table=main suppress-hw-offload=no".format(wan_gw_add))
    Send(screen, "add disabled=no distance=2 dst-address=0.0.0.0/0 gateway={} routing-table=main suppress-hw-offload=no".format(failover_gw_ip))
    

def Config_DHCP(screen, dhcp_opt_code, dhcp_opt_name, dhcp_opt_value, ap_dhcp_range, prop_code, vanity_vlan_start, vanity_vlan_end, vlan_16_sub_w_mask, dns_prim, dns_second, vlan_16_ip_no_mask):
    Send(screen, "/ip dhcp-server option add code={} name={} value={}".format(dhcp_opt_code,dhcp_opt_name,dhcp_opt_value))
    Send(screen, "/ip dhcp-server option sets add name={} options={}".format(dhcp_opt_name,dhcp_opt_name))
    Send(screen, "/ip pool")
    Send(screen, "add name=AP_MGMT ranges={}".format(ap_dhcp_range))
    Send(screen, "add name=AERWAVE_WLAN ranges=10.100.0.5-10.100.255.250")
    Send(screen, "add name={}_BoH ranges=10.40.0.5-10.40.0.250".format(prop_code))    
    Send(screen, "add name={}_IoT ranges=10.42.0.5-10.42.255.250".format(prop_code))
    Send(screen, ":global base 10.128.0.0")
    for vlan in range(int(vanity_vlan_start), (int(vanity_vlan_end)+1)): 
        Send(screen, "{")
        Send(screen, ":local id ({} - 1000);".format(str(vlan)))
        Send(screen, ":local ip ($base + ($id * 256) + 5)")
        Send(screen, ":local ip1 ($ip + 245)")
        Send(screen, """add name=("VLAN{}") ranges=("$ip-$ip1")""".format(str(vlan)))
        Send(screen, "}")

    Send(screen, "/ip dhcp-server")
    Send(screen, """add add-arp=yes address-pool=AP_MGMT dhcp-option-set={} interface=VLAN16 lease-time=1d name=AP_MGMT comment="AP MGMT" """.format(dhcp_opt_name))
    Send(screen, """add add-arp=yes address-pool=AERWAVE_WLAN interface=VLAN100 lease-time=1d name=AERWAVE_WLAN comment="AERWAVE WLAN" """)
    Send(screen, """add add-arp=yes address-pool={}_BoH interface=VLAN400 lease-time=1d name={}_BoH comment="{} BoH" """.format(prop_code,prop_code,prop_code))
    Send(screen, """add add-arp=yes address-pool={}_IoT interface=VLAN401 lease-time=1d name={}_IoT comment="{} IoT" """.format(prop_code,prop_code,prop_code))
    for vlan in range(int(vanity_vlan_start), int(vanity_vlan_end)+1):
        Send(screen, """add add-arp=yes address-pool=("VLAN" . {}) disabled=no interface=("VLAN" . {}) name=("VLAN" . {}) lease-time=1d comment="UNIT DHCP" """.format(str(vlan),str(vlan),str(vlan)))
    
    Send(screen, "/ip dhcp-server network")
    Send(screen, """add address={} dns-server={},{} gateway={} comment="AP MGMT" """.format(vlan_16_sub_w_mask,dns_prim,dns_second,vlan_16_ip_no_mask))
    Send(screen, """add address=10.100.0.0/16 dns-server={},{} gateway=10.100.0.1 comment="AERWAVE WLAN" """.format(dns_prim,dns_second))
    Send(screen, """add address=10.40.0.0/24 dns-server={},{} gateway=10.40.0.1 comment="{} BoH" """.format(dns_prim,dns_second,prop_code))
    Send(screen, """add address=10.42.0.0/16 dns-server={},{} gateway=10.42.0.1 comment="{} IoT" """.format(dns_prim,dns_second,prop_code))
    Send(screen, ":global base 10.128.0.0")
    for vlan in range(int(vanity_vlan_start), (int(vanity_vlan_end)+1)):
        Send(screen, "{")
        Send(screen, ":local id ({} - 1000);".format(str(vlan)))
        Send(screen, ":local ip ($base + ($id * 256))")
        Send(screen, ":local ip1 ($base + ($id * 256) +1)")
        Send(screen, """add address=("$ip/24") dns-server={},{} gateway=("$ip1") comment="VLAN {}" """.format(dns_prim,dns_second,str(vlan)))
        Send(screen, "}")


def Config_Firewall(screen, vlan_16_sub_w_mask):
    Send(screen, "/ip service")
    Send(screen, "set telnet disabled=yes")
    Send(screen, "set www disabled=yes")
    Send(screen, "/ip firewall service-port")
    Send(screen, "set ftp disabled=yes")
    Send(screen, "set h323 disabled=yes")
    Send(screen, "/ip firewall nat")
    Send(screen, "add action=masquerade chain=srcnat out-interface=ISP-SFP1 src-address=10.128.0.0/12")
    Send(screen, "add action=masquerade chain=srcnat out-interface=ISP-SFP1 src-address={}".format(vlan_16_sub_w_mask))
    Send(screen, "/ip firewall address-list")
    Send(screen, """add address=x.x.x.x/32 list=AER-MGMT-ALLOW comment="Azure VPN01" """)
    Send(screen, """add address=x.x.x.x/32 list=AER-MGMT-ALLOW comment="Azure VPN02" """)
    Send(screen, """add address=x.x.x.x/32 list=AER-MGMT-ALLOW comment="Azure WIN01" """)
    Send(screen, """add address=x.x.x.x/32 list=AER-MGMT-ALLOW comment="Azure WIN02" """)
    Send(screen, """add address=x.x.x.x/32 list=AER-MGMT-ALLOW comment="Azure LINUX01" """)
    Send(screen, """add address=x.x.x.x/32 list=AER-MGMT-ALLOW comment="Azure LINUX02" """)
    Send(screen, """add address=x.x.x.x/16 list=AER-MGMT-ALLOW comment="WEST VPN" """)
    Send(screen, """add address=x.x.x.x/16 list=AER-MGMT-ALLOW comment="EAST VPN" """)
    Send(screen, """add address=x.x.x.x/16 list=AER-MGMT-ALLOW comment="WEST VMWARE" """)
    Send(screen, """add address=x.x.x.x/16 list=AER-MGMT-ALLOW comment="EAST VMWARE" """)
    Send(screen, """add address=x.x.x.x/24 list=AER-MGMT-ALLOW comment="MikroTik MGMT Port" """)
    Send(screen, "add address=x.x.x.x/8 list=ICMP-ALLOW")
    Send(screen, "add address=x.x.x.x/16 list=ICMP-ALLOW")
    Send(screen, "add address=x.x.x.x/12 list=ICMP-ALLOW")
    Send(screen, "add address=x.x.x.x/10 list=ICMP-ALLOW")
    Send(screen, "/ip firewall filter")
    Send(screen, """add action=accept chain=input comment="Company Secure Sources" connection-state=established,related,new,untracked src-address-list=AER-MGMT-ALLOW disabled=yes""")
    Send(screen, """add action=accept chain=input comment="ALLOW BGP and BFD" connection-state=established,related,new,untracked port=179,3784,3785 protocol=tcp disabled=yes""")
    Send(screen, """add action=accept chain=input comment="UDP for Wireguard and BFD" port=3784,3785,13000-13599 protocol=udp disabled=yes""")
    Send(screen, """add action=accept chain=input comment="ALLOW - MikroTik Upgrades" connection-state=established disabled=yes""")
    Send(screen, """add action=accept chain=input comment="RFC1918 ICMP Allow" protocol=icmp src-address-list=ICMP-ALLOW disabled=yes""")
    Send(screen, """add action=accept chain=input comment="RADIUS for MAC AUTH" dst-address=127.0.0.1 src-address=127.0.0.1 disabled=yes""")
    Send(screen, """add action=drop chain=input comment="DROP ALL - INPUT to ROUTER" disabled=yes""")
    Send(screen, """add action=accept chain=forward comment="ALL LAN to ISP" in-interface=all-vlan out-interface=ISP-SFP1 disabled=yes""")
    Send(screen, """add action=accept chain=forward comment="ISP to ALL LAN - Return Traffic" in-interface=ISP-SFP1 out-interface=all-vlan disabled=yes""")
    Send(screen, """add action=drop chain=forward comment="DROP ALL OTHER TRAFFIC" in-interface=all-vlan out-interface=all-vlan disabled=yes""")
    Send(screen, "/routing filter rule")
    Send(screen, """add chain=ISP-DC-DEF-RX comment="DEFAULT ROUTE FILTER" disabled=no rule="if (dst == 0.0.0.0/0) {accept}" """)
    Send(screen, """add chain=MDU-OOB-RX comment="AZURE WG - VPN01" disabled=no rule="if (dst==100.95.1.0/24) {accept}" """)
    Send(screen, """add chain=MDU-OOB-RX comment="AZURE WG - VPN02" disabled=no rule="if (dst==100.127.1.0/24) {accept}" """)
    Send(screen, """add chain=MDU-OOB-RX comment="AZURE CENTRAL HUB" disabled=no rule="if (dst in 172.16.192.0/18 && dst-len>=18) {accept}" """)
    Send(screen, """add chain=MDU-OOB-RX comment="VM WORKLOADS - WEST" disabled=no rule="if (dst in 172.23.0.0/16 && dst-len in 16-32) {accept}" """)
    Send(screen, """add chain=MDU-OOB-RX comment="VM WORKLOADS - EAST" disabled=no rule="if (dst in 172.31.0.0/16 && dst-len in 16-32) {accept}" """)
    Send(screen, """add chain=MDU-OOB-TX comment="DC MGMT NETWORKS - WEST" disabled=no rule="if (dst in 100.64.0.0/11 && dst-len in 11-32) {accept}" """)
    Send(screen, """add chain=MDU-OOB-TX comment="DC MGMT NETWORKS - EAST" disabled=no rule="if (dst in 100.96.0.0/11 && dst-len in 11-32) {accept}" """)
    Send(screen, "/")


def Config_SNMPv3(screen, aertik_auvik_snmpv3, location, router_ip, snmp_server):
    Send(screen, "/snmp community")
    Send(screen, "set [ find default=yes ] disabled=yes")
    Send(screen, "add addresses=::/0 authentication-protocol=SHA1 encryption-protocol=AES name=community-snmp security=authorized write-access=yes authentication-password={} encryption-password={}".format(********_snmpv3,********_snmpv3))
    Send(screen, "/snmp")
    Send(screen, """set contact=company@company.com enabled=yes location="{}" src-address={} trap-community=community-snmp trap-generators=interfaces,start-trap trap-target={} trap-version=3""".format(location,router_ip,snmp_server))
    for interface in interfaces:
        Send(screen, "set trap-interfaces={}".format(interface))

    Send(screen, "/system logging action set 3 remote={} src-address={}".format(snmp_server,router_ip)) 
    Send(screen, "/system logging")
    Send(screen, "set 0 action=remote")  
    Send(screen, "set 1 action=remote")
    Send(screen, "set 2 action=remote")
    Send(screen, "set 3 action=remote")   
    Send(screen, "/ip traffic-flow")
    Send(screen, "set enabled=yes")   
    for interface in interfaces:
        Send(screen, "set interfaces={}".format(interface))

    Send(screen, "/ip traffic-flow target add dst-address={} src-address={} version=5".format(snmp_server,router_ip))


def Config_WG_BGP(screen, vlan_15_sub_w_mask, vlan_16_sub_w_mask, dc_oob, dc_code, wg_ip_add, remote_add, router_id):
    # 1. Deploy the BGP filter and FW IP group
    Send(screen, "/ip firewall address-list")
    Send(screen, """add address={} comment="NET MGMT" list=MDU-DC-FW-TX""".format(vlan_15_sub_w_mask))
    Send(screen, """add address={} comment="AP MGMT" list=MDU-DC-FW-TX""".format(vlan_16_sub_w_mask))
    # 2 Create WG interface
    Send(screen, "/interface wireguard")
    #add comment=aerNYCmfoob01 listen-port=13301 mtu=1420 name=NYC-DC-WG
    Send(screen, "add comment={} listen-port=13301 mtu=1420 name={}-DC-WG".format(dc_oob,dc_code))
    # 3. Add IP to WG interface
    Send(screen, "/ip address")
    Send(screen, """add address={} interface={}-DC-WG comment="{}" """.format(wg_ip_add,dc_code,dc_oob))
    # 4. Build the BGP peering
    Send(screen, "/routing bfd configuration")
    Send(screen, "add disabled=no interfaces={}-DC-WG min-rx=1s min-tx=1s multiplier=5 vrf=main".format(dc_code))
    Send(screen, "/routing bgp connection")
    # variables for name, remote address, and router-id
    Send(screen, "add address-families=ip as=65535 connect=yes disabled=no input.filter=MDU-OOB-RX listen=yes local.role=ebgp name={} output.filter-chain=MDU-OOB-TX .network=MDU-DC-FW-TX remote.address={} .as=64700 router-id={} routing-table=main use-bfd=yes".format(dc_oob,remote_add,router_id))


def Format_Disk(screen):
    Send(screen, "/")
    Send(screen, "/disk format-drive nvme1 file-system=ext4 mbr-partition-table=no")
    Send(screen, "/system/device-mode/update container=yes")
    Send(screen, "/system/reboot")
    
def Main():

    crt.Screen.Synchronous = True
    
    Base_Config(crt.Screen, hostname, admin_pw, *****_pw, ******_pw, *******_pw, timezone, dns_prim, dns_second)

    Config_Subinterfaces(crt.Screen, wan_vlan, prop_code, vanity_vlan_start, vanity_vlan_end)

    Config_IP_Addressing(crt.Screen, wan_add_w_mask, failover_ip_w_mask, vlan_15_ip_w_mask, vlan_16_ip_w_mask, prop_code, vanity_vlan_start, vanity_vlan_end)

    Config_Routing(crt.Screen, wan_gw_add, failover_gw_ip)

    Config_DHCP(crt.Screen, dhcp_opt_code, dhcp_opt_name, dhcp_opt_value, ap_dhcp_range, prop_code, vanity_vlan_start, vanity_vlan_end, vlan_16_sub_w_mask, dns_prim, dns_second, vlan_16_ip_no_mask)

    Config_Firewall(crt.Screen, vlan_16_sub_w_mask)

    Config_SNMPv3(crt.Screen, ********_snmpv3, location, router_ip, snmp_server)

    Config_WG_BGP(crt.Screen, vlan_15_sub_w_mask, vlan_16_sub_w_mask, dc_oob, dc_code, wg_ip_add, remote_add, router_id)
    
    Format_Disk(crt.Screen)
    
Main()