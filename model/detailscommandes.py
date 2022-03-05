from model.db import db

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