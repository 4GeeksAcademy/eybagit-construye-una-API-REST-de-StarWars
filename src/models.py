from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    mail: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    favorite_characters: Mapped[list["FavoriteCharacter"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mail": self.mail,
            "is_active": self.is_active
        }

class Character(db.Model):
    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    gender: Mapped[str] = mapped_column(String(20))
    skin_color: Mapped[str] = mapped_column(String(40))
    hair_color: Mapped[str] = mapped_column(String(40))
    height: Mapped[str] = mapped_column(String(10))

    favorites: Mapped[list["FavoriteCharacter"]] = relationship(back_populates="character", cascade="all, delete-orphan")

    def serialize(self):
        return {atributo: getattr(self, atributo) for atributo in ["id", "name", "gender", "skin_color", "hair_color", "height"]}

class Planet(db.Model):
    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(40))
    surface_water: Mapped[str] = mapped_column(String(40))
    diameter: Mapped[str] = mapped_column(String(40))
    rotation_period: Mapped[str] = mapped_column(String(40))

    favorites: Mapped[list["FavoritePlanet"]] = relationship(back_populates="planet", cascade="all, delete-orphan")

    def serialize(self):
        return {atributo: getattr(self, atributo) for atributo in ["id", "name", "climate", "surface_water", "diameter", "rotation_period"]}

class FavoriteCharacter(db.Model):
    __tablename__ = "favorite_characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False)
    created_at: Mapped[Date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    action_source: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")

    user: Mapped["User"] = relationship(back_populates="favorite_characters")
    character: Mapped["Character"] = relationship(back_populates="favorites")

    __table_args__ = (UniqueConstraint("user_id", "character_id"),)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "created_at": str(self.created_at) if self.created_at else None,
            "is_active": self.is_active,
            "action_source": self.action_source,
            "character": self.character.serialize() if self.character else None
        }

class FavoritePlanet(db.Model):
    __tablename__ = "favorite_planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=False)
    created_at: Mapped[Date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    action_source: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")

    user: Mapped["User"] = relationship(back_populates="favorite_planets")
    planet: Mapped["Planet"] = relationship(back_populates="favorites")

    __table_args__ = (UniqueConstraint("user_id", "planet_id"),)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "created_at": str(self.created_at) if self.created_at else None,
            "is_active": self.is_active,
            "action_source": self.action_source,
            "planet": self.planet.serialize() if self.planet else None
        }
