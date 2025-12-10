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
            "msg": "Los personajes fueron extraidos",
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

# Crear usuario

@app.route('/user', methods=['POST'])
def create_user():

    try:
    # revisa la data
        data= request.get_json()
    #si no hay data
        if not data:
            return jsonify({"msg": "no se proporcionaron datos"}), 400
    #la informacion que se va a postear  
        email=data.get("email")
        password=data.get("password")
        is_active=data.get("is_active", False)

    #si el correo es repetido
        existing_user= User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"msg": "Usuario ya registrado"}), 409

    #crear nuevo usuario
        new_user=User(
            email=email,
            password=password,
            is_active=is_active
        )
    #mandarlo a la tabla de modelado
        db.session.add(new_user)
        db.session.commit()

        return jsonify(new_user.serialize()), 201

    except Exception as e:
            print(f"Error al obtener usuarios:{e}")
            return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500
    
# Favorites

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    try:
        # Get favorites for this specific user
        favorites = Favorite.query.filter_by(id_user=user_id).all()

        if not favorites:
            return jsonify({"msg": "El usuario no tiene favoritos"}), 404

        results = []
        for fav in favorites:
            results.append({
                "id": fav.id,
                "id_user": fav.id_user,
                "id_people": fav.id_people,
                "id_planets": fav.id_planets
            })

        return jsonify({
            "msg": "Favoritos obtenidos correctamente",
            "results": results
        }), 200

    except Exception as e:
        print(f"Error al obtener favoritos: {e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500

#favorite planet

@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    try:
        # Verify planet exists
        planet = Planets.query.get(planet_id)
        if not planet:
            return jsonify({"msg": "El planeta no existe"}), 404

        # Check if already favorited
        existing_favorite = Favorite.query.filter_by(
            id_user=user_id,
            id_planets=planet_id
        ).first()

        if existing_favorite:
            return jsonify({"msg": "El planeta ya está en favoritos"}), 409

        # Create new favorite
        new_favorite = Favorite(
            id_user=user_id,
            id_planets=planet_id,
            id_people=None
        )

        db.session.add(new_favorite)
        db.session.commit()

        return jsonify({
            "msg": "Planeta agregado a favoritos",
            "favorite": {
                "id": new_favorite.id,
                "id_user": new_favorite.id_user,
                "id_planets": new_favorite.id_planets,
                "id_people": new_favorite.id_people
            }
        }), 201

    except Exception as e:
        print(f"Error al agregar favorito: {e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500
    
#favorite people

@app.route('/users/<int:user_id>/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(user_id, people_id):
    try:
        # Verify character exists
        person = People.query.get(people_id)
        if not person:
            return jsonify({"msg": "El personaje no existe"}), 404

        # Check if already favorited
        existing_favorite = Favorite.query.filter_by(
            id_user=user_id,
            id_people=people_id
        ).first()

        if existing_favorite:
            return jsonify({"msg": "El personaje ya está en favoritos"}), 409

        # Create new favorite
        new_favorite = Favorite(
            id_user=user_id,
            id_people=people_id,
            id_planets=None
        )

        db.session.add(new_favorite)
        db.session.commit()

        return jsonify({
            "msg": "Personaje agregado a favoritos",
            "favorite": {
                "id": new_favorite.id,
                "id_user": new_favorite.id_user,
                "id_people": new_favorite.id_people,
                "id_planets": new_favorite.id_planets
            }
        }), 201

    except Exception as e:
        print(f"Error al agregar favorito: {e}")
        return jsonify({"msg": "Internal Server Error", "error": str(e)}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
