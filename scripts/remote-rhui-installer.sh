#! /bin/bash -e

HOST=$1
KEY=$2
ISO=$3
RPM1=$4
RPM2=$5

# shared ssh options
SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityFile=$KEY"


usage() {
    echo "Usage: $0 <master hostname> <keyfile> <RHUI ISO> <rhui-testing-tools.rpm> <python-patchwork.rpm>"
    exit 1
}

if [ -z "$RPM2" ] || [ ! -f "$RPM2" ]; then
    usage
fi

if [ ! -f "$RPM1" ]; then
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
rcopy /root "$ISO" "$RPM1" "$RPM2"

rexec yum install -q -y /root/`basename $RPM1` /root/`basename $RPM2`
rexec rhui-installer.py --iso /root/`basename $ISO`
rexec easy_install pinocchio
rexec easy_install nose
