from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost/restaurant'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secretkey'

db = SQLAlchemy(app)

class Article(db.Model):
    __tablename__ = 'article'
    
    idarticle  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idcategorie  = db.Column(db.Integer, db.ForeignKey('categorie.idcategorie', ondelete='CASCADE'))
    nom = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    prix  = db.Column(db.Float())
    visibilite = db.Column(db.Boolean)
    position = db.Column(db.Integer, nullable=False)
    
    def __init__(self, idarticle, idcategorie, nom, description, prix, visibilite, position):
        self.idarticle = idarticle
        self.idcategorie = idcategorie
        self.nom = nom
        self.description = description
        self.prix = prix
        self.visibilite = visibilite
        self.position = position
    
class Categorie(db.Model):
    __tablename__ = 'categorie'
    
    idcategorie  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    visibilite = db.Column(db.Boolean)
    position = db.Column(db.Integer, unique=True, nullable=False)
    article = db.relationship('Article', backref='categorie', passive_deletes='all')

    def __init__(self, idcategorie, nom, visibilite, position):
        self.idcategorie = idcategorie
        self.nom = nom
        self.visibilite = visibilite
        self.position = position
        
class Commande(db.Model):
    __tablename__='commande'
    
    idcommande = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numtable = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    commentaire = db.Column(db.String(500), nullable=True) 
    
    def __init__(self, idcommande, numtable, status, commentaire):
        self.idcommande = idcommande
        self.numtable = numtable
        self.status = status
        self.commentaire = commentaire    
class DetailsCommande(db.Model):
    __tablename__ ='detailscommande'
    
    iddetailscommande = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idcommande = db.Column(db.Integer, db.ForeignKey('commande.idcommande'))
    idarticle  = db.Column(db.Integer, db.ForeignKey('article.idarticle'), nullable=False)
    idquantite = db.Column(db.Integer, nullable=False)
    
    def __init__(self, idcommande, idarticle, idquantite):
        self.idcommande = idcommande
        self.idarticle = idarticle
        self.idquantite = idquantite
        
class Tables(db.Model):
    __tablename__ ='tables'
    
    idtable = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(10), unique=True, nullable=False)
    url = db.Column(db.String(50), unique=True)
    
    def __init__(self, idtable, nom, url):
        self.idtable = idtable
        self.nom = nom
        self.url = url