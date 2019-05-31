Tests for fake Google Cloud Storage
===================================

[fsouza/fake-gcs-server] is a Go library providing a fake Google Cloud Storage
API server, intended for testing. [teone/gc-fake-storage] dockerizes it as a
server, available at [matteoscandolo/gc-fake-storage].
[jwhitlock/gc-fake-storage] is a fork that keeps up-to-date with
`fake-gcs-server`. This project demonstrates using the Docker image with the
[Python library for Google Cloud Storage].

Running
-------

To try it, run ``make test``.

Notes
-----

The ``server/init_buckets`` folder is mounted in the server container at
``/data``. The folder is used to create buckets and items in those buckets.
The files are copied to the ``/storage`` folder in the container.

[Python library for Google Cloud Storage]: https://github.com/googleapis/google-cloud-python/tree/master/storage
[jwhitlock/gc-fake-storage]: https://github.com/jwhitlock/gc-fake-storage
[fsouza/fake-gcs-server]: https://github.com/fsouza/fake-gcs-server/
[matteoscandolo/gc-fake-storage]: https://hub.docker.com/r/matteoscandolo/gc-fake-storage
[teone/gc-fake-storage]: https://github.com/teone/gc-fake-storage
