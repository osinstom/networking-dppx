Prerequisites
-------------

Before you install and configure the p4 service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``networking_p4`` database:

     .. code-block:: none

        CREATE DATABASE networking_p4;

   * Grant proper access to the ``networking_p4`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON networking_p4.* TO 'networking_p4'@'localhost' \
          IDENTIFIED BY 'NETWORKING_P4_DBPASS';
        GRANT ALL PRIVILEGES ON networking_p4.* TO 'networking_p4'@'%' \
          IDENTIFIED BY 'NETWORKING_P4_DBPASS';

     Replace ``NETWORKING_P4_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``networking_p4`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt networking_p4

   * Add the ``admin`` role to the ``networking_p4`` user:

     .. code-block:: console

        $ openstack role add --project service --user networking_p4 admin

   * Create the networking_p4 service entities:

     .. code-block:: console

        $ openstack service create --name networking_p4 --description "p4" p4

#. Create the p4 service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        p4 public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        p4 internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        p4 admin http://controller:XXXX/vY/%\(tenant_id\)s
