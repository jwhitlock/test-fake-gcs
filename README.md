Tests for fake Google Cloud Storage
===================================

[fsouza/fake-gcs-server] is a Go library providing a fake Google Cloud Storage
(GCS) API server, intended for testing. [teone/gc-fake-storage] dockerizes it
as a server, available at [matteoscandolo/gc-fake-storage].
[jwhitlock/gc-fake-storage] is a fork that keeps up-to-date with
`fake-gcs-server`.

This project demonstrates using the Docker image with the
[Python library for Google Cloud Storage], with customizations in a
derived ``FakeClient``.

Running
-------
To try it, run ``make test``. This will:

* Build a server container from the ``test`` branch of ``jwhitlock/gc-fake-storage``
* Build a client container from the ``client`` folder
* Run a series of commands using a modified Google Cloud Storage client to:
  - Create a bucket
  - List the contents of all buckets
  - Upload a text file
  - Download the text file
  - Delete the text file
* Shut down the client and server

Notes
-----
The Python Google Cloud Storage client is not written to use URLs other than
the official GCS URLs. It reads several URLs from class and module variables,
and doesn't provide a clean mechanism for changing them in derived classes or
instances.

To change the API URLs to the fake GCS server, the class and module variables
are updated when initialing a ``FakeClient``. This would affect other users
of the Python GCS libraries. The ``FakeClient`` can be initialized as a
context manager, which will undo the changes when exiting the context.

The ``server/init_buckets`` folder is mounted in the server container at
``/data``. The folder is used to create buckets and items in those buckets.
The files are copied to the ``/storage`` folder in the container.

Deleting buckets is not (yet) supported by ``fsouza/fake-gcs-server``.

[Python library for Google Cloud Storage]: https://github.com/googleapis/google-cloud-python/tree/master/storage
[jwhitlock/gc-fake-storage]: https://github.com/jwhitlock/gc-fake-storage
[fsouza/fake-gcs-server]: https://github.com/fsouza/fake-gcs-server/
[matteoscandolo/gc-fake-storage]: https://hub.docker.com/r/matteoscandolo/gc-fake-storage
[teone/gc-fake-storage]: https://github.com/teone/gc-fake-storage
