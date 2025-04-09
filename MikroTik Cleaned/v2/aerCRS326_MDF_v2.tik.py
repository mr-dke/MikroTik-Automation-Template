import os

#################################################################
####                  VARIABLES SECTION                      ####
#################################################################
#ALL values must be between the " "
#Enter the hostname of the router from the as-built and Managment IP with default gateway.
hostname = "value"

#Enter passwords to be used for each user being configured.
****_pw = "value"
*****_pw = "value"
******_pw = "value"
*******_pw = "value"
********_snmpv3 = "value"

# Choices are: US/Eastern, US/Central, US/Mountain, US/Pacific ****
timezone = "value"
mgmt_ip = "value"
gw_ip = "value"

# VLAN ranges to configure for this Layer 3 switch.
vlan_start = "value"
vlan_end = "value"

location = "City, ST" # City, ST
switch_ip = "value" # vlan 15 SVI IP
snmp_server = "value" # Regional Auvik Collector.

# the interface should not change any time soon.
interface = "bridge"
#################################################################
#### DO NOT TOUCH BELOW THIS LINE - SCRIPT RUNS FROM HERE    ####
#################################################################

def Send(screen, command):
    screen.Send(command + "\r")
    crt.Sleep(50)

def Base_Config(screen, hostname, admin_pw, aernoc_pw, aertech_pw, aertikauvik_pw, timezone):
    Send(screen, "/system identity set name={}".format(hostname))
    Send(screen, """/user set number=0 comment="System Default User" group=full name=**** password={}""".format(****_pw))
    Send(screen, """/user add comment="NOC Engineers" group=full name=***** password={}""".format(*****_pw))
    Send(screen, """/user add comment="Field Engineers" group=full name=****** password={}""".format(******_pw))
    Send(screen, """/user add comment="Auvik Monitoring" group=full name=******* password={}""".format(*******_pw))
    Send(screen, "/system clock set time-zone-name={}".format(timezone))
    Send(screen, "/ip dns set allow-remote-requests=no")
    Send(screen, "/interface bridge set number=0 priority=0x705A vlan-filtering=yes pvid=15")

def Config_VLANS(screen, interface, vlan_start, vlan_end):
    Send(screen, "/interface bridge vlan")
    Send(screen, """add bridge={} comment="NET MGMT" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,sfp-sfpplus5,sfp-sfpplus6,sfp-sfpplus7,sfp-sfpplus8,sfp-sfpplus9,sfp-sfpplus10,sfp-sfpplus11,sfp-sfpplus12,sfp-sfpplus13,sfp-sfpplus14,sfp-sfpplus15,sfp-sfpplus16,sfp-sfpplus17,sfp-sfpplus18,sfp-sfpplus19,sfp-sfpplus20,sfp-sfpplus21,sfp-sfpplus22,sfp-sfpplus23,sfp-sfpplus24 vlan-ids=15""".format(interface))
    Send(screen, """add bridge={} comment="AP MGMT" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,sfp-sfpplus5,sfp-sfpplus6,sfp-sfpplus7,sfp-sfpplus8,sfp-sfpplus9,sfp-sfpplus10,sfp-sfpplus11,sfp-sfpplus12,sfp-sfpplus13,sfp-sfpplus14,sfp-sfpplus15,sfp-sfpplus16,sfp-sfpplus17,sfp-sfpplus18,sfp-sfpplus19,sfp-sfpplus20,sfp-sfpplus21,sfp-sfpplus22,sfp-sfpplus23,sfp-sfpplus24 vlan-ids=16""".format(interface))
    Send(screen, """add bridge={} comment="AERWAVE GENERAL NETWORK" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,sfp-sfpplus5,sfp-sfpplus6,sfp-sfpplus7,sfp-sfpplus8,sfp-sfpplus9,sfp-sfpplus10,sfp-sfpplus11,sfp-sfpplus12,sfp-sfpplus13,sfp-sfpplus14,sfp-sfpplus15,sfp-sfpplus16,sfp-sfpplus17,sfp-sfpplus18,sfp-sfpplus19,sfp-sfpplus20,sfp-sfpplus21,sfp-sfpplus22,sfp-sfpplus23,sfp-sfpplus24 vlan-ids=100""".format(interface))
    Send(screen, """add bridge={} comment="PROPERTY MANAGEMENT" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,sfp-sfpplus5,sfp-sfpplus6,sfp-sfpplus7,sfp-sfpplus8,sfp-sfpplus9,sfp-sfpplus10,sfp-sfpplus11,sfp-sfpplus12,sfp-sfpplus13,sfp-sfpplus14,sfp-sfpplus15,sfp-sfpplus16,sfp-sfpplus17,sfp-sfpplus18,sfp-sfpplus19,sfp-sfpplus20,sfp-sfpplus21,sfp-sfpplus22,sfp-sfpplus23,sfp-sfpplus24 vlan-ids=400""".format(interface))
    Send(screen, """add bridge={} comment="PROPERTY MANAGEMENT" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,sfp-sfpplus5,sfp-sfpplus6,sfp-sfpplus7,sfp-sfpplus8,sfp-sfpplus9,sfp-sfpplus10,sfp-sfpplus11,sfp-sfpplus12,sfp-sfpplus13,sfp-sfpplus14,sfp-sfpplus15,sfp-sfpplus16,sfp-sfpplus17,sfp-sfpplus18,sfp-sfpplus19,sfp-sfpplus20,sfp-sfpplus21,sfp-sfpplus22,sfp-sfpplus23,sfp-sfpplus24 vlan-ids=401""".format(interface))
    for vlan in range(int(vlan_start), (int(vlan_end) + 1)):
        Send(screen, """add bridge=bridge comment="UNIT WLAN" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,sfp-sfpplus5,sfp-sfpplus6,sfp-sfpplus7,sfp-sfpplus8,sfp-sfpplus9,sfp-sfpplus10,sfp-sfpplus11,sfp-sfpplus12,sfp-sfpplus13,sfp-sfpplus14,sfp-sfpplus15,sfp-sfpplus16,sfp-sfpplus17,sfp-sfpplus18,sfp-sfpplus19,sfp-sfpplus20,sfp-sfpplus21,sfp-sfpplus22,sfp-sfpplus23,sfp-sfpplus24 vlan-id={}""".format(str(vlan)))
    Send(screen, "/")

