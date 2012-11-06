#! /bin/bash -e

SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

HOST=$1
KEY=$2
CERT=$3

usage() {
    echo "Usage: $0 <master hostname> <keyfile>  <RH cert for testing>"
    exit 1
}

if [ -z "$CERT" ] || [ ! -f "$CERT" ]; then
    usage
fi

if [ ! -f "$KEY" ]; then
    usage
fi

scp $SSH_OPT -r -i "$KEY" "$CERT" "root@$HOST:/var/lib/rhui-testing-tools/"
ssh $SSH_OPT -i "$KEY" "root@$HOST" "rhui-add-testing-parameter.py --param rhcert --value /var/lib/rhui-testing-tools/`basename $CERT`"
