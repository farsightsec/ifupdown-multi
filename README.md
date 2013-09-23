ifupdown-multi
==============

`ifupdown-multi` integrates support for multiple default gateways on independent
network connections into the Debian `ifupdown` network interface configuration
system. It adds new `multi_*` options to the `/etc/network/interfaces` file
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

Caveats
-------

+ Do not specify a prefix in `multi_gateway_prefixes` that overlaps one of the
subnets directly attached to the host.

+ IPv6 is supported, but it is implemented in a slightly different way than
IPv4. The `multi_gateway_weight` option is not supported for IPv6 gateways.
The first IPv6 gateway configured is used instead, unless a specific prefix is
configured to use a particular gateway using the `multi_gateway_prefixes`
option.

+ `ifup` disables stateless address autoconfiguration when the `static` method
is used with the `inet6` address family, however it does *not* disable the
learning of routes from IPv6 router advertisements. It is recommended to place
an executable script in the `/etc/network/if-pre-up.d` directory containing
something like the following contents:

```
#!/bin/sh
if test "$IFACE" = "--all"; then
    exit 0
fi
if test "$METHOD" != "static"; then
    exit 0
fi
IFACE="$(echo $IFACE | cut -f1 -d:)"
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/autoconf
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/accept_dad
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/accept_ra
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/accept_ra_defrtr
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/accept_ra_pinfo
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/accept_ra_rtr_pref
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/accept_redirects
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/accept_source_route
echo 0 > /proc/sys/net/ipv6/conf/$IFACE/dad_transmits
```
