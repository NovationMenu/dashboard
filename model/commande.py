from model.db import db

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