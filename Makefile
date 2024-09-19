.PHONY: dev test

dev:
	source activate py311 && export DEBUG=True && python manage.py runserver

test:
	python manage.py test
