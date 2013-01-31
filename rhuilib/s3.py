import os
import subprocess

from boto.s3.connection import S3Connection
from boto.s3.key import Key

def download_from_s3(packageprefix):
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
            fd = open("/root/" + rpm, "w")
            fd.write(k.get_contents_as_string())
            fd.close()
    return rpm