def Config_Interfaces(screen, mgmt_ip, gw_ip):
    Send(screen, """/interface vlan add interface=bridge name=VLAN15 vlan-id=15 comment="NET MGMT" """)
    Send(screen, """/ip address add address={} interface=VLAN15 comment="NET MGMT" """.format(mgmt_ip))
    Send(screen, "/ip address remove numbers=0")
    Send(screen, "/interface bridge port set numbers=9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32 bridge=bridge")
    Send(screen, """/ip route add disabled=no distance=4 dst-address=0.0.0.0/0 gateway={} pref-src="" routing-table=main scope=30 suppress-hw-offload=no target-scope=10""".format(gw_ip))
    
def Config_No_Vars(screen):
    Send(screen, "/ip neighbor discovery-settings set protocol=cdp,lldp")
    Send(screen, "/ip dns set servers=1.1.1.1,8.8.8.8")
    Send(screen, "/interface ethernet switch set number=0 l3-hw-offloading=no")
    Send(screen, "/ip firewall service-port")
    Send(screen, "set ftp disabled=yes")
    Send(screen, "set h323 disabled=yes")
    Send(screen, "set sip disabled=yes")
    Send(screen, "set pptp disabled=yes")
    Send(screen, "/ip service")
    Send(screen, "set telnet disabled=yes")
    Send(screen, "set ftp disabled=yes")
    Send(screen, "set www disabled=yes")
    Send(screen, "set api disabled=yes")
    Send(screen, "set api-ssl disabled=yes")
    Send(screen, "/system note set show-at-login=no")
    Send(screen, "/system ntp client set enabled=yes servers=time.nist.gov,0.north-america.pool.ntp.org,1.north-america.pool.ntp.org")

def Config_SNMPv3(screen, ********_snmpv3, location, switch_ip, interface, snmp_server):
    Send(screen, "/snmp community set [ find default=yes ] disabled=yes")
    Send(screen, "/snmp community add addresses=::/0 authentication-protocol=SHA1 encryption-protocol=AES name=aertik-auvik-snmp security=authorized write-access=yes authentication-password={} encryption-password={}".format(********_snmpv3,********_snmpv3))
    Send(screen, """/snmp set contact=company@company.com enabled=yes location="{}" src-address={} trap-community=********-snmp trap-generators=interfaces,start-trap trap-target={} trap-version=3""".format(location,switch_ip,snmp_server))
    Send(screen, "/snmp set trap-interfaces={}".format(interface))
    Send(screen, "/system logging action set 3 remote={} src-address={}".format(snmp_server,switch_ip))
    Send(screen, "/system logging")
    for num in range(4):
        Send(screen, "set {} action=remote".format(num))
    Send(screen, "/ip traffic-flow")
    Send(screen, "set enabled=yes interfaces={}".format(interface))
    Send(screen, "/ip traffic-flow target add dst-address={} src-address={} version=5".format(snmp_server,switch_ip))
    Send(screen, "/")

def Main():

    crt.Screen.Synchronous = True
    
    Base_Config(crt.Screen, hostname, ****_pw, *****_pw, ******_pw, *******_pw, timezone)
   
    Config_VLANS(crt.Screen, interface, vlan_start, vlan_end)

    Config_Interfaces(crt.Screen, mgmt_ip, gw_ip)

    Config_No_Vars(crt.Screen)

    Config_SNMPv3(crt.Screen, ********_snmpv3, location, switch_ip, interface, snmp_server)

Main()