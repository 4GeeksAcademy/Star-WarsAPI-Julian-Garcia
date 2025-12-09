"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():
    try:
        query_results = User.query.all()
        if not query_results:
            return jsonify({"msg": "No hay usuarios encontrados"}), 400

        results = list(map(lambda item: item.serialize(), query_results))
        response_body = {
            "msg": "Los usuarios fueron extraidos",
            "results": results
        }

        return jsonify(response_body), 200

    except Exception as e:
        print(f"Error al obtener usuarios:{e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500


@app.route('/people', methods=['GET'])
def get_people():
    try:
        query_results = People.query.all()
        if not query_results:
            return jsonify({"msg": "No hay personajes encontrados"}), 400

        results = list(map(lambda item: item.serialize(), query_results))
        response_body = {
            "msg": "Los usuarios fueron extraidos",
            "results": results
        }

        return jsonify(response_body), 200

    except Exception as e:
        print(f"Error al obtener personajes:{e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500

# Get People by id


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_byid(people_id):
    try:
        query_results = People.query.filter_by(id=people_id).first()
        if not query_results:
            return jsonify({"msg": "Personaje no existe"}), 400

        response_body = {
            "msg": "Usuario encontrado",
            "results": query_results.serialize()
        }

        return jsonify(response_body), 200

    except Exception as e:
        print(f"Error al obtener personajes:{e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500

# Get Planets

@app.route('/planets', methods=['GET'])
def get_planets():
    try:
        query_results = Planets.query.all()
        if not query_results:
            return jsonify({"msg": "No hay planetas encontrados"}), 400

        results = list(map(lambda item: item.serialize(), query_results))
        response_body = {
            "msg": "Los planetas fueron extraidos",
            "results": results
        }

        return jsonify(response_body), 200

    except Exception as e:
        print(f"Error al obtener los planetas:{e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500
    
# Get Planets by ID 
    
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_byid(planet_id):
    try:
        query_results = Planets.query.filter_by(id=planet_id).first()
        if not query_results:
            return jsonify({"msg": "Planeta no existe"}), 400

        response_body = {
            "msg": "Planeta encontrado",
            "results": query_results.serialize()
        }

        return jsonify(response_body), 200

    except Exception as e:
        print(f"Error al obtener planetas:{e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
