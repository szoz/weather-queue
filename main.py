from flask import Flask, Response, request, jsonify, abort
from flasgger import Swagger
from rq import Queue

from worker import conn
from utils import validate_cities
from collect import get_group_weather

app = Flask(__name__)
swag = Swagger(app, template_file='docs/template.yml', config={"openapi": "3.0.2", "specs_route": "/docs/"}, merge=True)

q = Queue(connection=conn)


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


@app.route('/jobs', methods=['POST'])
def create_job() -> Response:
    """Create new job - collecting weather data for given cities list."""
    cities = request.args.get('cities', '')
    if not validate_cities(cities):
        return abort(422)

    job = q.enqueue_call(get_group_weather, args=(cities.split(','),))

    return jsonify({'job_id': job.get_id()})


@app.route('/jobs', methods=['GET'])
def read_all_jobs() -> Response:
    """Return all jobs ids grouped by job status."""
    payload = {'started': q.started_job_registry.get_job_ids(),
               'deferred': q.deferred_job_registry.get_job_ids(),
               'finished': q.finished_job_registry.get_job_ids(),
               'failed': q.failed_job_registry.get_job_ids(),
               'scheduled': q.scheduled_job_registry.get_job_ids()}

    return jsonify(payload)


@app.route('/jobs/<string:job_id>', methods=['GET'])
def read_job(job_id) -> Response:
    """Return job details based on given job id."""
    job = q.fetch_job(job_id)
    if not job:
        return abort(404)

    job_details = {key: value for key, value in job.to_dict().items()
                   if type(value) != bytes}

    return jsonify(job_details)
