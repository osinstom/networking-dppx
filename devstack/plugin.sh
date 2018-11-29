#!/usr/bin/env bash
# plugin.sh - DevStack plugin.sh dispatch script template

LIBDIR=$DEST/networking-p4/devstack/lib

source $LIBDIR/bmv2.sh

function networking_p4_install {
    setup_develop $NETWORKING_P4_DIR
}

function _networking_p4_install_server {
    _neutron_service_plugin_class_add $NEUTRON_P4_PLUGIN
    iniset $NEUTRON_CONF DEFAULT service_plugins $Q_SERVICE_PLUGIN_CLASSES
    iniadd $NEUTRON_CONF p4 drivers $NEUTRON_PDP_DRIVERS
}

function _networking_p4_install_agent {

    echo_summary "Installing networking-p4 agent"

    _install_p4_dependencies

    source $NEUTRON_DIR/devstack/lib/l2_agent
    plugin_agent_add_l2_agent_extension p4
    configure_l2_agent

    start_new_bmv2
}

function _install_p4_dependencies {
    echo_summary "Installing P4 dependencies"
    configure_bmv2_env
    install_bmv2
}

function _uninstall_p4_dependencies {
    stop_bmv2
    unconfigure_bmv2_env
}

function networking_p4_configure_common {
    if is_service_enabled q-svc; then
        _networking_p4_install_server
    fi
    if is_service_enabled q-agt; then
        _networking_p4_install_agent
    fi
}


if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
    # Set up system services
    echo_summary "Configuring system services Template"

elif [[ "$1" == "stack" && "$2" == "install" ]]; then
      # Perform installation of service source
      echo_summary "Installing networking-p4 service"
      networking_p4_install

elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
      # Configure after the other layer 1 and 2 services have been configured
      echo_summary "Configuring Template"p
      networking_p4_configure_common

elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
      # Initialize and start the template service
      echo_summary "Initializing Template"
fi

if [[ "$1" == "unstack" ]]; then
    # Shut down services
    _uninstall_p4_dependencies
fi

if [[ "$1" == "clean" ]]; then
    # Remove state and transient data
    # Remember clean.sh first calls unstack.sh
    # no-op
    :
fi
