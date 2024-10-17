# Welcome to the EVPN Workshop at NANOG 92
This README is your starting point into the hands on section.

Pre-requisite: A laptop with SSH client

If you need help, please raise your hand and a Nokia team member will be happy to assist.

## Lab Environment

A Nokia team member will provide you with a sheet that contains:
- your group and VM ID
- SSH credentials to the VM instance
- URL of this repo

> <p style="color:red">!!! Make sure to backup any code, config, ... <u> offline (e.g on your laptop)</u>. 
> The VM instances might be destroyed once the Workshop is concluded.</p>

# Workshop
The objective of the handson section of this workshop is the following:
- Build a DC fabric with leaf and spine
- Build Layer 2 EVPN
- Build Layer 3 EVPN

## Lab Topology
![image](images/lab-topology.jpg)

## NOS (Network Operating System)

Both leafs and Spine nodes will be running Nokia [SR Linux](https://www.nokia.com/networks/ip-networks/service-router-linux-NOS/).

## Deploying the lab

Login to the VM using the credentials on your sheet.

This Git repo is already cloned to your VM.
But in case you need it, use the below command to clone this repo to your VM.

```
git clone https://github.com/srlinuxamericas/N92-evpn.git
```

Verify that this git repo files are now available on your VM.

```
ls -lrt N92-evpn/n92-evpn-lab/
```

To deploy the lab, run the following:

```
cd N92-evpn
sudo clab deploy -t n92-evpn-lab/srl-evpn.clab.yml
```

[Containerlab](https://containerlab.dev/) will deploy the lab and display a table with the list of nodes and their IPs.

To display current deployed labs at any time, use:

```
sudo clab inspect --all
```

## Connecting to the devices

Find the nodename or IP address of the device and then use SSH.

Username: `admin`

Password: Refer to the provided sheet

```
ssh admin@clab-srl-evpn-leaf1
```

To login to the client, identify the client hostname using the `clab inspect` command above and then:

```
sudo docker exec –it clab-srl-evpn-client3 sh
```

## Physical link connectivity

When the lab is deployed with the default startup config, all the links are created with IPv4 and IPv6 addresses.

This allows to start configuring the protocols right away!

Check the [startup config](n92-evpn-lab/configs/fabric/startup) files to see how interfaces and IP addresses are configured in SR Linux.

### IPv4 Link Addressing

![image](images/lab-ipv4.jpg)

### IPv6 Link Addressing

![image](images/lab-ipv4.jpg)

### Verify reachability between devices

After the lab is deployed, check reachability between leaf and spine devices using ping.

Example on spine to Leaf1 for IPv4:

```
ping -c 3 192.168.10.2 network-instance default
```

Example on spine to Leaf1 for IPv6:

```
ping6 -c 3 192:168:10::2 network-instance default
```

## Configure BGP Underlay

We are now ready to start configuring the fabric for EVPN.

The first step is to configure BGP for underlay.

![image](images/bgp-underlay.jpg)

### SR Linux Configuration Mode

To enter candidate configuration edit mode in SR Linux, use:

```
enter candidate
```

To commit the configuration in SR Linux, use:

```
commit stay
```

### BGP Underlay Configuration

BGP underlay configuration on Leaf1:

```
set / network-instance default protocols bgp autonomous-system 64501
set / network-instance default protocols bgp router-id 1.1.1.1
set / network-instance default protocols bgp ebgp-default-policy import-reject-all false
set / network-instance default protocols bgp ebgp-default-policy export-reject-all false
set / network-instance default protocols bgp afi-safi ipv4-unicast admin-state enable
set / network-instance default protocols bgp group ebgp peer-as 64500
set / network-instance default protocols bgp group ebgp afi-safi ipv6-unicast admin-state enable
set / network-instance default protocols bgp neighbor 192.168.10.3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.10.3 export-policy [ export-underlay-v4 ]
set / network-instance default protocols bgp neighbor 192.168.10.3 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:10::3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:10::3 export-policy [ export-underlay-v6 ]
set / network-instance default protocols bgp neighbor 192:168:10::3 afi-safi ipv4-unicast admin-state disable
```

BGP underlay configuration on Leaf2:

```
set / network-instance default protocols bgp autonomous-system 64502
set / network-instance default protocols bgp router-id 2.2.2.2
set / network-instance default protocols bgp ebgp-default-policy import-reject-all false
set / network-instance default protocols bgp ebgp-default-policy export-reject-all false
set / network-instance default protocols bgp afi-safi ipv4-unicast admin-state enable
set / network-instance default protocols bgp group ebgp peer-as 64500
set / network-instance default protocols bgp group ebgp afi-safi ipv6-unicast admin-state enable
set / network-instance default protocols bgp neighbor 192.168.20.3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.20.3 export-policy [ export-underlay-v4 ]
set / network-instance default protocols bgp neighbor 192.168.20.3 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:20::3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:20::3 export-policy [ export-underlay-v6 ]
set / network-instance default protocols bgp neighbor 192:168:20::3 afi-safi ipv4-unicast admin-state disable
```

BGP underlay configuration on Spine:

```
set / network-instance default protocols bgp autonomous-system 64500
set / network-instance default protocols bgp router-id 3.3.3.3
set / network-instance default protocols bgp ebgp-default-policy import-reject-all false
set / network-instance default protocols bgp ebgp-default-policy export-reject-all false
set / network-instance default protocols bgp afi-safi ipv4-unicast admin-state enable
set / network-instance default protocols bgp group ebgp afi-safi ipv6-unicast admin-state enable
set / network-instance default protocols bgp neighbor 192.168.10.2 peer-as 64501
set / network-instance default protocols bgp neighbor 192.168.10.2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.10.2 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192.168.20.2 peer-as 64502
set / network-instance default protocols bgp neighbor 192.168.20.2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.20.2 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:10::2 peer-as 64501
set / network-instance default protocols bgp neighbor 192:168:10::2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:10::2 afi-safi ipv4-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:20::2 peer-as 64502
set / network-instance default protocols bgp neighbor 192:168:20::2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:20::2 afi-safi ipv4-unicast admin-state disable
```

### BGP Underlay Verification

The BGP underlay sessions should be UP now. Check using the following commands on the Spine.

```
show network-instance default protocols bgp neighbor
```

The output confirms that both IPv4 and IPv6 BGP neighbor sessions are established.

```
A:spine# show network-instance default protocols bgp neighbor
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP neighbor summary for network-instance "default"
Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+-----------------------+---------------------------------+-----------------------+--------+------------+------------------+------------------+----------------+---------------------------------+
|       Net-Inst        |              Peer               |         Group         | Flags  |  Peer-AS   |      State       |      Uptime      |    AFI/SAFI    |         [Rx/Active/Tx]          |
+=======================+=================================+=======================+========+============+==================+==================+================+=================================+
| default               | 192.168.10.2                    | ebgp                  | S      | 64501      | established      | 0d:0h:9m:17s     | ipv4-unicast   | [1/1/1]                         |
| default               | 192.168.20.2                    | ebgp                  | S      | 64502      | established      | 0d:0h:9m:17s     | ipv4-unicast   | [1/1/1]                         |
| default               | 192:168:10::2                   | ebgp                  | S      | 64501      | established      | 0d:0h:9m:22s     | ipv6-unicast   | [1/1/1]                         |
| default               | 192:168:20::2                   | ebgp                  | S      | 64502      | established      | 0d:0h:9m:22s     | ipv6-unicast   | [1/1/1]                         |
+-----------------------+---------------------------------+-----------------------+--------+------------+------------------+------------------+----------------+---------------------------------+
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Summary:
4 configured neighbors, 4 configured sessions are established, 0 disabled peers
0 dynamic peers
```

## Configure BGP for Overlay

BGP is required to advertise EVPN routes between the leaf devices.

For establishing overlay BGP neighbors, we will use the system loopback IP of the Leaf nodes. These IPs are pre-configured as part of initial lab deployment and can be verified using `show interface system0` command.

BGP overlay configuration is not required on the Spine as Spine is not aware of EVPN routes.

![image](images/bgp-overlay.jpg)

### BGP Overlay Configuration

BGP Overlay configuration on Leaf1:

```
set / network-instance default protocols bgp group evpn peer-as 65500
set / network-instance default protocols bgp group evpn multihop admin-state enable
set / network-instance default protocols bgp group evpn afi-safi evpn admin-state enable
set / network-instance default protocols bgp group evpn afi-safi ipv4-unicast admin-state disable
set / network-instance default protocols bgp group evpn afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp group evpn local-as as-number 65500
set / network-instance default protocols bgp neighbor 2.2.2.2 peer-group evpn
set / network-instance default protocols bgp neighbor 2.2.2.2 transport local-address 1.1.1.1
set / network-instance default protocols bgp neighbor 2001::2 peer-group evpn
set / network-instance default protocols bgp neighbor 2001::2 transport local-address 2001::1
```

BGP Overlay configuration on Leaf2:

```
set / network-instance default protocols bgp group evpn peer-as 65500
set / network-instance default protocols bgp group evpn multihop admin-state enable
set / network-instance default protocols bgp group evpn afi-safi evpn admin-state enable
set / network-instance default protocols bgp group evpn afi-safi ipv4-unicast admin-state disable
set / network-instance default protocols bgp group evpn afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp group evpn local-as as-number 65500
set / network-instance default protocols bgp neighbor 1.1.1.1 peer-group evpn
set / network-instance default protocols bgp neighbor 1.1.1.1 transport local-address 2.2.2.2
set / network-instance default protocols bgp neighbor 2001::1 peer-group evpn
set / network-instance default protocols bgp neighbor 2001::1 transport local-address 2001::2
```

### BGP Overlay Verification

The BGP overlay sessions should be UP now. Check using the following commands on Leaf1 or Leaf2.

```
show network-instance default protocols bgp neighbor
```

The output confirms that EVPN neigbor sessions are established to both the IPv4 and IPv6 loopback IPs.
The output also displays the underlay IPv4 and IPv6 sessions.

```
A:leaf1# show network-instance default protocols bgp neighbor
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP neighbor summary for network-instance "default"
Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+-----------------------+---------------------------------+-----------------------+--------+------------+------------------+------------------+----------------+---------------------------------+
|       Net-Inst        |              Peer               |         Group         | Flags  |  Peer-AS   |      State       |      Uptime      |    AFI/SAFI    |         [Rx/Active/Tx]          |
+=======================+=================================+=======================+========+============+==================+==================+================+=================================+
| default               | 2.2.2.2                         | evpn                  | S      | 65500      | established      | 0d:0h:22m:42s    | evpn           | [0/0/0]                         |
| default               | 192.168.10.3                    | ebgp                  | S      | 64500      | established      | 0d:0h:22m:52s    | ipv4-unicast   | [1/1/1]                         |
| default               | 192:168:10::3                   | ebgp                  | S      | 64500      | established      | 0d:0h:22m:57s    | ipv6-unicast   | [1/1/1]                         |
| default               | 2001::2                         | evpn                  | S      | 65500      | established      | 0d:0h:22m:44s    | evpn           | [0/0/0]                         |
+-----------------------+---------------------------------+-----------------------+--------+------------+------------------+------------------+----------------+---------------------------------+
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Summary:
4 configured neighbors, 4 configured sessions are established, 0 disabled peers
0 dynamic peers
```

## Useful links

* [Network Developer Portal](https://network.developer.nokia.com/)
* [containerlab](https://containerlab.dev/)
* [gNMIc](https://gnmic.openconfig.net/)

### SR Linux
* [SR Linux documentation](https://documentation.nokia.com/srlinux/)
* [Learn SR Linux](https://learn.srlinux.dev/)
* [YANG Browser](https://yang.srlinux.dev/)
* [gNxI Browser](https://gnxi.srlinux.dev/)
* [Ansible Collection](https://learn.srlinux.dev/ansible/collection/)
