#! /usr/bin/python -tt

import os
import subprocess

from rhuilib.s3 import download_from_s3

for rpm in ["python-patchwork-", "python-pinocchio-"]:
    rpmfile = download_from_s3(rpm)
    if rpmfile != "":
        ret = subprocess.call(["yum", "-y", "install", rpmfile])
        if ret != 0:
            sys.stderr.write("Failed to install %s rpm!" % rpm)
    else:
        sys.stderr.write("Can't install %s from S3!" % rpm)
