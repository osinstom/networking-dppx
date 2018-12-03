#!/bin/bash

BMV2_COMMIT="1.12.0"
BMV2_LOGDIR="/var/log/bmv2/"

NUM_CORES=`grep -c ^processor /proc/cpuinfo`

function install_bmv2 {

    sudo apt-get install -y \
    automake \
    cmake \
    libjudy-dev \
    libgmp-dev \
    libpcap-dev \
    libboost-dev \
    libboost-test-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-filesystem-dev \
    libboost-thread-dev \
    libevent-dev \
    libtool \
    flex \
    bison \
    pkg-config \
    g++ \
    libssl-dev \
    libffi-dev

    # BMv2 deps (needed by PI)
    git clone https://github.com/p4lang/behavioral-model.git
    cd behavioral-model
    git checkout ${BMV2_COMMIT}
    # From bmv2's install_deps.sh, we can skip apt-get install.
    # Nanomsg is required by p4runtime, p4runtime is needed by BMv2...
    tmpdir=`mktemp -d -p .`
    cd ${tmpdir}
    bash ../travis/install-thrift.sh
    bash ../travis/install-nanomsg.sh
    sudo ldconfig
    bash ../travis/install-nnpy.sh
    cd ..
    sudo rm -rf $tmpdir
    cd ..

    # Bmv2
    cd behavioral-model
    ./autogen.sh
    ./configure --enable-debugger --with-thrift
    make -j${NUM_CORES}
    sudo make install
    sudo ldconfig
    # Simple_switch target
    cd targets/simple_switch
#    ./autogen.sh
#    ./configure
    make -j${NUM_CORES}
    sudo make install
    sudo ldconfig
    cd ..
    cd ..
    cd ..

}

function configure_bmv2_env {
    sudo mkdir ${BMV2_LOGDIR}
    cd $DEST
    mkdir p4-dep
    cd p4-dep
}

function unconfigure_bmv2_env {
    rm -rf $DEST/p4-dep/
    sudo rm -rf ${BMV2_LOGDIR}
}

function start_new_bmv2 {
    sudo simple_switch --pcap ${BMV2_LOGDIR} --log-file ${BMV2_LOGDIR}/output --log-level debug --no-p4 -- --enable-swap &
}

function stop_bmv2 {
    for pid in $(ps -ef | grep simple_switch | awk '{print $2}')
    do
        echo "Killing BMv2 process: $pid"
        sudo kill -9 $pid
    done
    for intf in $(sudo ifconfig | sed 's/[ \t].*//;/^\(lo\|\)$/d' | grep veth)
    do
       sudo ip link delete $intf
    done
}