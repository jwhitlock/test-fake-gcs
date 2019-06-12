# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
FakeClient is a Google Cloud Storage client that talks to gc_fake_storage.
"""

from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
import requests
import urllib3


class FakeClient(storage.Client):
    """Client to bundle configuration needed for API requests to faked GCS."""

    def __init__(self, server_url, public_host, project="fake"):
        """Initialize a FakeClient."""

        self.server_url = server_url
        self.public_host = public_host
        self.init_fake_urls(server_url, public_host)

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

    _FAKED_URLS = None

    @classmethod
    def init_fake_urls(cls, server_url, public_host):
        """
        Update URL variables in classes and modules.

        This is ugly, but the Google Cloud Storage Python library doesn't
        support setting these as instance variables.
        """
        if cls._FAKED_URLS:
            # Check that we're not changing the value, which would affect other
            # intances of FakeClient
            assert cls._FAKED_URLS['server_url'] == server_url
            assert cls._FAKED_URLS['public_host'] == public_host
        else:
            cls._FAKED_URLS = {
                'server_url': server_url,
                'public_host': public_host,
                'old_api_base_url': storage._http.Connection.API_BASE_URL,
                'old_api_access_endpoint': storage.blob._API_ACCESS_ENDPOINT,
                'old_download_tmpl': storage.blob._DOWNLOAD_URL_TEMPLATE,
                'old_multipart_tmpl': storage.blob._MULTIPART_URL_TEMPLATE,
                'old_resumable_tmpl': storage.blob._RESUMABLE_URL_TEMPLATE,
            }

            storage._http.Connection.API_BASE_URL = server_url
            storage.blob._API_ACCESS_ENDPOINT = 'https://' + public_host
            storage.blob._DOWNLOAD_URL_TEMPLATE = (
                u"%s/download/storage/v1{path}?alt=media" % server_url)
            base_tmpl = (
                u"%s/upload/storage/v1{bucket_path}/o?uploadType="
                % server_url)
            storage.blob._MULTIPART_URL_TEMPLATE = base_tmpl + u"multipart"
            storage.blob._RESUMABLE_URL_TEMPLATE = base_tmpl + u"resumable"

    @classmethod
    def undo_fake_urls(cls):
        """Reset the faked URL variables in classes and modules."""
        if cls._FAKED_URLS is not None:
            storage._http.Connection.API_BASE_URL = (
                cls._FAKED_URLS['old_api_base_url'])
            storage.blob.Connection._API_ACCESS_ENDPOINT = (
                cls._FAKED_URLS['old_api_access_endpoint'])
            storage.blob._DOWNLOAD_URL_TEMPLATE = (
                cls._FAKED_URLS['old_download_tmpl'])
            storage.blob._MULTIPART_URL_TEMPLATE = (
                cls._FAKED_URLS['old_multipart_tmpl'])
            storage.blob._RESUMABLE_URL_TEMPLATE = (
                cls._FAKED_URLS['old_resumable_tmpl'])
            cls._FAKED_URLS = None

    def __enter__(self):
        """Allow FakeClient to be used as a context manager."""
        return self

    def __exit__(self, *args):
        """Undo setting fake URLs when exiting context."""
        self.undo_fake_urls()
