#! /usr/bin/python -tt

import argparse
import yaml
import os

argparser = argparse.ArgumentParser(description='Create RHUI install')
argparser.add_argument('--param', required=True,
                       help='parameter')
argparser.add_argument('--value', required=True,
                       help='value')
argparser.add_argument('--yamlfile',
                       default="/etc/rhui-testing.yaml", help='use specified YAML config file')
args = argparser.parse_args()

fd = open(args.yamlfile, 'r')
yamlconfig = yaml.load(fd)
fd.close()
if not 'Config' in yamlconfig.keys():
    yamlconfig['Config'] = {}
yamlconfig['Config'][args.param] = args.value
os.system("mv " + args.yamlfile + " " + args.yamlfile +".old")
fd = open(args.yamlfile, 'w')
fd.write(yaml.safe_dump(yamlconfig))
fd.close()
