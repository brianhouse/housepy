#!/usr/bin/env python

""" This is not for Python 3 """

import mimetypes, os, sys, time, subprocess, datetime, boto, urlparse, math
import lib.S3 as S3lib
from cStringIO import StringIO
from multiprocessing import Pool
from housepy import config, log


def upload(source, dest=None, num_processes=2, split=50, force=True, reduced_redundancy=False, verbose=False):
    if dest is None:
        dest = source
    log.info("s3.upload %s to %s/%s..." % (source, config['aws']['bucket'], dest))
    src = open(source)
    s3 = boto.connect_s3(config['aws']['access_key_id'], config['aws']['secret_access_key'])
    bucket = s3.lookup(config['aws']['bucket'])
    key = bucket.get_key(dest)
    if key is not None:
        if not force:
            raise ValueError("--> '%s' already exists" % dest)
    part_size = max(5 * 1024 * 1024, 1024 * 1024 * split)
    src.seek(0,2)
    size = src.tell()
    num_parts = int(math.ceil(size / part_size))
    if size < 5 * 1024 * 1024:
        src.seek(0)
        t1 = time.time()
        k = boto.s3.key.Key(bucket, dest)
        k.set_contents_from_file(src)
        t2 = time.time() - t1
        s = size/1024./1024.
        log.info("--> finished uploading %0.2fM in %0.2fs (%0.2fMbps)" % (s, t2, s/t2))
        return
    mpu = bucket.initiate_multipart_upload(dest, reduced_redundancy=reduced_redundancy)
    log.info("--> initialized upload: %s" % mpu.id)
    def gen_args(num_parts, fold_last):
        for i in range(num_parts+1):
            part_start = part_size*i
            if i == (num_parts-1) and fold_last is True:
                yield (bucket.name, mpu.id, src.name, i, part_start, part_size*2)
                break
            else:
                yield (bucket.name, mpu.id, src.name, i, part_start, part_size)
    fold_last = ((size % part_size) < 5*1024*1024)
    try:
        pool = Pool(processes=num_processes)
        t1 = time.time()
        pool.map_async(do_part_upload, gen_args(num_parts, fold_last)).get(9999999)
        t2 = time.time() - t1
        s = size/1024./1024.
        src.close()
        mpu.complete_upload()
        log.info("--> finished uploading %0.2fM in %0.2fs (%0.2fMbps)" % (s, t2, s/t2))
        return True
    except Exception as err:
        log.error("--> encountered an error, canceling upload")        
        log.error(log.exc(err))
        mpu.cancel_upload()
        return False
        


def do_part_upload(args):
    """
    Upload a part of a MultiPartUpload

    Open the target file and read in a chunk. Since we can't pickle
    S3Connection or MultiPartUpload objects, we have to reconnect and lookup
    the MPU object with each part upload.

    :type args: tuple of (string, string, string, int, int, int)
    :param args: The actual arguments of this method. Due to lameness of
                 multiprocessing, we have to extract these outside of the
                 function definition.

                 The arguments are: S3 Bucket name, MultiPartUpload id, file
                 name, the part number, part offset, part size
    """

    bucket_name, mpu_id, fname, i, start, size = args
    s3 = boto.connect_s3(config['aws']['access_key_id'], config['aws']['secret_access_key'])
    bucket = s3.lookup(bucket_name)
    mpu = None
    for mp in bucket.list_multipart_uploads():
        if mp.id == mpu_id:
            mpu = mp
            break
    if mpu is None:
        raise Exception("--> could not find MultiPartUpload %s" % mpu_id)
    fp = open(fname, 'rb')
    fp.seek(start)
    data = fp.read(size)
    fp.close()
    if not data:
        raise Exception("--> unexpectedly tried to read an empty chunk")
    def progress(x,y):
        log.info("Part %d: %0.2f%%" % (i+1, 1.*x/y))
    t1 = time.time()
    mpu.upload_part_from_file(StringIO(data), i+1, cb=progress)
    t2 = time.time() - t1
    s = len(data)/1024./1024.
    log.info("--> uploaded part %s (%0.2fM) in %0.2fs at %0.2fMbps" % (i+1, s, t2, s/t2))


def delete(path):
    log.info("s3.delete")        
    conn = S3lib.AWSAuthConnection(config['aws']['access_key_id'], config['aws']['secret_access_key'])
    log.info("--> deleting %s/%s" % (config['aws']['bucket'], path))        
    try:
        response = conn.delete(config['aws']['bucket'], path)
    except Exception as e:
        log.error("--> failed: %s" % log.exc(e))
        return False
    log.info("--> %s" % response.message)
    return True
    
def list_contents():
    log.info("s3.list")
    connection = boto.connect_s3(config['aws']['access_key_id'], config['aws']['secret_access_key'])
    log.info("--> listing %s" % (config['aws']['bucket']))        
    try:
        bucket = connection.get_bucket(config['aws']['bucket'])
        contents = [key.name.encode('utf-8') for key in bucket.list()]
    except Exception as e:
        log.error("--> failed: %s" % log.exc(e))
        return False
    log.info("--> %s" % contents)
    return contents

def download(path, destination=None):
    if destination is None:
        destination = path
    log.info("s3.download")        
    connection = boto.connect_s3(config['aws']['access_key_id'], config['aws']['secret_access_key'])
    log.info("--> downloading %s/%s" % (config['aws']['bucket'], path))        
    try:
        bucket = connection.get_bucket(config['aws']['bucket'])
        key = bucket.get_key(path)    
        key.get_contents_to_filename(destination)
    except Exception as e:
        log.error("--> failed: %s" % log.exc(e))
        return False
    log.info("--> successfully wrote %s" % destination)
    return True
    
