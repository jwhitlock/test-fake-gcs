#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Test of Google Cloud Storage library against gc-fake-storage"""

import hashlib
import os
import uuid

from fake_client import FakeClient
from google.cloud import storage


def list_buckets(client, header=None):
    """Print contents of buckets."""
    if header:
        print(header)
        print('-' * len(header))
    for bucket in client.list_buckets():
        print('Bucket "%s":' % bucket.name)
        for blob in bucket.list_blobs():
            print('- %s' % blob.name)
    if header:
        print()


def test_files(rootDir):
    """Return files to upload in the test directory."""
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            full_path = os.path.join(dirName, fname)

            # Create a object path relative to the bucket
            obj_path = full_path.replace(rootDir, '')
            while obj_path.startswith('/'):
                obj_path = obj_path[1:]

            if obj_path == '.gitignore':
                continue

            yield obj_path, full_path


def run_tests(client, bucket_name=None, object_name=None, test_file_dir=None):
    """Test a GCS server.

    :arg:client: A client authorized to create buckets
    :arg:bucket_name: The name of a test bucket to create
    :arg:object_name: The name of a test object to create
    :arg:test_file_dir: The path to a directory of test files to upload
    """

    bucket_name = bucket_name or "test_%s" % uuid.uuid4()
    object_name = object_name or "test_%s.txt" % uuid.uuid4()

    list_buckets(client, 'FILES AT START')

    # Create the bucket
    bucket = client.create_bucket(bucket_name)

    # Create a file in the bucket
    blob = bucket.blob(object_name)
    blob.upload_from_string("This is a test file.\n\nIt has a few lines.\n")
    list_buckets(client, 'FILES AFTER UPLOAD')

    # List the file contents
    print("CONTENTS OF TEST FILE")
    print("---------------------")
    blob = bucket.get_blob(object_name)
    contents = blob.download_as_string()
    print(contents.decode('utf8'))
    print("---------------------")
    print()

    # Delete the file
    blob.delete()
    list_buckets(client, 'FILES AFTER DELETION')

    # Upload any test files
    if test_file_dir:
        print("UPLOADING TEST FILES")
        print("--------------------")
        signatures = {}
        for obj_name, path in test_files(test_file_dir):
            # Calculate the hash, size
            sha1 = hashlib.sha1()
            size = 0
            with open(path, 'rb') as test_file:
                while True:
                    data = test_file.read(1024)
                    if not data:
                        break
                    size += len(data)
                    sha1.update(data)
                signatures[obj_name] = (size, sha1.hexdigest())

            # Upload the file
            print("Uploading %s as %s" % (path, obj_name))
            blob = bucket.blob(obj_name)
            blob.upload_from_filename(path)
        print()
        list_buckets(client,"AFTER UPLOADING TEST FILES")

        # Verify files
        for obj_name, sig in signatures.items():
            blob = bucket.get_blob(obj_name)
            contents = blob.download_as_string()
            sha1 = hashlib.sha1(contents)
            size = len(contents)
            sig_out = (size, sha1.hexdigest())
            if sig == sig_out:
                print("%s: OK (size=%s, sha1=%s)" %
                      (obj_name, size, sig_out[1]))
            else:
                print("%s: Not OK! (size=%s -> %s, sha1=%s -> %s)" %
                      (obj_name, sig[0], size, sig[1], sig_out[1]))


if __name__ == "__main__":
    SERVER_URL = os.environ.get('SERVER_URL', '')
    assert SERVER_URL, 'Set SERVER_URL in the environment'
    print("Connecting to GCS server at %s" % SERVER_URL)

    TEST_FILE_DIR = os.environ.get('TEST_FILE_DIR', '')

    # FakeClient changes some module variables
    old_value = storage.blob._DOWNLOAD_URL_TEMPLATE
    print("Before using FakeClient, DOWNLOAD_URL_TEMPLATE=%r" % old_value)

    with FakeClient(SERVER_URL) as client:
        new_value = storage.blob._DOWNLOAD_URL_TEMPLATE
        print(
            "After initializing FakeClient, DOWNLOAD_URL_TEMPLATE=%r"
            % new_value)
        assert new_value != old_value
        run_tests(client, test_file_dir=TEST_FILE_DIR)

    # FakeClient resets module variables when used as context
    returned_value = storage.blob._DOWNLOAD_URL_TEMPLATE
    print(
        "After closing FakeClient, DOWNLOAD_URL_TEMPLATE=%r"
        % storage.blob._DOWNLOAD_URL_TEMPLATE)
    assert returned_value == old_value
