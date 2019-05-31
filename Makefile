# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

.PHONY: help
help: default

.PHONY: default
default:
	@echo "Usage: make RULE"
	@echo ""
	@ecgo "Main rules"
	@echo "  test - Run the tests in containers"
	@echo "  test-quick - Run the tests, without building or safety checks"
	@echo "  lint - Run the linter on client files"
	@echo ""
	@ecgo "Other rules"
	@echo "  build - Build the server and client containers"
	@echo "  build-client - Build the client container"
	@echo "  build-server - Build the server container"
	@echo "  clean - Stop and delete containers"
	@echo "  stop - Stop the containers"

.PHONY: clean
clean:
	docker-compose down

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
	docker-compose run --rm client

.PHONY: stop
stop:
	docker-compose stop

.PHONY: test
test: clean build test-quick stop

.PHONY: lint
lint: build-client
	docker-compose run --rm client flake8 . && echo "OK"
