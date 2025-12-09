from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    Favorite: Mapped[List["Favorite"]] = relationship(back_populates="User")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    population: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(120), nullable=False)
    Favorite: Mapped[List["Favorite"]] = relationship(back_populates="Planets")


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "climate": self.climate

        }
    

class People(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    BirthYear: Mapped[int] = mapped_column(String(120), nullable=False)
    Height: Mapped[str] = mapped_column(String(120), nullable=False)
    EyeColor: Mapped[str] = mapped_column(String(120), nullable=False)
    Gender: Mapped[str] = mapped_column(String(120), nullable=False)
    Favorite: Mapped[List["Favorite"]] = relationship(back_populates="People")


    def serialize(self):
        return {


            "id": self.id,
            "name": self.name,
            "BirthYear": self.BirthYear,
            "Height": self.Height,
            "EyeColor": self.EyeColor,
            "Gender": self.Gender,
            

        }
    
class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    id_people: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    id_planets: Mapped[int] = mapped_column(ForeignKey("planets.id"), primary_key=True)
    User: Mapped["User"] = relationship(back_populates="Favorite")
    People: Mapped["People"] = relationship(back_populates="Favorite")
    Planets: Mapped["Planets"] = relationship(back_populates="Favorite")
