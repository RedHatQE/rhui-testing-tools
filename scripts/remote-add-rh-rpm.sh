#! /bin/bash -e

SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

HOST=$1
KEY=$2
RPM=$3

usage() {
    echo "Usage: $0 <main hostname> <keyfile>  <RH rpm for testing>"
    exit 1
}

if [ -z "$RPM" ] || [ ! -f "$RPM" ]; then
    usage
fi

if [ ! -f "$KEY" ]; then
    usage
fi

scp $SSH_OPT -r -i "$KEY" "$RPM" "root@$HOST:/var/lib/rhui-testing-tools/"
ssh $SSH_OPT -i "$KEY" "root@$HOST" "rhui-add-testing-parameter.py --param rhrpm --value /var/lib/rhui-testing-tools/`basename $RPM`"
