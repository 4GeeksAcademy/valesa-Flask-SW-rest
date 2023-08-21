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
from models import db, User, Planet, People, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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



# endpoints de "USER"
@app.route('/user', methods=['GET'])
def get_user():
    users = User.query.all()
    users_serialized = list(map(lambda x: x.serialize(), users))

    return jsonify({"msg": 'Realizado con éxito', "users": users_serialized})

@app.route('/user/favorites', methods=['GET'])
def get_favorites():
    favorites = User.query.all()
    favorites_serialized = list(map(lambda x: x.serialize(), favorites))

    return jsonify({"msg": 'Realizado con éxito', "favorites": favorites_serialized})



# endpoints de "PLANET"
@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_serialized = list(map(lambda x: x.serialize(), planets))

    return jsonify({"msg": 'Realizado con éxito', "planets": planets_serialized})

@app.route("/planet/<int:planet_id>", methods=['GET'])
def get_id_planet(planet_id):
    single_planet = Planet.query.get(planet_id)
    if single_planet is None:
        raise APIException(f" No se encontró el siguiente Id {planet_id}", status_code=400)
    response_body = {
        "msg": "GET /planet_id ",
        "planet_id": planet_id,
        "planet_info": single_planet.serialize()
    }
    return jsonify(response_body), 200

@app.route('/planet', methods=['POST'])
def post_planet():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Envia info al body, esta vacio", status_code=400)
    print(body)
    if "id" not in body:
        raise APIException("Coloca un ID", status_code=400)
    if "name" not in body:
        raise APIException("Escribe un nombre", status_code=400)
    if "diameter" not in body:
        raise APIException(
            "Escribe un diametro", status_code=400)
    if "gravity" not in body:
        raise APIException(
            "Escribe una gravedad", status_code=400)
    if "climate" not in body:
        raise APIException("Escribe un clima", status_code=400)

    new_planet = Planet(id=body['id'], name=body['name'], diameter=body['diameter'],
                        gravity=body['gravity'], climate=body['climate'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "POST exitoso", "new_planet_info": new_planet.serialize()})

@app.route("/planet", methods=['PUT'])
def modify_planet():
    body = request.get_json(silent=True)
    if "id" not in body:
        raise APIException("Coloca un ID", status_code=400)
    if "name" not in body:
        raise APIException("Escribe un nombre", status_code=400)
    if "diameter" not in body:
        raise APIException(
            "Escribe un diametro", status_code=400)
    if "gravity" not in body:
        raise APIException(
            "Escribe una gravedad", status_code=400)
    if "climate" not in body:
        raise APIException("Escribe un clima", status_code=400)
    single_planet = Planet.query.get(body['id'])
    single_planet.name = body['name']
    single_planet.diameter = body['diameter']
    single_planet.gravity = body['gravity']
    single_planet.climate = body['climate']
    db.session.commit()
    return jsonify({"msg": "PUT exitoso"})

@app.route("/planet/<int:planet_id>", methods=['DELETE'])
def delete_planet(planet_id):
    single_planet = Planet.query.get(planet_id)
    if single_planet is None:
        raise APIException("No existe este planeta", status_code=400)

    db.session.delete(single_planet)
    db.session.commit()

    return jsonify({"msg": "DELETE exitoso"})



# endpoints de "PEOPLE"
@app.route("/people", methods=['GET'])
def get_people():
    people = People.query.all()
    people_serialized = list(map(lambda x: x.serialize(), people))

    return jsonify({"msg": 'Get exitoso', "people": people_serialized}), 200

@app.route("/people/<int:people_id>", methods=['GET'])
def get_people_id(people_id):
    single_people = People.query.get(people_id)
    if single_people is None:
        raise APIException(f"No existe {people_id}", status_code=400)
    response_body = {
        "msg": "GET /people_id ",
        "people_id": people_id,
        "people_info": single_people.serialize()
    }
    return jsonify(response_body), 200

