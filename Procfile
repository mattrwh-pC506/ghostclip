web: cd project && python manage.py migrate && gunicorn project.wsgi
worker: cd project && python manage.py rqworker high default low
