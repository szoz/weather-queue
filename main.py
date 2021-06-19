from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swag = Swagger(app, template_file='docs/template.yml', config={"openapi": "3.0.2", "specs_route": "/docs/"}, merge=True)


@app.route('/')
def get_root():
    """Return simple greeting."""
    return jsonify({'hello': 'user'})
