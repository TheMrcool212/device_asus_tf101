# Copyright (C) 2012 The Android Open Source Project
# Copyright (C) 2013 Christopher N. Hesse <raymanfx@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""AOSP releasetools for TF101"""

import common
import os
import sys
import subprocess

OPTIONS = common.OPTIONS
OPTIONS.backuptool = False

OUT_DIR = os.getenv('OUT')

if OUT_DIR:
    TARGET_DIR = OUT_DIR
else:
    print 'TF101: OUT_DIR not set, hardcoding path..'
    TARGET_DIR = os.path.abspath(os.path.join(LOCAL_DIR, '../../../out/target/product/tf101/'))

def MakeBlob():
    blobpath = os.path.join(TARGET_DIR, "boot.blob")
    cmdblob = ["blobpack_tf", blobpath, "LNX", os.path.join(TARGET_DIR, "boot.img")]
    pblob = common.Run(cmdblob, stdout=subprocess.PIPE)
    print "TF101: LNX blob created successfully"
    pblob.communicate()
    assert pblob.returncode == 0, "blobpack of %s image failed" % (os.path.basename(TARGET_DIR),)
    return open(blobpath).read()
    
def WriteBlob(info, blob):
    common.ZipWriteStr(info.output_zip, "boot.blob", blob)
    fstab = info.info_dict["fstab"]
    info.script.Print("Writing boot blob...")
    info.script.AppendExtra('package_extract_file("boot.blob","' + fstab["/staging"].device + '");')
    
def FullOTA_InstallEnd(info):
    WriteBlob(info, MakeBlob())

def IncrementalOTA_InstallEnd(info):
    write = False
    try:
        source = info.source_zip.read("boot.blob")
        target = MakeBlob()
        write = not (target == source)
    except KeyError:
        write = True
    if write:
        print "TF101: boot blob changed, writing the new one"
        WriteBlob(info, target)
    else:
        print "TF101: boot blob unchanged, skipping"
