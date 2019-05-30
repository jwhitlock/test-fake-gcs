Tests for fake Google Cloud Storage
===================================

[fsouza/fake-gcs-server] is a Go library providing a fake Google Cloud Storage
API server, intended for testing. [teone/gc-fake-storage] dockerizes it as a
server, available at [matteoscandolo/gc-fake-storage]. This project
demonstrates using the Docker image with the
[Python library for Google Cloud Storage].

Running
-------

To try it, run ``./run_test.sh``.

Notes
-----

The ``server/init_buckets`` folder is mounted in the server container at
``/data``. The folder is used to create buckets and items in those buckets. I
was unable to create buckets using the normal GCS library calls
(``405 Method Not Allowed`` on a ``POST``), so this is required to create the
initial buckets.

The files are copied to the ``/storage`` folder in the container. In 0.1.0 of
the Docker image, this folder is created on startup, by the process that
copies files from ``/data``. If you omit the ``/data`` mount, then some GCS
operations fail with a 404.

[fsouza/fake-gcs-server]: https://github.com/fsouza/fake-gcs-server/
[teone/gc-fake-storage]: https://github.com/teone/gc-fake-storage
[matteoscandolo/gc-fake-storage]: https://hub.docker.com/r/matteoscandolo/gc-fake-storage
[Python library for Google Cloud Storage]: https://github.com/googleapis/google-cloud-python/tree/master/storage
