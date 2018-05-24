web: cd project && python manage.py migrate && gunicorn project.wsgi
rqueue: cd project && python manage.py rqworker high default low
