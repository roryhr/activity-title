.PHONY: dev test

dev:
	export DEBUG=True && python manage.py runserver

test:
	python manage.py test
