#!/usr/bin/env python3
"""Test of Google Cloud Storage library against gc-fake-storage"""

from google.cloud import storage
from google.auth.credentials import AnonymousCredentials
import requests
import urllib3


BASE_URL = "https://127.0.0.1:4443"

storage._http.Connection.API_BASE_URL = BASE_URL # override the BASE_URL in the client library with the mock server
storage.blob._DOWNLOAD_URL_TEMPLATE = (u"%s/download/storage/v1{path}?alt=media" % BASE_URL)
storage.blob._BASE_UPLOAD_TEMPLATE = (u"%s/upload/storage/v1{bucket_path}/o?uploadType=" % BASE_URL)
storage.blob._MULTIPART_URL_TEMPLATE = storage.blob._BASE_UPLOAD_TEMPLATE + u"multipart"
storage.blob._RESUMABLE_URL_TEMPLATE = storage.blob._BASE_UPLOAD_TEMPLATE + u"resumable"

my_http = requests.Session()
my_http.verify = False  # disable SSL validation
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable https warnings for https insecure certs

client = storage.Client(credentials=AnonymousCredentials(), project="test", _http=my_http)

def list_buckets():
    for bucket in client.list_buckets():
        print('Bucket "%s":' % bucket.name)
        for blob in bucket.list_blobs():
            print('- %s' % blob.name)

print("FILES AT START")
print("--------------")
list_buckets()
print()

# Can't create a bucket - issue w/ anon creds?
bucket_name = 'storage'
test_file = 'test.txt'

# Can't create a bucket - issue with anonymous creds? emulation limitation?
# bucket.client.create_bucket(bucket_name)

# Load a bucket
bucket = client.get_bucket(bucket_name)

# Create a file in the bucket
blob = storage.blob.Blob(test_file, bucket=bucket)
blob.upload_from_string("""\
This is a test file.

It has a few lines.
""")

print("FILES AFTER UPLOAD")
print("------------------")
list_buckets()
print()

# List the file contents
print("CONTENTS OF TEST FILE")
print("---------------------")
blob = bucket.get_blob(test_file)
contents = blob.download_as_string()
print(contents.decode('utf8'))
print("---------------------")
print()

# Delete the file
blob = bucket.get_blob(test_file)
blob.delete()

print("FILES AFTER DELETION")
print("--------------------")
list_buckets()
print()
