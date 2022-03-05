from model.article import Article
from model.db import db

class Categorie(db.Model):
    __tablename__ = 'categorie'
    
    idcategorie  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    visibilite = db.Column(db.Boolean)
    position = db.Column(db.Integer, unique=True, nullable=False)
    

    def __init__(self, nom, visibilite, position):
        self.nom = nom
        self.visibilite = visibilite
        self.position = position
    


