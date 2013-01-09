#! /bin/bash -e

HOST=$1
shift
KEY=$1
shift
ISO=$1
shift
RPM1=$1
shift
OARGS=$@

# shared ssh options
SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityFile=$KEY"


usage() {
    echo "Usage: $0 <master hostname> <keyfile> <RHUI ISO> <rhui-testing-tools.rpm> [--coverage|--nostorage]"
    exit 1
}

if [ -z "$RPM1" ] || [ ! -f "$RPM1" ]; then
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
rcopy /root "$ISO" "$RPM1"

rexec yum install -q -y /root/`basename $RPM1`
rexec rhui-installer.py --iso /root/`basename $ISO` $OARGS
rexec easy_install pinocchio
rexec easy_install nose
