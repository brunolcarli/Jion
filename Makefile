run:
	python manage.py runserver 0.0.0.0:6500 --settings=jion.settings.development

migrate:
	python manage.py makemigrations --settings=jion.settings.development
	python manage.py migrate --settings=jion.settings.development
