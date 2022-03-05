from model.db import db
from sqlalchemy import ForeignKey

class Article(db.Model):
    __tablename__ = 'article'
    
    idarticle  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idcategorie  = db.Column(db.Integer, ForeignKey('categorie.idcategorie'))
    nom = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    prix  = db.Column(db.Float())
    visibilite = db.Column(db.Boolean)
    position = db.Column(db.Integer, nullable=False)
    
    def __init__(self, idcategorie, nom, description, prix, visibilite, position):
        self.idcategorie = idcategorie
        self.nom = nom
        self.description = description
        self.prix = prix
        self.visibilite = visibilite
        self.position = position
