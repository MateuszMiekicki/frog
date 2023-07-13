from entity import device as entity
from sqlalchemy.orm import Session
from configuration.database import Database


class Pet():
    def __init__(self, database: Database):
        self.database = database

    def add_pet(self, name: str, description: str):
        with self.database.get_db() as db:
            new_pet = entity.Pet(name=name, description=description)
            db.add(new_pet)
            db.commit()

    def get_pet_by_id(self, pet_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Pet).filter(entity.Pet.id == pet_id).first()

    def get_pets(self):
        with self.database.get_db() as db:
            return db.query(entity.Pet).all()

    def delete_pet(self, pet_id: int):
        with self.database.get_db() as db:
            db.query(entity.Pet).filter(
                entity.Pet.id == pet_id).delete()
            db.commit()


class PetHabitat():
    def __init__(self, database: Database):
        self.database = database

    def add_pet_habitat(self, pet_id: int, information: str):
        with self.database.get_db() as db:
            new_pet_habitat = entity.PetHabitat(
                pet_id=pet_id, information=information)
            db.add(new_pet_habitat)
            db.commit()

    def get_pet_habitat_by_id(self, pet_habitat_id: int):
        with self.database.get_db() as db:
            return db.query(entity.PetHabitat).filter(entity.PetHabitat.id == pet_habitat_id).first()

    def delete_pet_habitat(self, pet_habitat_id: int):
        with self.database.get_db() as db:
            db.query(entity.PetHabitat).filter(
                entity.PetHabitat.id == pet_habitat_id).delete()
            db.commit()
