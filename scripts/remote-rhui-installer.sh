#! /bin/bash -e

usage() {
    echo "Usage: `basename $0` -h | <master hostname> <keyfile> <RHUI ISO>"
    echo "        <rhui-testing-tools rpm> [--coverage|--nostorage]"
}


[ $# -eq 0 ] && {
    usage
    exit 1
}

while getopts ":h" option ; do
    case $option in
        h) usage; exit 0 ;;
    esac
done

shift $(( ${OPTIND} - 1 ))


HOST=${1:?hostname not specified}
KEY=${2:?ssh key not specified}
ISO=${3:?RHUI ISO not specified}
RPM=${4:?rhui-testing-tools rpm not specified}
shift 4
OARGS=$@

# shared ssh options
SSH_OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityFile=$KEY"

if [ ! -f "$ISO" ]; then
    echo not a file: $ISO
    usage
    exit 1
fi

if [ ! -f "$KEY" ]; then
    echo not a file: $KEY
    usage
    exit 1
fi

if [ ! -f "$RPM" ] ; then
    echo not a file: $RPM
    usage
    exit 1
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

rexec yum install -q -y /root/`basename $RPM`
rexec rhui-testing-dependencies.py
rexec rhui-installer.py --iso /root/`basename $ISO` $OARGS
