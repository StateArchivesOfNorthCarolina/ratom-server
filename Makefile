PROJECT_NAME = ratom_api
STATIC_DIR = ./$(PROJECT_NAME)/static

default: lint test

test:
	# Run all tests and report coverage
	# Requires coverage
	python manage.py makemigrations --dry-run | grep 'No changes detected' || \
		(echo 'There are changes which require migrations.' && exit 1)
	pytest

build-base:
	DOCKER_BUILDKIT=1 docker build --target base --pull -t govsanc/ratom-server:base .

build-test:
	DOCKER_BUILDKIT=1 docker build --target test-base -t govsanc/ratom-server:test-base .

ci-pre-commit:
	docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm app pre-commit run --all -v

ci-test:
	docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm app pytest

build-deploy:
	DOCKER_BUILDKIT=1 docker build --target deploy -t govsanc/ratom-server .

lint-py:
	# Check for Python formatting issues
	# Requires flake8
	$(WORKON_HOME)/ratom_api/bin/flake8 .

lint: lint-py

# Generate a random string of desired length
generate-secret: length = 32
generate-secret:
	@strings /dev/urandom | grep -o '[[:alnum:]]' | head -n $(length) | tr -d '\n'; echo

conf/keys/%.pub.ssh:
	# Generate SSH deploy key for a given environment
	ssh-keygen -t rsa -b 4096 -f $*.priv -C "$*@${PROJECT_NAME}"
	@mv $*.priv.pub $@

staging-deploy-key: conf/keys/staging.pub.ssh

production-deploy-key: conf/keys/production.pub.ssh

# Translation helpers
makemessages:
	# Extract English messages from our source code
	python manage.py makemessages --ignore 'conf/*' --ignore 'docs/*' --ignore 'requirements/*' \
		--no-location --no-obsolete -l en

compilemessages:
	# Compile PO files into the MO files that Django will use at runtime
	python manage.py compilemessages

pushmessages:
	# Upload the latest English PO file to Transifex
	tx push -s

pullmessages:
	# Pull the latest translated PO files from Transifex
	tx pull -af

setup:
	virtualenv -p `which python3.7` $(WORKON_HOME)/ratom_api
	$(WORKON_HOME)/ratom_api/bin/pip install -U pip wheel
	$(WORKON_HOME)/ratom_api/bin/pip install -Ur requirements/dev.txt
	$(WORKON_HOME)/ratom_api/bin/pip freeze
	cp ratom_api/settings/local.example.py ratom_api/settings/local.py
	echo "DJANGO_SETTINGS_MODULE=ratom_api.settings.local" > .env
	createdb -E UTF-8 ratom_api
	$(WORKON_HOME)/ratom_api/bin/python manage.py migrate
	if [ -e project.travis.yml ] ; then mv project.travis.yml .travis.yml; fi
	@echo
	@echo "The ratom_api project is now setup on your machine."
	@echo "Run the following commands to activate the virtual environment and run the"
	@echo "development server:"
	@echo
	@echo "	workon ratom_api"

update:
	$(WORKON_HOME)/ratom_api/bin/pip install -U -r requirements/dev.txt

# Build documentation
docs:
	cd docs && make html

.PHONY: default test lint lint-py generate-secret makemessages \
		pushmessages pullmessages compilemessages docs

.PRECIOUS: conf/keys/%.pub.ssh
