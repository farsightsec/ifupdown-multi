ifupdown-multi
==============

`ifupdown-multi` integrates support for multiple default gateways on independent
network connections into the Debian `ifupdown` network interface configuration
system. It adds new `multi_*` options to the `/etc/network/interface` file
format in order to more easily configure Linux's policy based routing.

The policy information used to configure each network interface using
`ifupdown-multi` is saved when `ifup` is run. This allows network interfaces
using `ifupdown-multi` to be brought up or down cleanly as needed.

Installation
------------

The `ifupdown-multi` Debian package should be used if possible.

Manual installation can be accomplished by running the following commands:

```
    # install -m 0755 ifupdown-multi.py /usr/local/lib/ifupdown-multi.py
    # ln -sf /usr/local/lib/ifupdown-multi.py /etc/network/if-up.d/ifupdown-multi
    # ln -sf /usr/local/lib/ifupdown-multi.py /etc/network/if-down.d/ifupdown-multi
```

`ifupdown-multi` is implemented in Python and requires the Python runtime to be
installed on the system and available during boot.

Configuration
-------------

See the [ifupdown-multi-interfaces(5)](man/ifupdown-multi-interfaces.5.rst)
manpage for details.

The following example shows a basic configuration with two network interfaces
attached to two Internet providers.

```
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
```
