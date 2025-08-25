
import os
from datetime import date
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet

app = Flask(__name__)
app.url_map.strict_slashes = False


db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///starwars.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


CURRENT_USER_ID = 1


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.before_request
def seed_data():
    if not User.query.first():
        db.session.add_all([
            User(id=1, user="carlita03", first_name="Carla", last_name="Londoño", mail="carlita03@gmail.com", password="hashed"),
            User(id=2, user="josefacedo10", first_name="Josefina", last_name="Caicedo", mail="josefacedo10@gmail.com", password="hashed"),
            User(id=3, user="infandro14", first_name="Pedro", last_name="Infante", mail="infandro14@gmail.com", password="hashed"),
            User(id=4, user="veronesa25", first_name="Verona", last_name="Mesa", mail="veronesa25@outlook.com", password="hashed"),
        ])
        db.session.add_all([
            Character(id=11, name="Luke Skywalker", gender="male", skin_color="fair", hair_color="blond", height="172"),
            Character(id=12, name="C-3PO", gender="n/a", skin_color="gold", hair_color="n/a", height="167"),
            Character(id=13, name="R2-D2", gender="n/a", skin_color="white", hair_color="blue", height="96"),
            Character(id=14, name="Darth Vader", gender="male", skin_color="white", hair_color="none", height="202"),
        ])
        db.session.add_all([
            Planet(id=21, name="Tatooine", climate="arid", surface_water="1", diameter="10465", rotation_period="23"),
            Planet(id=22, name="Alderaan", climate="temperate", surface_water="40", diameter="12500", rotation_period="24"),
            Planet(id=23, name="Yavin IV", climate="temperate, tropical", surface_water="8", diameter="10200", rotation_period="24"),
            Planet(id=24, name="Hoth", climate="frozen", surface_water="100", diameter="200", rotation_period="23"),
        ])
        db.session.add_all([
            FavoriteCharacter(id=31, user_id=2, character_id=11, created_at=date(2025, 7, 4), is_active=True, action_source="home"),
            FavoriteCharacter(id=32, user_id=3, character_id=14, created_at=date(2025, 6, 6), is_active=True, action_source="navbar_button"),
            FavoriteCharacter(id=33, user_id=1, character_id=13, created_at=date(2025, 5, 16), is_active=False, action_source="favorites_pages"),
            FavoriteCharacter(id=34, user_id=4, character_id=12, created_at=date(2025, 8, 1), is_active=True, action_source="custom_list"),
        ])
        db.session.add_all([
            FavoritePlanet(id=41, user_id=1, planet_id=21, created_at=date(2025, 8, 11), is_active=True, action_source="favorites_pages"),
            FavoritePlanet(id=42, user_id=2, planet_id=24, created_at=date(2025, 8, 5), is_active=False, action_source="custom_list"),
            FavoritePlanet(id=43, user_id=4, planet_id=23, created_at=date(2025, 8, 8), is_active=True, action_source="home"),
            FavoritePlanet(id=44, user_id=3, planet_id=22, created_at=date(2025, 8, 1), is_active=True, action_source="navbar_button"),
        ])
        db.session.commit()


@app.route('/people', methods=['GET'])
def get_people():
    personajes = Character.query.all()
    return jsonify([personaje.serialize() for personaje in personajes]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    personaje = Character.query.get(people_id)
    if not personaje:
        raise APIException("Person not found", 404)
    return jsonify(personaje.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planetas = Planet.query.all()
    return jsonify([planeta.serialize() for planeta in planetas]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planeta = Planet.query.get(planet_id)
    if not planeta:
        raise APIException("Planet not found", 404)
    return jsonify(planeta.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    usuarios = User.query.all()
    return jsonify([usuario.serialize() for usuario in usuarios]), 200

@app.route('/users/favorites', methods=['GET'])
def get_my_favorites():
    usuario = User.query.get(CURRENT_USER_ID)
    if not usuario:
        raise APIException("Current user not found", 404)
    favoritos_personajes = [favorito_personaje.serialize() for favorito_personaje in FavoriteCharacter.query.filter_by(user_id=usuario.id, is_active=True)]
    favoritos_planetas = [favorito_planeta.serialize() for favorito_planeta in FavoritePlanet.query.filter_by(user_id=usuario.id, is_active=True)]
    return jsonify({"user": usuario.serialize(), "characters": favoritos_personajes, "planets": favoritos_planetas}), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_fav_person(people_id):
    usuario = User.query.get(CURRENT_USER_ID)
    if not usuario:
        raise APIException("Current user not found", 404)
    personaje = Character.query.get(people_id)
    if not personaje:
        raise APIException("Person not found", 404)
    favorito_personaje = FavoriteCharacter.query.filter_by(user_id=usuario.id, character_id=people_id).first()
    if favorito_personaje and favorito_personaje.is_active:
        return jsonify({"status": "exists", "favorite": favorito_personaje.serialize()}), 200
    if favorito_personaje:
        favorito_personaje.is_active = True
        db.session.commit()
        return jsonify({"status": "reactivated", "favorite": favorito_personaje.serialize()}), 200
    nuevo_favorito_personaje = FavoriteCharacter(user_id=usuario.id, character_id=people_id, created_at=date.today(), is_active=True)
    db.session.add(nuevo_favorito_personaje)
    db.session.commit()
    return jsonify({"status": "created", "favorite": nuevo_favorito_personaje.serialize()}), 201

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def del_fav_person(people_id):
    favorito_personaje = FavoriteCharacter.query.filter_by(user_id=CURRENT_USER_ID, character_id=people_id, is_active=True).first()
    if not favorito_personaje:
        raise APIException("Active favorite not found", 404)
    favorito_personaje.is_active = False
    db.session.commit()
    return jsonify({"status": "deactivated", "favorite": favorito_personaje.serialize()}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def del_fav_planet(planet_id):
    favorito_planeta = FavoritePlanet.query.filter_by(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id,
        is_active=True
    ).first()
    if not favorito_planeta:
        raise APIException("Active favorite not found", 404)
    favorito_planeta.is_active = False
    db.session.commit()
    return jsonify({"status": "deactivated", "favorite": favorito_planeta.serialize()}), 200



@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(planet_id):
    usuario = User.query.get(CURRENT_USER_ID)
    if not usuario:
        raise APIException("Current user not found", 404)
    planeta = Planet.query.get(planet_id)
    if not planeta:
        raise APIException("Planet not found", 404)
    favorito_planeta = FavoritePlanet.query.filter_by(user_id=usuario.id, planet_id=planet_id).first()
    if favorito_planeta and favorito_planeta.is_active:
        return jsonify({"status": "exists", "favorite": favorito_planeta.serialize()}), 200
    if favorito_planeta:
        favorito_planeta.is_active = True
        db.session.commit()
        return jsonify({"status": "reactivated", "favorite": favorito_planeta.serialize()}), 200
    nuevo_favorito_planeta = FavoritePlanet(user_id=usuario.id, planet_id=planet_id, created_at=date.today(), is_active=True)
    db.session.add(nuevo_favorito_planeta)
    db.session.commit()
    return jsonify({"status": "created", "favorite": nuevo_favorito_planeta.serialize()}), 201