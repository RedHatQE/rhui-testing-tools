#! /usr/bin/python -tt
# this script converts a Rhui testing tools inventory to Ansible inventory
import argparse
import json
import yaml
import sys

class InstanceError(Exception):
    pass

class InventoryError(Exception):
    pass

class Instance(object):
    def __init__(self, data):
        required_fields = ('Name', 'id', 'private_hostname', 'private_ip',
                           'public_hostname', 'public_ip', 'role')
        if not isinstance(data, dict):
            raise InstanceError('not a dict: %s' % data)
        for field in required_fields:
            if not field in data:
                raise InstanceError('%s not in %s' % (field, data))

        self.__dict__.update(data)
        self.data = data
        self.host = data

    def __repr__(self):
        return 'Instance(%r)' % self.data



class Inventory(object):
    def __init__(self, data):
        if not isinstance(data, dict):
            raise InventoryError('not a dict: %s' % data)
        if 'Instances' not in data:
            raise InventoryError('Instances not in %s' % data)
        if not isinstance(data['Instances'], list):
            raise InventoryError('not a list: %s' % data['Instances'])

        self.data = data
        self.instances = map(lambda x: Instance(x), data['Instances'])

        self.instances_by_id = {}
        self.instances_by_public_ip = {}
        self.instances_by_private_ip = {}
        for instance in self.instances:
            self.instances_by_id[instance.id] = instance
            self.instances_by_public_ip[instance.public_ip] = instance
            self.instances_by_private_ip[instance.private_ip] = instance

    def __repr__(self):
        return 'Inventory(%r)' % self._data

    def __getitem__(self, query):
        if query in self.instances_by_id:
            return self.instances_by_id[query]
        if query in self.instances_by_private_ip:
            return self.instances_by_private_ip[query]
        if query in self.instances_by_public_ip:
            return self.instances_by_public_ip[query]
        if isinstance(query, int):
            return self.instances[query]
        else:
            try:
                # could be an index
                return self.instances[int(query)]
            except ValueError:
                # wasn't an int after all
                pass
        raise KeyError("Can't locate instance by: %s" % query)

    def __len__(self):
        return len(self.instances)

    def get_groups(self, public=False):
        groups = {}
        # in addition to roles, RHUI group is provided, too
        # all CDSes and RHUAs should be present in it
        groups['RHUI'] = []
        for instance in self.instances:
            if not instance.role in groups:
                groups[instance.role] = []
            if public:
                host = instance.public_ip
            else:
                host = instance.private_ip
            if instance.role in ('RHUA, CDS'):
                groups['RHUI'].append(host)
            groups[instance.role].append(host)
        return groups


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Provide a Rhui inventory for Ansible'
    )
    argparser.add_argument('-l', '--list', default=False, action='store_true',
                          help='list all hosts')
    argparser.add_argument('-H', '--host', default=None,
                          help='get host details')
    argparser.add_argument('-p', '--with-public', default=False,
                          action='store_true',
                          help='give host details rather with public ip')
    argparser.add_argument('-i', '--with-inventory',
                          dest='inventory',
                          default='/etc/rhui-testing.yaml',
                          help='provide custom inventory file')

    args = argparser.parse_args()

    try:
        with open(args.inventory) as fd:
            inventory = Inventory(yaml.load(fd))
    except (InstanceError, InventoryError, IOError) as e:
        print >> sys.stderr, 'Got %s processing %s' % (e, args.inventory)
        exit(1)

    if args.list:
        print json.dumps(inventory.get_groups(args.with_public))
        exit(0)

    if args.host:
        try:
            print json.dumps(inventory[args.host].host)
            exit(0)
        except (KeyError, IndexError) as e:
            print >> sys.stderr, 'Got %s. Wrong host: %s' % (e, args.host)
            exit(1)


