# Welcome to the EVPN Workshop at NANOG 92
This README is your starting point into the hands on section.

Pre-requisite: A laptop with SSH client

If you need help, please raise your hand and a Nokia team member will be happy to assist.

## Lab Environment

A Nokia team member will provide you with a card that contains:
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
![image](lab-topology.jpg)

## NOS (Network Operating System)

Both leafs and Spine nodes will be running Nokia [SRLinux](https://www.nokia.com/networks/ip-networks/service-router-linux-NOS/).

## Deploying the lab

After logging into the VM (using the credentials on your card), use the below command to clone this repo to your VM.

```
git clone 
```

Verify that this git repo files are now available on your VM.

```
ls -lrt
```

To deploy the lab, run the following:

```
sudo clab deploy -t 
```

[Containerlab](https://containerlab.dev/) will deploy the lab and display a table with the list of nodes and their IPs.

To display current deployed labs at any time, use:

```
sudo clab inspect --all
```

## Connecting to the devices

Find the nodename or IP address of the device and then use SSH.
Username: `admin`
Password: Refer to the card

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

Check the startup config files to see how interfaces and IP addresses are configured in SR Linux.

### IPv4 Link Addressing

![image](lab-ipv4.jpg)

### IPv6 Link Addressing

![image](lab-ipv4.jpg)

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
