# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

.PHONY: help
help: default

.PHONY: default
default:
	@echo "Usage: make RULE"
	@echo ""
	@echo "Main rules"
	@echo "  test - Run the tests in containers"
	@echo "  test-run - Run the tests, and keep the server running"
	@echo "  test-quick - Run the tests, without building or safety checks"
	@echo "  lint - Run the linter on client files"
	@echo ""
	@echo "Other rules"
	@echo "  build - Build the server and client containers"
	@echo "  build-client - Build the client container"
	@echo "  build-server - Build the server container"
	@echo "  clean - Stop and delete containers and delete files"
	@echo "  clean-storage - Delete uploaded files"
	@echo "  clean-docker - Stop and delete containers"
	@echo "  stop - Stop the containers"

.PHONY: clean-docker
clean-docker:
	docker-compose down


.PHONY: clean-storage
clean-storage:
	find server/storage/ ! \( -name .gitignore \) -type f -delete
	find server/storage/ -type d -depth 1 -delete

.PHONY: clean
clean: clean-docker clean-storage

.PHONY: build-server
build-server:
	docker-compose build server

.PHONY: build-client
build-client:
	docker-compose build client

.PHONY: build
build: build-server build-client

.PHONY: test-quick
test-quick:
	-docker-compose run --rm client
	docker-compose logs server

.PHONY: stop
stop:
	docker-compose stop

.PHONY: test-run
test-run: clean build test-quick

.PHONY: test
test: test-run stop

.PHONY: lint
lint: build-client
	docker-compose run --rm client flake8 . && echo "OK"
