.PHONY: dev test

dev:
	source activate py311 && export DEBUG=True && python manage.py runserver

test:
	source activate py311 && export DEBUG=True && python manage.py test
