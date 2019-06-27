# networking-p4 #

This repository contains source code of new Service Plugin for OpenStack Neutron.

## What is networking-p4? ##

The networking-p4 is a new service plugin (extension) for OpenStack Neutron implementing Data Plane Programmability Exposure (DPPx) framework. 
The purpose of DPPx framework is to allow users to install dedicated data plane modules (packet processing functions) on-the-fly. 

DPPx is based on P4 and BMv2. Current implementation makes use of Glance store and Service Function Chaining (SFC) plugin of Neutron.

Note that DPPx is an ongoing research work. This version of networking-p4 is a research prototype and should be used only for experiments and research purposes. Current version has several limitations in context of performance and functionality. 
 
## How to install? ##

The DPPx plugin was tested on DevStack (Pike) installation. In order to install DevStack follow steps on https://docs.openstack.org/devstack/latest/. The `local.conf` file to configure the DevStack to use the DPPx plugin is provided in the `devstack/` directory. Make sure you use the Pike branch of DevStack before installation.

## How to use? ##



## Contacts ##

Tomek Osiński < tomasz.osinski2@orange.com >
