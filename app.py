from flask import Flask, render_template, request
from werkzeug.utils import redirect
from controller.gestionController import GestionController
from model.db import db
import os

gestioncontroller = GestionController()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://root:root@localhost/restaurant')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secretkey'
db.init_app(app)

@app.route("/")
def hello():
    return redirect("/suivi")

@app.route("/suivi")
def suivi():
    return gestioncontroller.fetch_suivi()

@app.route("/gestion")
def gestion():
    return gestioncontroller.fetch_data()

@app.route("/ajoutArticle", methods=['POST', 'GET'])
def ajoutArticle():
    datapost = request.form
    return gestioncontroller.ajouter_article(datapost)

@app.route("/editerArticle", methods=['POST', 'GET'])
def editerArticle():
    datapost = request.form
    return gestioncontroller.editer_article(datapost)

@app.route("/editerCategorie", methods=['POST', 'GET'])
def editerCategorie():
    datapost = request.form
    return gestioncontroller.editer_categorie(datapost)

@app.route("/delete/<int:id>")
def delete(id):
    return gestioncontroller.deleteById(id)

@app.route("/deleteCat/<int:id>")
def deleteCat(id):
    return gestioncontroller.deleteCatById(id)

@app.route("/prendreencharge/<int:id>")
def prendreencharge(id):
    return gestioncontroller.prendreencharge(id)

@app.route("/finaliser/<int:id>")
def finaliser(id):
    return gestioncontroller.finaliser(id)

@app.route("/stock")
def stock():
    return render_template("stock.html")

@app.route("/qrcode")
def qrcode():
    return gestioncontroller.qrcode()
    
@app.route('/lastorder')
def lastorder():
    return gestioncontroller.lastorder()

@app.route('/updatetable', methods=['POST', 'GET'])
def updatetable():
    nombretable = request.form
    return gestioncontroller.updatetable(nombretable)

@app.route('/generateqrcode', methods=['POST', 'GET'])
def generateqrcode():
    qrcode = request.form
    return gestioncontroller.generateqrcode(qrcode)

@app.route('/generateallqrcode')
def generateallqrcode():
    return gestioncontroller.generateallqrcode()

@app.route('/generatepdf')
def generatepdf():
    return gestioncontroller.generatepdf()

@app.route("/rendreinvisiblearticle/<int:id>")
def rendreinvisiblearticle(id):
    return gestioncontroller.rendreinvisiblearticle(id)

@app.route("/rendrevisiblearticle/<int:id>")
def rendrevisiblearticle(id):
    return gestioncontroller.rendrevisiblearticle(id)

@app.route("/rendreinvisiblecategorie/<int:id>")
def rendreinvisiblecategorie(id):
    return gestioncontroller.rendreinvisiblecategorie(id)

@app.route("/rendrevisiblecategorie/<int:id>")
def rendrevisiblecategorie(id):
    return gestioncontroller.rendrevisiblecategorie(id)

@app.route("/deleteAll")
def deleteAllCmd():
    return gestioncontroller.deleteAllCmd()

@app.route("/deleteCmd/<int:id>")
def deleteCmd(id):
    return gestioncontroller.deleteCmdById(id)

@app.route("/downcat/<int:id>")
def downcat(id):
    return gestioncontroller.downcat(id)

@app.route("/upcat/<int:id>")
def upcat(id):
    return gestioncontroller.upcat(id)

@app.route("/downart/<int:id>")
def downart(id):
    return gestioncontroller.downart(id)

@app.route("/upart/<int:id>")
def upart(id):
    return gestioncontroller.upart(id)

@app.route("/disconnect")
def disconnect():
    url = request.referrer
    return redirect("https://auth.novation.menu/logout?rd="+url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')