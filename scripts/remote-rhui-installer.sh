#! /bin/bash -e

HOST=$1
KEY=$2
ISO=$3
RPM=$4

# shared ssh options
SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityFile=$KEY"


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

function rexec() {
    # root remotelly execute stuff via ssh
    ssh $SSH_OPT "root@$HOST" "${@:?no command specified}"
}

function rcopy() {
    # root copy remotelly stuff via scp
    # $1:       destination folder
    # $@ - $1:  sources
    local destination=$1
    shift
    scp $SSH_OPT -r ${@:?no source specified} root@$HOST:${destination}
}

# copy the stuff
rcopy /root "$ISO" "$RPM"

rexec yum install -y /root/`basename $RPM`
rexec rhui-installer.py --iso /root/`basename $ISO`
rexec easy_install pinocchio
