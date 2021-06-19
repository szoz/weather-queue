from flask import Flask, Response, request, jsonify, abort
from flasgger import Swagger
from redis import Redis

app = Flask(__name__)
swag = Swagger(app, template_file='docs/template.yml', config={"openapi": "3.0.2", "specs_route": "/docs/"}, merge=True)

rdb = Redis()


@app.route('/')
def get_root() -> Response:
    """Return simple greeting."""
    return jsonify({'hello': 'user'})


@app.route('/redis')
def redis_find_keys() -> Response:
    """Return list of all Redis keys with given pattern."""
    pattern = request.args.get('pattern', '*')
    keys = [key.decode('utf-8') for key in rdb.keys(pattern)]
    return jsonify(keys)


@app.route('/redis/<string:key>')
def redis_get_value(key: str) -> Response:
    """Return value of given Redis key."""
    value = rdb.get(key)
    if not value:
        return abort(404)

    return jsonify({key: value.decode('utf-8')})
