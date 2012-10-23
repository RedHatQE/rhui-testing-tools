#! /bin/bash -e

SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

HOST=$1
KEY=$2
ISO=$3
RPM=$4

usage() {
    echo "Usage: $0 <master hostname> <keyfile> <RHUI ISO> <rhui-testing-tools.rpm>"
    exit 1
}

if [ -z "$RPM" ] || [ ! -f "$RPM" ]; then
    usage
fi

if [ ! -f "$ISO" ]; then
    usage
fi

if [ ! -f "$KEY" ]; then
    usage
fi

scp $SSH_OPT -r -i "$KEY" "$ISO" "$RPM" "root@$HOST:/root/"
ssh $SSH_OPT -i "$KEY" "root@$HOST" "yum install -y /root/`basename $RPM`; rhui-installer.py --iso /root/`basename $ISO`"