@app.route('/people', methods=['POST'])
def post_people():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Debes enviar info en el body", status_code=400)
    print(body)
    if "id" not in body:
        raise APIException("Escribe un ID", status_code=400)
    if "name" not in body:
        raise APIException("Escribe un nombre", status_code=400)
    if "height" not in body:
        raise APIException("Escribe una altura", status_code=400)
    if "mass" not in body:
        raise APIException("Escribe un peso", status_code=400)
    if "eyes_color" not in body:
        raise APIException("Escribe un color de ojos", status_code=400)

    new_people = People(id=body['id'], name=body['name'], height=body['height'],
                        mass=body['mass'], eyes_color=body['eyes_color'])
    db.session.add(new_people)
    db.session.commit()
    return jsonify({"msg": "POST exitoso", "new_people_info": new_people.serialize()})

@app.route("/people", methods=['PUT'])
def modify_people():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Crea un body", status_code=400)
    if "id" not in body:
        raise APIException(
            "Ingresa el id nuevo", status_code=400)
    if "name" not in body:
        raise APIException("ingresa el nombre nuevo", status_code=400)
    if "height" not in body:
        raise APIException(
            "Ingresa la nueva altura", status_code=400)
    if "mass" not in body:
        raise APIException("Ingresa la nueva masa", status_code=400)
    if "eyes_color" not in body:
        raise APIException("Ingresa el nuevo color de ojos")
    single_people = People.query.get(body['id'])
    single_people.name = body['name']
    single_people.height= body['height']
    single_people.mass = body['mass']
    single_people.eyes_color = body['eyes_color']
    db.session.commit()
    return jsonify({"msg": "PUT exitoso"})

@app.route("/people/<int:people_id>", methods=['DELETE'])
def delete_people(people_id):
    single_people = People.query.get(people_id)
    if single_people is None:
        raise APIException("No existe el personaje", status_code=400)

    db.session.delete(single_people)
    db.session.commit()

    return jsonify({"msg": "DELETE exitoso"})



# endpoints de "FAVORITES"
@app.route("/favorite/planet/<int:planet_id>", methods=['POST'])
def add_new_favorite_planet(planet_id):
    current_user = 1
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet is not None:
        favorite = Favorite.query.filter_by(name=planet.name).first()
        if favorite:
            return jsonify({"ok": True, "msg": "Existe el planeta favorito"}), 200
        body = {
            "name": planet.name,
            "user_id": current_user
        }
        new_favorite = Favorite.create(body)
        if new_favorite is not None:
            return jsonify(new_favorite.serialize()), 201
        return jsonify({"msg": "Hubo un Error"}), 500
    return jsonify({
        "msg": "No se encontro en favoritos el planeta"
    }), 404

@app.route("/favorite/planet/<int:planet_id>", methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user = 1
    planet = Planet.query.filter_by(id=planet_id).first()

    if planet is not None:
        favorite = Favorite.query.filter_by(
            name=planet.name, user_id=current_user).first()

        if not favorite:
            return jsonify({"ok": False, "msg": "El planeta en favoritos no existe"}), 404

        try:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"ok": True, "msg": "Se elimino el favorito con exito"}), 200
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"msg": "Hubo un Error"}), 500
    return jsonify({
        "msg": "No se encontro el planeta"
    }), 404

@app.route("/favorite/people/<int:people_id>", methods=['POST'])
def add_new_favorite_people(people_id):
    current_user = 1
    people = People.query.filter_by(id=people_id).first()
    if people is not None:
        favorite = Favorite.query.filter_by(name=people.name).first()
        if favorite:
            return jsonify({"ok": True, "msg": "Existe el personaje favorito"}), 200
        body = {
            "name": people.name,
            "user_id": current_user
        }
        new_favorite = Favorite.create(body)
        if new_favorite is not None:
            return jsonify(new_favorite.serialize()), 201
        return jsonify({"msg": "Hubo un error"}), 500
    return jsonify({
        "msg": "No se encontro en favoritos el personaje"
    }), 404

@app.route("/favorite/people/<int:people_id>", methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user = 1
    people = People.query.filter_by(id=people_id).first()

    if people is not None:
        favorite = Favorite.query.filter_by(
            name=people.name, user_id=current_user).first()

        if not favorite:
            return jsonify({"ok": False, "msg": "El personaje en favoritos no existe"}), 404

        try:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"ok": True, "msg": "Se elimino el favorito con exito"}), 200
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"msg": "Hubo un error"}), 500
    return jsonify({
        "msg": "No se encontro el personaje"
    }), 404



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
