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
CURRENT_USER_ID = 1

@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


# ======================
# PEOPLE
# ======================

@app.route("/people", methods=["GET"])
def get_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_people_by_id(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "Personaje no existe"}), 404
    return jsonify(person.serialize()), 200


# ======================
# PLANETS
# ======================

@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planets.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet_by_id(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planeta no existe"}), 404
    return jsonify(planet.serialize()), 200


# ======================
# FAVORITES
# ======================

@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    favorites = Favorite.query.filter_by(id_user=CURRENT_USER_ID).all()

    results = []
    for fav in favorites:
        if fav.People:
            results.append({
                "type": "people",
                "data": fav.People.serialize()
            })
        if fav.Planets:
            results.append({
                "type": "planet",
                "data": fav.Planets.serialize()
            })

    return jsonify(results), 200


# ----- ADD FAVORITE PLANET -----

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "El planeta no existe"}), 404

    exists = Favorite.query.filter_by(
        id_user=CURRENT_USER_ID,
        id_planets=planet_id
    ).first()

    if exists:
        return jsonify({"msg": "El planeta ya está en favoritos"}), 409

    fav = Favorite(
        id_user=CURRENT_USER_ID,
        id_planets=planet_id,
        id_people=None
    )

    db.session.add(fav)
    db.session.commit()

    return jsonify({"msg": "Planeta agregado a favoritos"}), 200


# ----- ADD FAVORITE PEOPLE -----

@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "El personaje no existe"}), 404

    exists = Favorite.query.filter_by(
        id_user=CURRENT_USER_ID,
        id_people=people_id
    ).first()

    if exists:
        return jsonify({"msg": "El personaje ya está en favoritos"}), 409

    fav = Favorite(
        id_user=CURRENT_USER_ID,
        id_people=people_id,
        id_planets=None
    )

    db.session.add(fav)
    db.session.commit()

    return jsonify({"msg": "Personaje agregado a favoritos"}), 200


# ----- DELETE FAVORITE PLANET -----

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    fav = Favorite.query.filter_by(
        id_user=CURRENT_USER_ID,
        id_planets=planet_id
    ).first()

    if not fav:
        return jsonify({"msg": "Favorito no existe"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "Planeta eliminado de favoritos"}), 200


# ----- DELETE FAVORITE PEOPLE -----

@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    fav = Favorite.query.filter_by(
        id_user=CURRENT_USER_ID,
        id_people=people_id
    ).first()

    if not fav:
        return jsonify({"msg": "Favorito no existe"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "Personaje eliminado de favoritos"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
