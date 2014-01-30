""" Download from S3 bucket """

import os

from boto.s3.connection import S3Connection
from boto.s3.key import Key

def download_from_s3(packageprefix):
    """ Download rpm from S3 bucket """
    conn = S3Connection(anon=True)
    bucket = conn.get_bucket('rhuiqerpm')
    k = Key(bucket)
    rpm = ""
    for key in bucket.list():
        fname = key.name.encode('utf-8')
        if fname.startswith(packageprefix) and fname > rpm:
            rpm = fname
    if rpm != "":
        k.key = rpm
        if not os.path.exists("/root/" + rpm):
            with open("/root/" + rpm, "w") as rpmfile:
                rpmfile.write(k.get_contents_as_string())
    return rpm
