#!/usr/bin/env python3
"""Test of Google Cloud Storage library against gc-fake-storage"""

import os
import uuid

from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
import requests
import urllib3


class FakeClient(storage.Client):
    """Client to bundle configuration needed for API requests to faked GCS."""

    def __init__(self, server_url, project="fake"):
        """Initialize a FakeClient."""

        self.server_url = server_url

        # Create a session that is OK talking over insecure HTTPS
        # - Doesn't validate SSL, doesn't warn about insecure certs
        weak_http = requests.Session()
        weak_http.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Initialize the base class
        super().__init__(
            project=project,
            credentials=AnonymousCredentials(),
            _http=weak_http)

        class Connection(storage._http.Connection):
            """A connection to our fake Google Cloud Storage."""
            API_BASE_URL = server_url

        # Swap out the Connection class
        self._base_connection = None
        self._connection = Connection(self)


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

    storage.blob._DOWNLOAD_URL_TEMPLATE = (
        u"%s/download/storage/v1{path}?alt=media" % SERVER_URL)
    storage.blob._BASE_UPLOAD_TEMPLATE = (
        u"%s/upload/storage/v1{bucket_path}/o?uploadType=" % SERVER_URL)
    storage.blob._MULTIPART_URL_TEMPLATE = (
        storage.blob._BASE_UPLOAD_TEMPLATE + u"multipart")
    storage.blob._RESUMABLE_URL_TEMPLATE = (
        storage.blob._BASE_UPLOAD_TEMPLATE + u"resumable")

    client = FakeClient(SERVER_URL)
    run_tests(client)
