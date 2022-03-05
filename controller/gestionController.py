import json
from nntplib import ArticleInfo
from turtle import pos, position
from flask import render_template, send_file, send_from_directory
from flask import request,flash
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import asc, join, or_, update
from sqlalchemy.sql.schema import Table
from model.categorie import Categorie
from model.article import Article
from model.tables import Tables
from model.commande import Commande
from model.detailscommandes import DetailsCommande
from model.db import db
from itertools import groupby, product
from werkzeug.utils import redirect
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
import re
import requests
import qrcode
import io
import os
class GestionController():
    
    def fetch_data(self):
        """Retourne la liste des catégories et des articles dans le template table.html

        Returns:
            render_template: Affiche la page gestion.html avec les catégories et les articles associés.
        """
        nbreCat = db.session.query(Categorie).count()
        nbreArticle = db.session.query(Article).count()
        nbreCatInvisible = db.session.query(Categorie).filter(Categorie.visibilite==False).count()
        nbreArticleInvisible = db.session.query(Categorie, Article).filter(Categorie.idcategorie==Article.idcategorie, or_(Article.visibilite==False, Categorie.visibilite==False)).count()
        result_categorie = db.session.query(Categorie).order_by(Categorie.position).all()
        data_article = db.session.query(Article, Categorie).order_by(Categorie.position,Article.position).join(Article).all()
        # print(result_article)
        # for i in result_article:
        #     print(i.Article.nom, '   ', i.Article.description, '   ', i.Categorie.nom)
        lists = {}
        for k, g in groupby(data_article, key=lambda t: t['Categorie']):
            lists[k] = list(g)
            # print(lists)
        # for list_, items in lists.items():
        #     print(list_.nom)
        #     for item in items:
        #         print('    ', item[0].nom,'    ', item[0].description)
        return render_template("gestion.html", data= result_categorie, data2 = lists, nbreCat=nbreCat, nbreArticle=nbreArticle, nbreCatInvisible=nbreCatInvisible, nbreArticleInvisible=nbreArticleInvisible)
    
    def ajouter_article(self, datapost):
        """Methode qui rajoute un article dans la table article et crée une catégorie dans la table catégorie si elle n'existe pas

        Args:
            datapost ([type]): contenu de la requête http

        Returns:
            rien: Met à jour la base de données et recharge la page avec les données mises à jour.
        """
        print(datapost.get('prixarticle'))
        # print(isinstance(datapost.get('prixarticle'), float))
        print(type(datapost.get('prixarticle')))
        pattern = '^[+-]?((\d+(\.\d+)?)|(\.\d+))$'
        if (datapost.get('nomarticle') == ''):
            print("toto")
            flash('Le nom de l\'article ne peut être vide', 'danger')
            return redirect("/gestion")
        elif (datapost.get('prixarticle') == ''or datapost.get('categorieSelection') == ''):
            print("toto")
            flash('Seul le champ description peut être vide', 'danger')
            return redirect("/gestion")
        elif (len(datapost.get('description'))>500):
            print(len(datapost.get('description')))
            flash('Le champ description est limité à 500 caractères', 'danger')
            return redirect("/gestion")
        elif (db.session.query(Article).filter_by(nom=datapost.get('nomarticle')).count()>0):
            flash('Ce nom d\'article a déjà été utilisé', 'danger')
            return redirect("/gestion")
        elif not re.match(pattern, (datapost.get('prixarticle'))):
            flash('Le prix n\'est pas au bon format, ex: 3.50', 'danger')
            return redirect("/gestion")
        else:
        # Vérification s'il existe au moins une catégorie
            if(db.session.query(Categorie).first() is not None):
                #Vérifie si la catégorie séléctionnée existe
                if (db.session.query(Categorie).filter_by(nom=datapost.get('categorieSelection')).first() is not None):
                    numcat = db.session.query(Categorie).filter_by(nom=datapost.get('categorieSelection')).first()
                    #Vérifie s'il y a déjà des articles dans la catégorie pour spécifier la position (1 s'il n'y en a pas sinon, on incémente de 1 la position la plus élévé)
                    if (db.session.query(Article).filter_by(idcategorie=numcat.idcategorie).count() == 0):
                        article = Article(idcategorie=numcat.idcategorie,nom=datapost.get('nomarticle'),description=datapost.get('description'),prix=datapost.get('prixarticle'),visibilite=True,position=1)
                        db.session.add(article)   
                        db.session.commit()
                    else:
                        resart = db.session.query(Article).filter(Article.idcategorie==numcat.idcategorie).order_by(desc(Article.position)).first()
                        lastPositionArticle = resart.position + 1
                        article = Article(idcategorie=numcat.idcategorie,nom=datapost.get('nomarticle'),description=datapost.get('description'),prix=datapost.get('prixarticle'),visibilite=True,position=lastPositionArticle)
                        db.session.add(article)   
                        db.session.commit()
                else:
                    res = db.session.query(func.max(Categorie.idcategorie).label("max_cat"))
                    lastPosition = res.one().max_cat + 1
                    categorie= Categorie(nom=datapost.get('categorieSelection'),visibilite=True,position=lastPosition)
                    db.session.add(categorie)   
                    db.session.commit()
                    numcat = db.session.query(Categorie).filter_by(nom=datapost.get('categorieSelection')).first()
                    article = Article(idcategorie=numcat.idcategorie,nom=datapost.get('nomarticle'),description=datapost.get('description'),prix=datapost.get('prixarticle'),visibilite=True,position=1)
                    db.session.add(article)   
                    db.session.commit()
            else:
                #Si Catégorie et donc articles est vide, il crée la catégorie puis l'article
                categorie= Categorie(nom=datapost.get('categorieSelection'),visibilite=True,position=1)
                db.session.add(categorie)   
                db.session.commit()
                numcat = db.session.query(Categorie).filter_by(nom=datapost.get('categorieSelection')).first()
                article = Article(idcategorie=numcat.idcategorie,nom=datapost.get('nomarticle'),description=datapost.get('description'),prix=datapost.get('prixarticle'),visibilite=True,position=1)
                db.session.add(article)   
                db.session.commit()
            flash('Votre carte a été mise à jour avec succès', 'success')    
            return redirect("/gestion")
    
    def deleteById(self,id):
        """Méthode qui supprime un article à partir de son id

        Args:
            id (int): valeur de l'id de l'article qu'on veut supprimer

        Returns:
            rien: Met à jour la base de données et recharge la page avec les données mises à jour.
        """
        art = db.session.query(Article).filter(Article.idarticle==id).first()
        db.session.delete(art)
        db.session.commit()
        flash('Votre carte a été mise à jour avec succès', 'success')
        return redirect("/gestion")
    
    def deleteCatById(self,id):
        """Méthode qui supprime une catégorie à partir de son id et les articles associés par effet cascade

        Args:
            id (int): valeur de l'id de la catégorie qu'on veut supprimer

        Returns:
            rien: Met à jour la base de données et recharge la page avec les données mises à jour.
        """
        cat = db.session.query(Categorie).filter(Categorie.idcategorie==id).first()
        db.session.delete(cat)
        db.session.commit()
        flash('Votre carte a été mise à jour avec succès', 'success')
        return redirect("/gestion")
    
    def downcat(self,id):
        """Méthode qui permet de descendre une catégorie dans le menu

        Args:
            id (int): Contient l'id de la catégorie
        """
        resmax = db.session.query(func.max(Categorie.position).label("max_cat"))
        lastPosition = resmax.one().max_cat
        print("Dernière Position")
        print(lastPosition)
        resmin = db.session.query(func.min(Categorie.position).label("min_cat"))
        FirstPosition = resmin.one().min_cat
        print("Première Position")
        print(FirstPosition)
        positioncat = db.session.query(Categorie).filter(Categorie.idcategorie==id).first().position
        print(positioncat)
        if (positioncat == lastPosition):
            flash('Votre catégorie est déjà en dernière position', 'info')
            return redirect("/gestion")
        else:
            # select * from foo where id = (select min(id) from foo where id > 4)
            positionsuiv = db.session.query(func.min(Categorie.position).filter(Categorie.position > positioncat).label("position_dessus"))
            positionsuivante = positionsuiv.one().position_dessus
            print("Position suivante:")
            print(positionsuivante)
            categorie = Categorie.query.filter_by(idcategorie=id).first()
            categoriesuivante = Categorie.query.filter_by(position=positionsuivante).first()
            categorie.position = lastPosition + 1
            categoriesuivante.position = lastPosition + 2
            db.session.commit()
            categorie.position = positionsuivante
            categoriesuivante.position = positioncat
            db.session.commit()
            return redirect("/gestion")
        return redirect("/gestion")
    
    def upcat(self,id):
        """Méthode qui permet de monter une catégorie dans le menu

        Args:
            id (int): Contient l'id de la catégorie
        """
        resmax = db.session.query(func.max(Categorie.position).label("max_cat"))
        lastPosition = resmax.one().max_cat
        print("Dernière Position")
        print(lastPosition)
        resmin = db.session.query(func.min(Categorie.position).label("min_cat"))
        FirstPosition = resmin.one().min_cat
        print("Première Position")
        print(FirstPosition)
        positioncat = db.session.query(Categorie).filter(Categorie.idcategorie==id).first().position
        print(positioncat)
        if (positioncat == FirstPosition):
            flash('Votre catégorie est déjà en première position', 'info')
            return redirect("/gestion")
        else:
            # select * from foo where id = (select min(id) from foo where id > 4)
            positionprec = db.session.query(func.max(Categorie.position).filter(Categorie.position < positioncat).label("position_dessous"))
            positionprecedente = positionprec.one().position_dessous
            print("Position suivante:")
            print(positionprecedente)
            categorie = Categorie.query.filter_by(idcategorie=id).first()
            categorieprecedente = Categorie.query.filter_by(position=positionprecedente).first()
            categorie.position = lastPosition + 1
            categorieprecedente.position = lastPosition + 2
            db.session.commit()
            categorie.position = positionprecedente
            categorieprecedente.position = positioncat
            db.session.commit()
            return redirect("/gestion")
        return redirect("/gestion")
    
    def downart(self,id):
        """Méthode qui permet de descendre un article dans le menu

        Args:
            id (int): Contient l'id de l'article'
        """
        article = Article.query.filter_by(idarticle=id).first()
        cat_article = article.idcategorie
        print("Catégorie de l'article")
        print(cat_article)
        resmax = db.session.query(func.max(Article.position).filter(Article.idcategorie==cat_article).label("maxposition_art"))
        lastPosition = resmax.one().maxposition_art
        print("Position max article de cette catégorie")
        print(lastPosition)
        resmin = db.session.query(func.min(Article.position).filter(Article.idcategorie==cat_article).label("minposition_art"))
        FirstPosition = resmin.one().minposition_art
        print("Première Position article de cette catégorie")
        print(FirstPosition)
        positionart = db.session.query(Article).filter(Article.idarticle==id).first().position
        print(positionart)
        if (positionart == lastPosition):
            flash('Votre article est déjà en dernière position', 'info')
            return redirect("/gestion")
        else:
            # select * from foo where id = (select min(id) from foo where id > 4)
            positionsuiv = db.session.query(func.min(Article.position).filter(Article.position > positionart, Article.idcategorie==cat_article).label("position_dessus"))
            positionsuivante = positionsuiv.one().position_dessus
            print("Position suivante:")
            print(positionsuivante)
            article = Article.query.filter_by(idarticle=id).first()
            articlesuivant = Article.query.filter(Article.idcategorie==cat_article, Article.position==positionsuivante).first()
            article.position = lastPosition + 1
            articlesuivant.position = lastPosition + 2
            db.session.commit()
            article.position = positionsuivante
            articlesuivant.position = positionart
            db.session.commit()
            return redirect("/gestion")
        return redirect("/gestion")
    
    def upart(self,id):
        """Méthode qui permet de monter un article dans le menu

        Args:
            id (int): Contient l'id de l'article'
        """
        article = Article.query.filter_by(idarticle=id).first()
        cat_article = article.idcategorie
        print("Catégorie de l'article")
        print(cat_article)
        resmax = db.session.query(func.max(Article.position).filter(Article.idcategorie==cat_article).label("maxposition_art"))
        lastPosition = resmax.one().maxposition_art
        print("Position max article de cette catégorie")
        print(lastPosition)
        resmin = db.session.query(func.min(Article.position).filter(Article.idcategorie==cat_article).label("minposition_art"))
        FirstPosition = resmin.one().minposition_art
        print("Première Position article de cette catégorie")
        print(FirstPosition)
        positionart = db.session.query(Article).filter(Article.idarticle==id).first().position
        print(positionart)
        if (positionart == FirstPosition):
            flash('Votre article est déjà en première position', 'info')
            return redirect("/gestion")
        else:
            # select * from foo where id = (select min(id) from foo where id > 4)
            positionprec = db.session.query(func.max(Article.position).filter(Article.position < positionart, Article.idcategorie==cat_article).label("position_dessus"))
            positionprecedente = positionprec.one().position_dessus
            print("Position précedente:")
            print(positionprecedente)
            article = Article.query.filter_by(idarticle=id).first()
            articlesuivant = Article.query.filter(Article.idcategorie==cat_article, Article.position==positionprecedente).first()
            article.position = lastPosition + 1
            articlesuivant.position = lastPosition + 2
            db.session.commit()
            article.position = positionprecedente
            articlesuivant.position = positionart
            db.session.commit()
            return redirect("/gestion")
        return redirect("/gestion")
        
    
    def editer_article(self, datapost):
        """Méthode qui met à jour un article en base de données

        Args:
            datapost ([type]): contenu de la requête http

        Returns:
            rien: Met à jour la base de données et recharge la page avec les données mises à jour.
        """
        pattern = '^[+-]?((\d+(\.\d+)?)|(\.\d+))$'
        if (datapost.get('nomarticle') == ''):
            print("toto")
            flash('Le nom de l\'article ne peut être vide', 'danger')
            return redirect("/gestion")
        elif (datapost.get('prixarticle') == ''or datapost.get('categorieSelection') == ''):
            print("toto")
            flash('Seul le champ description peut être vide', 'danger')
            return redirect("/gestion")
        elif (len(datapost.get('description'))>500):
            print(len(datapost.get('description')))
            flash('Le champ description est limité à 500 caractères', 'danger')
            return redirect("/gestion")
        elif not re.match(pattern, (datapost.get('prixarticle'))):
            flash('Le prix n\'est pas au bon format, ex: 3.50', 'danger')
            return redirect("/gestion")
        else:        
            print(datapost.get('idcategorie'))
            article = Article.query.filter_by(idarticle=datapost.get('idarticle')).first()
            print(article.idcategorie)
            article.idcategorie = datapost.get('idcategorie')
            article.nom = datapost.get('nomarticle')
            article.description = datapost.get('description')
            article.prix = datapost.get('prixarticle')
            db.session.commit()
            flash('Votre article a été mise à jour avec succès', 'success')
            return redirect("/gestion")
    
    def editer_categorie(self, datapost):
        """Méthode qui met à jour une catégorie en base de données

        Args:
            datapost ([type]): contenu de la requête http

        Returns:
            rien: Met à jour la base de données et recharge la page avec les données mises à jour.
        """
        print(datapost)
        categorie = Categorie.query.filter_by(idcategorie=datapost.get('idcategorie')).first()
        categorie.nom = datapost.get('nomcatgorie')
        db.session.commit()
        flash('Votre catégorie a été mise à jour avec succès', 'success')
        return redirect("/gestion")
    
    def fetch_suivi(self):
        """Retourne la liste des commandes en attente de prises en charge, en attente de validation et affiche dans les vignettes le nombre de commandes passées, le nombre de commande en cours et le nombre de commande en attente de prise en charge.

        Returns:
            render_template: Affiche la page suivi.html avec le statut des commandes passées.
        """
        if(db.session.query(Commande).order_by(desc(Commande.idcommande)).first() is not None):
            nbcmdEnAttente = db.session.query(Commande).filter(Commande.status==0).count()
            nbcmdEnCours = db.session.query(Commande).filter(Commande.status==1).count()
            nbcmdFinal = db.session.query(Commande).filter(Commande.status==2).count()
            numcommande = db.session.query(Commande).order_by(desc(Commande.idcommande)).first()
            print(numcommande.idcommande)
            result = db.session.query(DetailsCommande.idcommande, DetailsCommande.idarticle, DetailsCommande.idquantite, Article.nom, Article.position).join(Article, DetailsCommande.idarticle == Article.idarticle).subquery()
            data_suivi = db.session.query(Commande, result).order_by(Commande.status, desc(Commande.idcommande), result.c.idcommande).join(result).filter(Commande.status != 2).all()
            lists = {}
            for k, g in groupby(data_suivi, key=lambda t: t['Commande']):
                lists[k] = list(g)
                print("lists")
                print(lists)
            for list_, items in lists.items():
                print(list_.numtable)
                for item in items:
                    print(item)
                    print(item[4], item[3])
            return render_template("suivi.html", lists=lists, numerocommande=numcommande.idcommande, nbcmdFinal=nbcmdFinal, nbcmdEnAttente=nbcmdEnAttente, nbcmdEnCours=nbcmdEnCours)
        else:
            return render_template("suivi.html", lists=0, numerocommande=0, nbcmdFinal=0,  nbcmdEnAttente=0, nbcmdEnCours=0)
    
    def prendreencharge(self,id):
        """Change le status de la commande en 1 en base de données, indique que la commande a été prise en charge

        Args:
            id (int): id de la commande dont on veut mettre à jour le statut

        Returns:
            rien: Met à jour la base de données et recharge la page avec les données mises à jour.
        """
        db.session.query(Commande).filter(Commande.idcommande==id).update({Commande.status: 1})          
        db.session.commit()
        return redirect("/suivi")
    
    def finaliser(self,id):
        """Change le status de la commande en 2 en base de données, indique que la commande a été finalisée et supprime les données de la table detailscommande relative à cette commande.

        Args:
            id (int): id de la commande dont on veut mettre à jour le statut

        Returns:
            rien: Met à jour la base de données et recharge la page avec les données mises à jour.
        """
        commande = Commande.query.filter_by(idcommande=id).first()
        commande.status = 2
        details = db.session.query(DetailsCommande).filter(DetailsCommande.idcommande==id).all()
        for o in details:
            db.session.delete(o)
        db.session.commit()
        return redirect("/suivi")
    
    def lastorder(self):
        """Méthode appelée toutes les 10 secondes par un script javascript dans la page suivi.html et qui va récuperer l'idcommande max dans la table commande. Rafraichit la page suivi si une nouvelle commande est passée.

        Returns:
            [str]: idcommande max dans la table commande
        """
        numcommande = db.session.query(Commande).order_by(desc(Commande.idcommande)).first()
        if numcommande == None:
            return str(-1)
        else:
            return str(numcommande.idcommande)
    
    def updatetable(self,id):
        """Méthode qui met à jour la table table avec le nombre de table (id) et les urls raccourcis. Cette méthode recoit en paramètre le nombre de table, pour chaque table, on regénère l'URL de la table et on l'envoie au serveur https://2me.nu qui va nous renvoyer une URL raccourcies qu'on va mettre dans la table.

        Args:
            id (int): nombre de tables

        Returns:
            rien: redirige vers la page qrcode après avoir mis à jour la table table avec les données mises à jour.
        """
        pattern = '^([\s\d]+)$'
        if not re.match(pattern, (id.get('nbretable'))):
            flash('Vous devez renseigner un nombre.', 'danger')
            return redirect("/qrcode")
        else:
            db.session.query(Tables).delete()
            db.session.commit()
            tables = id.get('nbretable')
            for table in range(int(tables)):
                print("table"+str(table+1))
                url = request.referrer
                print(url)
                numtable = "table"+str(table+1)
                if 'GENERATE_URL' in os.environ:
                    if os.environ['GENERATE_URL'] == 'PROD':
                        url = url.replace("admin-","").replace("qrcode", numtable)
                    else:
                        url = re.sub("5000/qrcode", "5001/table"+str(table+1), url)
                else:
                    url = re.sub("5000/qrcode", "5001/table"+str(table+1), url)
                # url = re.sub("5000/qrcode", "5001/table"+str(table+1), url)
                # URL en prod
                # url = url.replace("admin-","").replace("qrcode", numtable)
                print(url)
                r = requests.post('https://2me.nu/addnewurl', json={"url": url})
                print('r')
                print(r.text)
                table = Tables(nom="table"+str(table+1), url=r.text)
                db.session.add(table)
                db.session.commit()
            flash('Le nombre de table a été mis à jour avec succès', 'success')
            return redirect("/qrcode")
    
    def qrcode(self):
        """Méthode qui retourne le nombre de table.

        Returns:
            render_template: renvoie vers la page qrcode avec le nombre de table.
        """
        rows = db.session.query(Tables).count()
        print(rows)
        return render_template("qrcode.html", data=rows)
    
    def generateqrcode(self, id):
        """Méthode qui permet de générer un qrcode spécifique à une table au format jpg

        Args:
            id ([int]): Numéro de la table dont on veut générer le QRcode

        Returns:
            send_file: renvoie le téléchargement du QRcode au format jpg.
        """
        print("qrcode")
        print(id.get('qrcodegen'))
        nomtable = 'table'+id.get('qrcodegen')
        print(nomtable)
        shorturl = db.session.query(Tables).filter_by(nom=nomtable).first()
        print(shorturl.url)
        file = qrcode.make(shorturl.url)
        buf = io.BytesIO()
        file.save(buf)
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name=nomtable+".jpg")
        # return redirect("/qrcode")
        
    def generateallqrcode(self):
        """Méthode qui permet la génération de l'ensemble des QRcodes de toutes les tables au format png et les enregistrer dans le dossier /static/qr

        Returns:
            rien: redirige vers la route generatepdf qui va générer un pdf avec un jeu de QRcodes propre à chaque table
        """
        alltables = db.session.query(Tables).all()
        for i in alltables:
            print(i.url)
            file = qrcode.make(i.url)
            file.save(os.path.join("./static/qr", secure_filename(i.nom+".png")))
        return redirect("/generatepdf")
    
    def generatepdf(self):
        """Méthode qui permet de générer un jeu de QRcode pour chaque table au format pdf

        Returns:
            send_from_directory: renvoie le téléchargement d'un jeu de QRcode pour l'ensemble des tables au format pdf.
        """
        alltables = db.session.query(Tables).all()
        from fpdf import FPDF
        pdf = FPDF()
        pdf.alias_nb_pages()
        for i in alltables:
            print(i.nom+".png")
            num = re.sub('table', "", i.nom)
            print(num)
            pdf.add_page()
            pdf.set_top_margin(10)
            pdf.set_font('Arial', 'B', 16)
            pdf.image("./static/qr/"+i.nom+".png", 10, 10, 50 ,50)
            pdf.set_xy(55, 15)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 80, 10, 50 ,50)
            pdf.set_xy(125, 15)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 150, 10, 50 ,50)
            pdf.set_xy(195, 15)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')

            pdf.image("./static/qr/"+i.nom+".png", 10, 65, 50 ,50)
            pdf.set_xy(55, 70)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 80, 65, 50 ,50)
            pdf.set_xy(125, 70)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 150, 65, 50 ,50)
            pdf.set_xy(195, 70)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')

            pdf.image("./static/qr/"+i.nom+".png", 10, 120, 50 ,50)
            pdf.set_xy(55, 125)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 80, 120, 50 ,50)
            pdf.set_xy(125, 125)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 150, 120, 50 ,50)
            pdf.set_xy(195, 125)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')

            pdf.image("./static/qr/"+i.nom+".png", 10, 175, 50 ,50)
            pdf.set_xy(55, 180)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 80, 175, 50 ,50)
            pdf.set_xy(125, 180)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 150, 175, 50 ,50)
            pdf.set_xy(195, 180)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')

            pdf.image("./static/qr/"+i.nom+".png", 10, 230, 50 ,50)
            pdf.set_xy(55, 235)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 80, 230, 50 ,50)
            pdf.set_xy(125, 235)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
            pdf.image("./static/qr/"+i.nom+".png", 150, 230, 50 ,50)
            pdf.set_xy(195, 235)
            pdf.cell(30, 10, txt = num, border = 0, ln = 0, align = 'c', fill = False, link = '')
        pdf.output('./static/qr/qrcode.pdf', 'F')
        return send_from_directory("./static/qr/", path='qrcode.pdf', as_attachment=True)
    
    def rendreinvisiblearticle(self,id):
        """Méthode qui passe le status visibilite d'un article de true à false

        Args:
            id (int): id de l'article qu'on veut rendre invisible

        Returns:
            rien: Met à False visibilite dans la table article et redirige vers la page gestion avec les données mises à jour.
        """
        db.session.query(Article).filter(Article.idarticle==id).update({Article.visibilite: False})
        db.session.commit()
        return redirect("/gestion")
    
    def rendrevisiblearticle(self,id):
        """Méthode qui passe le status visibilite d'un article de false à true

        Args:
            id (int): id de l'article qu'on veut rendre visible

        Returns:
            rien: Met à true visibilite dans la table article et redirige vers la page gestion avec les données mises à jour.
        """
        db.session.query(Article).filter(Article.idarticle==id).update({Article.visibilite: True})
        db.session.commit()
        return redirect("/gestion")
    
    def rendreinvisiblecategorie(self,id):
        """Méthode qui passe le status visibilite d'une catégorie de true à false. Change aussi le statut de tous les articles de cette catégorie.

        Args:
            id (int): id de la categorie qu'on veut rendre invisible

        Returns:
            rien: Met à False visibilite dans la table categorie et redirige vers la page gestion avec les données mises à jour.
        """
        db.session.query(Categorie).filter(Categorie.idcategorie==id).update({Categorie.visibilite: False})
        db.session.query(Article).filter(Article.idcategorie==id).update({Article.visibilite: False})
        db.session.commit()
        return redirect("/gestion")
    
    def rendrevisiblecategorie(self,id):
        """Méthode qui passe le status visibilite d'une catégorie de false à true. Change aussi le statut de tous les articles de cette catégorie.

        Args:
            id (int): id de la categorie qu'on veut rendre visible

        Returns:
            rien: Met à False visibilite dans la table article et redirige vers la page gestion avec les données mises à jour.
        """
        db.session.query(Categorie).filter(Categorie.idcategorie==id).update({Categorie.visibilite: True})
        db.session.query(Article).filter(Article.idcategorie==id).update({Article.visibilite: True})
        db.session.commit()
        return redirect("/gestion")
    
    def deleteAllCmd(self):
        """Method qui efface toutes les commandes de la table commande afin de remettre les compteurs à 0

        Returns:
            rien: met à jour la table commande et redirige vers la page suivi avec les données mises à jour.
        """
        if(db.session.query(Commande).first() is not None):
            listCmd = db.session.query(Commande).all()
            for cmd in listCmd:
                db.session.delete(cmd)
            db.session.commit()
        return redirect("/suivi")
    
    def deleteCmdById(self,id):
        """Methode qui permet d'annuler une commande d'un client.

        Args:
            id (int): id de la commande qu'on veu annuler

        Returns:
            rien: met à jour la table commande et redirige vers la page suivi avec les données mises à jour.
        """
        cmd = db.session.query(Commande).filter(Commande.idcommande==id).first()
        db.session.delete(cmd)
        db.session.commit()
        return redirect("/suivi")