#!/usr/bin/env python

import glob
import logging
import os
import subprocess
import sys

process_name = os.path.basename(sys.argv[0])

required_keys = (
    'MODE',
    'ADDRFAM',
    'IFACE',
    'IF_ADDRESS',
    'IF_NETMASK',
    'IF_MULTI_TABLE',
    'IF_MULTI_GATEWAY',
)

additional_keys = (
    'IF_MULTI_GATEWAY_WEIGHT',
    'IF_MULTI_PREFERRED_PREFIXES',
)

fname_prefix = '/var/run/network/ifupdown-multi.'
fname_nexthop = fname_prefix + '%(IFACE)s.nexthop.%(ADDRFAM)s'
fname_rules = fname_prefix + '%(IFACE)s.rules'

glob_nexthop = fname_prefix + '*.nexthop.%(ADDRFAM)s'

priority_magic_preferred = 25357
priority_magic = 31047

def run(cmd):
    logging.debug('running command %r', cmd)
    return subprocess.call(cmd, shell=True)

class ifupdownMulti:
    def __init__(self, env):
        self.cfg = {}
        for key in required_keys:
            if env.has_key(key):
                self.cfg[key] = env[key]
            else:
                raise Exception, 'missing environment variable %s' % key
        for key in additional_keys:
            if env.has_key(key):
                self.cfg[key] = env[key]
        if not self.cfg['MODE'] in ('start', 'stop'):
            raise Exception, 'unknown ifupdown mode %s' % self.cfg['MODE']
        if self.cfg['ADDRFAM'] == 'inet':
            self.cfg['ip'] = 'ip'
        elif self.cfg['ADDRFAM'] == 'inet6':
            self.cfg['ip'] = 'ip -6'
        table_id = int(self.cfg['IF_MULTI_TABLE'])
        self.cfg['PRIORITY_PREFERRED'] = priority_magic_preferred + table_id
        self.cfg['PRIORITY'] = priority_magic + table_id
        self.fname_nexthop = fname_nexthop % self.cfg
        self.fname_rules = fname_rules % self.cfg
        self.glob_nexthop = glob_nexthop % self.cfg

    def dispatch(self):
        if self.cfg['ADDRFAM'] in ('inet', 'inet6'):
            if self.cfg['MODE'] == 'start':
                self.start()
            elif self.cfg['MODE'] == 'stop':
                self.stop()

    def flush_route_cache(self):
        run('%(ip)s route flush cache' % self.cfg)

    def start_rule(self, rule):
        rule = rule % self.cfg
        with open(self.fname_rules, 'a') as w:
            w.write(rule + '\n')
        run('%s rule add %s' % (self.cfg['ip'], rule))

    def start_route(self, route):
        route = route % self.cfg
        run('%s route replace %s' % (self.cfg['ip'], route))

    def start_gateway(self):
        self.start_route('default via %(IF_MULTI_GATEWAY)s dev %(IFACE)s table %(IF_MULTI_TABLE)s proto static')
        nexthop = 'nexthop via %(IF_MULTI_GATEWAY)s dev %(IFACE)s' % self.cfg
        weight = self.cfg.get('IF_MULTI_GATEWAY_WEIGHT')
        if weight:
            nexthop += ' weight ' + weight
        with open(self.fname_nexthop, 'w') as w:
            w.write(nexthop)
            w.write('\n')

    def restart_nexthops(self):
        nexthops = set()
        for fname in glob.glob(self.glob_nexthop):
            for line in open(fname):
                nexthops.add(line.strip())
        if nexthops:
            nexthops = sorted(list(nexthops))
            cmd = self.cfg['ip'] + ' route replace default scope global ' + ' '.join(nexthops)
            run(cmd)
        else:
            run('%(ip)s route delete default' % self.cfg)

    def start(self):
        self.start_rule('from %(IF_ADDRESS)s table %(IF_MULTI_TABLE)s priority %(PRIORITY)s')
        self.start_rule('to %(IF_ADDRESS)s table %(IF_MULTI_TABLE)s priority %(PRIORITY)s')
        preferred_prefixes = self.cfg.get('IF_MULTI_PREFERRED_PREFIXES')
        if preferred_prefixes:
            for prefix in preferred_prefixes.split():
                self.cfg['PREFIX'] = prefix
                self.start_rule('to %(PREFIX)s table %(IF_MULTI_TABLE)s priority %(PRIORITY_PREFERRED)s')
        self.start_gateway()
        self.restart_nexthops()
        self.flush_route_cache()

    def stop_rules(self):
        if os.path.exists(self.fname_rules):
            for line in open(self.fname_rules):
                rule = line.strip()
                run(self.cfg['ip'] + ' rule delete ' + rule)
            try:
                logging.debug('unlinking %s', self.fname_rules)
                os.unlink(self.fname_rules)
            except OSError:
                pass

    def stop(self):
        run('%(ip)s route flush table %(IF_MULTI_TABLE)s' % self.cfg)
        try:
            logging.debug('unlinking %s', self.fname_nexthop)
            os.unlink(self.fname_nexthop)
        except OSError:
            pass
        self.restart_nexthops()
        self.stop_rules()
        self.flush_route_cache()

def main():
    if not 'IF_MULTI_TABLE' in os.environ:
        sys.exit(0)
    if not os.getenv('MODE') in ('start', 'stop'):
        sys.exit(0)

    if os.getenv('VERBOSITY') == '1':
        level = logging.DEBUG
    else:
        level = logging.CRITICAL
    logging.basicConfig(format=process_name+': %(levelname)s: %(message)s', level=level)

    ifupdownMulti(os.environ).dispatch()

if __name__ == '__main__':
    main()