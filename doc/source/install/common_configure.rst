2. Edit the ``/etc/networking_p4/networking_p4.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://networking_p4:NETWORKING_P4_DBPASS@controller/networking_p4
