from flask import Flask, Response, request, jsonify, abort
from flasgger import Swagger
# from redis import Redis
from rq import Queue

from worker import conn
from utils import validate_cities
from collect import get_group_weather

app = Flask(__name__)
swag = Swagger(app, template_file='docs/template.yml', config={"openapi": "3.0.2", "specs_route": "/docs/"}, merge=True)

q = Queue(connection=conn)
# rdb = Redis()


@app.route('/')
def get_root() -> Response:
    """Return simple greeting."""
    return jsonify({'hello': 'user'})


@app.route('/redis')
def redis_find_keys() -> Response:
    """Return list of all Redis keys with given pattern."""
    pattern = request.args.get('pattern', '*')
    keys = [key.decode('utf-8') for key in conn.keys(pattern)]
    return jsonify(keys)


@app.route('/redis/<string:key>')
def redis_get_value(key: str) -> Response:
    """Return value of given Redis key."""
    value = conn.get(key)
    if not value:
        return abort(404)

    return jsonify({key: value.decode('utf-8')})


@app.route('/tasks', methods=['POST'])
def add_weather_tasks() -> Response:
    """Creates new task with collecting weather data for given cities list."""  # TODO add GET method support
    cities = request.args.get('cities', '')
    if not validate_cities(cities):
        return abort(422)

    job = q.enqueue_call(get_group_weather, args=(cities.split(','), ))

    return jsonify({'task_id': job.get_id()})
