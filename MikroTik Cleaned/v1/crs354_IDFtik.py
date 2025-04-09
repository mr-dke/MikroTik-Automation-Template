#$language = "Python"
#$interface = "1.0"

import os

#################################################################
####                  VARIABLES SECTION                      ####
#################################################################

#Enter variables bellow which will be used by the script.

#ALL values must be between the " "

#Enter the hostname of the router from the as-built and Managment IP with default gateway.
hostname = "aer90DGmrb1.1.1"

#Enter passwords to be used for each user being configured.
admin = "n0t1kl0rdh3r3!"
aernoc = "n0crul3th3t1k!"
aertech = "n0t3chh3r3!"
auvik = "l00k@th3tikcr@wl!"

# Choices are: US/Eastern, US/Central, US/Mountain, US/Pacific ****
timezone = "US/Pacific"
mgmt_ip = "100.64.6.236/27"
gw_ip = "100.64.6.231"

# VLAN ranges to configure for this Layer 3 switch.
vlan_start = "1000"
vlan_end = "1336"

#################################################################
#### DO NOT TOUCH BELOW THIS LINE - SCRIPT RUNS FROM HERE    ####
#################################################################

def Main():

####################################################

#! Be sure to update the system name.
    crt.Screen.Synchronous = True
    
    crt.Screen.Send("""
        /system identity\r
        set name=""" + hostname + "\r")
    crt.Sleep(2000) 

    crt.Screen.Send("""
        /user\r
        add comment="system default user" group=full name=admin password=""" + admin + "\r"
        """add comment="NOC Engineers" group=full name=aernoc password=""" + aernoc + "\r"
        """add comment="Field Engineers" group=full name=aertech password=""" + aertech + "\r"
        """add comment="Auvik Monitoring" group=full name=aertik-auvik password=""" + auvik + "\r\r""")
    crt.Sleep(2000)

    crt.Screen.Send("""
        /system clock\r
        set time-zone-name=""" + timezone + "\r""")
    crt.Sleep(2000)

    crt.Screen.Send(
    "/interface bridge\r"
    "set number=0 priority=0x705A vlan-filtering=yes\r"
    "add name=bridge15 priority=0x705a vlan-filtering=yes pvid=15\r")
    crt.Sleep(2000)

    crt.Screen.Send("""
    /interface bridge vlan\r
    add bridge=bridge comment="NET MGMT" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4 vlan-ids=15\r
    add bridge=bridge comment="AP MGMT" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4 untagged=ether1,ether2,ether3,ether4,ether5,ether6,ether7,ether8,ether9,ether10,ether11,ether12,ether13,ether14,ether15,ether16,ether17,ether18,ether19,ether20,ether21,ether22,ether23,ether24 vlan-ids=16\r
    add bridge=bridge comment="AERWAVE GENERAL NETWORK" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,ether1,ether2,ether3,ether4,ether5,ether6,ether7,ether8,ether9,ether10,ether11,ether12,ether13,ether14,ether15,ether16,ether17,ether18,ether19,ether20,ether21,ether22,ether23,ether24 vlan-ids=100\r
    add bridge=bridge comment="PROPERTY MANAGEMENT" tagged=sfp-sfpplus1,sfp-sfpplus2,sfp-sfpplus3,sfp-sfpplus4,ether1,ether2,ether3,ether4,ether5,ether6,ether7,ether8,ether9,ether10,ether11,ether12,ether13,ether14,ether15,ether16,ether17,ether18,ether19,ether20,ether21,ether22,ether23,ether24 vlan-ids=400\r
    :for e from=""" + vlan_start + """ to=""" + vlan_end + """ do={add bridge=bridge comment="UNIT WLAN" tagged=sfp-sfpplus1,sfp-sfpplus2,ether1,ether2,ether3,ether4,ether5,ether6,ether7,ether8,ether9,ether10,ether11,ether12,ether13,ether14,ether15,ether16,ether17,ether18,ether19,ether20,ether21,ether22,ether23,ether24 vlan-ids=$e}\r""")
    crt.Sleep(20000)

    crt.Screen.Send("""
    /interface vlan
    add interface=bridge15 name=VLAN15 vlan-id=15 comment="NET MGMT" \r""")
    crt.Sleep(2000)
    
    crt.Screen.Send("""
    /ip address
    add address=""" + mgmt_ip + """ interface=VLAN15 comment="NET MGMT"\r""")
    crt.Sleep(2000)

    crt.Screen.Send("""
        /interface bridge port\r
        set numbers=24,25,26,27 bridge=bridge15\r"""
    )
    crt.Sleep(2000)
    
    crt.Screen.Send(
        "/ip route\r"
        "add disabled=no distance=5 dst-address=0.0.0.0/0 gateway=" + gw_ip + """ pref-src="" routing-table=main scope=30 suppress-hw-offload=no target-scope=10 \r""")
    crt.Sleep(2000)


####################################################
# Commands with NO Variables.
    crt.Screen.Send("""
        /ip neighbor discovery-settings\r
        set protocol=cdp,lldp\r""")
    crt.Sleep(2000)

    crt.Screen.Send("""
        /ip dns\r
        set servers=1.1.1.1,8.8.8.8\r""")
    crt.Sleep(2000)

    crt.Screen.Send(
        "/interface ethernet switch\r"
        "set number=0 l3-hw-offloading=yes\r")
    crt.Sleep(2000)

    crt.Screen.Send("""
        /ip firewall service-port\r
        set ftp disabled=yes\r
        set h323 disabled=yes\r
        set sip disabled=yes\r
        set pptp disabled=yes\r""")
    crt.Sleep(2000)

    crt.Screen.Send("""
        /ip service\r
        set telnet disabled=yes\r
        set ftp disabled=yes\r
        set www disabled=yes\r
        set api disabled=yes\r
        set api-ssl disabled=yes\r""")
    crt.Sleep(2000)

    crt.Screen.Send("""
        /system note\r
        set show-at-login=no\r""")
    crt.Sleep(2000) 

    crt.Screen.Send(
        "/system ntp client\r"
        "set enabled=yes servers=time.nist.gov,0.north-america.pool.ntp.org,1.north-america.pool.ntp.org\r")
    crt.Sleep(2000) 


Main()