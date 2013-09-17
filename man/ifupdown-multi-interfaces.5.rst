ifupdown-multi-interfaces
=========================
----------------------------------------------------------
ifupdown-multi extension for the interfaces(5) file format
----------------------------------------------------------

:Date:              17 September 2013
:Version:           0.1.0
:Manual section:    5
:Manual group:      File formats

DESCRIPTION
-----------

`/etc/network/interfaces` contains network interface information for the
**ifup**\(8) and **ifdown**\(8) commands. This manpage describes the
**ifupdown-multi** extensions to the the standard **interfaces**\(5) file
format.

The **ifupdown-multi** extensions to **ifupdown** integrate Linux's policy
routing based support for multiple default gateways on independent network
connections. These extensions can replace a typical shell script based approach
that directly invokes a sequence of **ip**\(8) commands for configuring
multiple uplinks with declarative syntax in the `/etc/network/interfaces` file.

**ifupdown-multi** records the policy information used to bring up each network
interface when **ifup**\(8) is run and removes the same policy routing
information when **ifdown**\(8) is run.

IFACE OPTIONS
-------------

The standard **address** and **netmask** options must be set for each
interface. The **gateway** option must *NOT* be set.

The new **multi_gateway** and **multi_table** options must be set to configure
policy routing with **ifupdown-multi**.

Additionally, the **multi_gateway_weight** and **multi_preferred_prefixes**
options can be specified in order to control optional policy routing features.

**multi_gateway** *address*
 Default gateway for this interface. (Required.)

**multi_table** *id*
 Table identifier. This must be a numeric value, and each interface must have a
 unique value. Recommended range: 1-1000. (Required.)

**multi_gateway_weight** *weight*
 Set this gateway's weight. This value is directly passed as the *weight*
 parameter to the *nexthop* part of an **ip-route**\(8) route object. Higher
 values indicate higher relative bandwidth or quality. (Optional.)

**multi_preferred_prefixes** *prefix* [*prefix*]...
 Prefer this connection for the given prefixes. This option configures the
 routing policy database using the **ip-rule**\(8) command to use this
 connection for the specified prefixes. (Optional.)

EXAMPLES
--------

The following example shows a basic configuration with two network interfaces.
*eth0* is on the 198.51.100.0/24 network, while *eth1* is on the 203.0.113.0/24
network. Each interface stanza has a "multi_gateway" option, as opposed to the
usual "gateway" option. Each interface stanza also needs a "multi_table" option,
whose parameter is a small, unique non-negative integer.  (This number will be
used internally to uniquely identify an interface-specific routing table.)

::

    auto eth0
    iface eth0 inet static
        address 198.51.100.123
        netmask 255.255.255.0
        multi_table 1
        multi_gateway 198.51.100.1

    auto eth1
    iface eth1 inet static
        address 203.0.113.234
        netmask 255.255.255.0
        multi_table 2
        multi_gateway 203.0.113.1

The following example shows a more complicated setup using optional
**ifupdown-multi** parameters. It is similar to the first example, but the
network connection on *eth0* is preferred for most connections, and several
network prefixes prefer to use one or the other network connection.

::

    auto eth0
    iface eth0 inet static
        address 198.51.100.123
        netmask 255.255.255.0
        multi_table 1
        multi_gateway 198.51.100.1
        multi_gateway_weight 5
        multi_preferred_prefixes 10.0.0.0/8

    auto eth1
    iface eth1 inet static
        address 203.0.113.234
        netmask 255.255.255.0
        multi_table 2
        multi_gateway 203.0.113.1
        multi_gateway_weight 1
        multi_preferred_prefixes 172.16.0.0/12 192.168.0.0/16

FILES
-----

`/etc/network/interfaces`
 System-wide network interface configuration. See **interfaces**\(5).

`/var/run/network/ifupdown-multi.*`
 State information used by **ifupdown-multi**.

SEE ALSO
--------

**interfaces**\(5), **ifup**\(8), **ip**\(8), **ip-route**\(8), **ip-rule**\(8).

Linux Advanced Routing & Traffic Control HOWTO -- Chapter 4: Rules.
    http://www.tldp.org/HOWTO/Adv-Routing-HOWTO/lartc.rpdb.html
