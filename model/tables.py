from model.db import db

class Tables(db.Model):
    __tablename__ ='tables'
    
    idtable = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(10), unique=True, nullable=False)
    url = db.Column(db.String(50), unique=True)
    
    def __init__(self, nom, url):
        self.nom = nom
        self.url = url