from os import environ
from redis import from_url as redis_from_url
from rq import Worker, Queue, Connection

REDIS_URL = environ.get('REDISTOGO_URL', 'redis://localhost:6379')
listen = ['high', 'default', 'low']
conn = redis_from_url(REDIS_URL)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
