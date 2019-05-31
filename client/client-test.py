#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Test of Google Cloud Storage library against gc-fake-storage"""

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


def run_tests(client, bucket_name=None, object_name=None):
    """Test a GCS server.

    :arg:client: A client authorized to create buckets
    :arg:bucket_name: The name of a test bucket to create
    :arg:object_name: The name of a test object to create
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


if __name__ == "__main__":
    SERVER_URL = os.environ.get('SERVER_URL', '')
    assert SERVER_URL, 'Set SERVER_URL in the environment'
    print("Connecting to GCS server at %s" % SERVER_URL)

    # FakeClient changes some module variables
    old_value = storage.blob._DOWNLOAD_URL_TEMPLATE
    print("Before using FakeClient, DOWNLOAD_URL_TEMPLATE=%r" % old_value)

    with FakeClient(SERVER_URL) as client:
        new_value = storage.blob._DOWNLOAD_URL_TEMPLATE
        print(
            "After initializing FakeClient, DOWNLOAD_URL_TEMPLATE=%r"
            % new_value)
        assert new_value != old_value
        run_tests(client)

    # FakeClient resets module variables when used as context
    returned_value = storage.blob._DOWNLOAD_URL_TEMPLATE
    print(
        "After closing FakeClient, DOWNLOAD_URL_TEMPLATE=%r"
        % storage.blob._DOWNLOAD_URL_TEMPLATE)
    assert returned_value == old_value
