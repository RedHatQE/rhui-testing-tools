#! /bin/bash -e

SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

HOST=$1
KEY=$2
ISO=$3

usage() {
    echo "Usage: $0 <master hostname> <keyfile> <RHUI ISO>"
    exit 1
}

if [ -z "$ISO" ] || [ ! -f "$ISO" ]; then
    usage
fi

if [ ! -f "$KEY" ]; then
    usage
fi

scp $SSH_OPT -i "$KEY" "$ISO" *.py "root@$HOST:/root/"
ssh $SSH_OPT -i "$KEY" "root@$HOST" "yum install -y python-paramiko; python rhui_installer.py --iso /root/`basename $ISO` > /root/log 2>&1"
