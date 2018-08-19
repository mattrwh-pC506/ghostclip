import os
from urllib.parse import urlparse
from redis import Redis
from rq import use_connection, get_failed_queue
from django.core.management.base import BaseCommand

redis_url = os.getenv('REDISTOGO_URL')

class Command(BaseCommand):
    help = 'Clears RQ redis failed jobs queue'

    def handle(self, *args, **options):
                if redis_url:
            parsed_url = urlparse(redis_url)
            hostname = parsed_url.hostname
            password = parsed_url.password
            port = parsed_url.port
            conn = Redis(hostname, port, password=password)
            fq = get_failed_queue(connection=conn)
            if fq.count > 0: fq.empty()
