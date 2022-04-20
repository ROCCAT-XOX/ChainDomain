from msilib.schema import Property
import os
from datetime import datetime
import sqlite3
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from sqlalchemy import null, true
from .models import User,Property,Transaction,Offer
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/chain', methods=['GET', 'POST'])
@login_required
def chain():
    return render_template("Chain_deine_Domain.html", user=current_user)

@auth.route('/immobilie', methods=['GET', 'POST'])
@login_required
def immobilie():
    return render_template("immobilie.html", user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            #con = sqlite3.connect('chaindomain.db')
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            
            db.session.add(new_user)
            db.session.commit()
            #BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            #db_path = os.path.join(BASE_DIR, "chaindomain.db")
            #with sqlite3.connect(db_path) as db:
            #cur = db.cursor()
            #hashPassword = generate_password_hash(password1, method='sha256')
            #cur.execute("INSERT INTO User (email, password, first_name) VALUES (?,?,?)",
            #    (email,first_name,hashPassword))
            #cur.commit()
            
            #cur.close()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)

#def get_db_connection():
 #   conn = sqlite3.connect('chaindomain.db')
  #  cur=conn.cursor()
   # return cur

#@auth.before_request
#def before_request():
 #   if current_user.is_authenticated:
  #      current_user.last_seen = datetime.utcnow()
   #     db.session.commit()

#@auth.route('/logout')
#@login_required
#def logout():
    #logout_user()
    #return redirect(url_for('auth.login'))

#@auth.route('/profile')
#@login_required
#def profile():
 #   return render_template("home.html", user=current_user)

@auth.route('/immobilieAnlegen', methods=['GET', 'POST'])
#@login_required
def immobilieAnlegen():
    if request.method == 'POST':
        SellerID = 1 #current_user.userID
        Straße = request.form.get('straße')
        Hausnummer = request.form.get('hausnummer')
        Ort = request.form.get('ort')
        PLZ = request.form.get('plz')
        Beschreibung = request.form.get('beschreibung')
        Gesamtwert= int(request.form.get('preis'))
        AnzahlTokens = 10000
        Preis = float(Gesamtwert/AnzahlTokens)
        VerfügbareAnteile = int(request.form.get('prozentanteil'))
        img = request.files['img']
        filename = secure_filename(img.filename)

        #directory = '%s'%os.getcwd
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/images")
        #= "C:/Users/mariu/OneDrive/Dokumente/DHBW/Semester6/Projektkonzeption/Test/Flask-Web-App-Tutorial/website/static/images"
        img.save(os.path.join(UPLOAD_FOLDER, filename))
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "chaindomain.db")
        con = sqlite3.connect(db_path)
        cursor= con.cursor()
        #new_property = Property(sellerID=SellerID,straße=Straße,hausnummer=Hausnummer,ort=Ort,plz=PLZ,beschreibung=Beschreibung,preis=Preis,anzahlTokens=AnzahlTokens,verfügbareAnteile=VerfügbareAnteile,img=filename)
        #db.session.add(new_property)
        #db.session.commit()      
        #cursor = get_db_connection()
        cursor.execute("INSERT INTO Property (sellerID,straße,hausnummer,ort,plz,beschreibung,preis,anzahlTokens,verfügbareAnteile,img) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (SellerID,Straße,Hausnummer,Ort,PLZ,Beschreibung,Preis,AnzahlTokens,VerfügbareAnteile,filename))
        con.commit()
        immobilienID = cursor.lastrowid
        con.close()

        besitzerTokens = AnzahlTokens-VerfügbareAnteile
        initialTransaction(SellerID,immobilienID,besitzerTokens,Preis)#Tokens des Besitzers
        initialOffer(SellerID,immobilienID,VerfügbareAnteile,Preis)#Tokens, die verkauft werden sollen
        zuverkaufendeTokens = str(VerfügbareAnteile)
        flash('Immobilie wurde gechained - momentan zu verkaufende Tokens:'+zuverkaufendeTokens, category='success')

    return render_template("home.html", user=current_user)

def initialTransaction(sellerID,immobilienID,AnzahlTokens,Preis):
    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    BuyerID = 0
    new_transaction = Transaction(sellerID=sellerID,buyerID=BuyerID,propertyID=immobilienID,anzahlTokens=AnzahlTokens,preisToken=Preis,datum=dt_string)
    db.session.add(new_transaction)
    db.session.commit() 

    #BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #db_path = os.path.join(BASE_DIR, "chaindomain.db")
    #con = sqlite3.connect(db_path)
    #cursor= con.cursor()
    #cursor.execute("INSERT INTO Transaction (sellerID,buyerID,propertyID,anzahlTokens,preisToken,datum) VALUES (?,?,?,?,?,?)",
    #        (sellerID,BuyerID,immobilienID,AnzahlTokens,Preis,dt_string))
    #con.commit
    #con.close()
    return


def initialOffer(sellerID,immobilienID,AnzahlTokens,preis):
    dt_string = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    BuyerID = 0
    new_offer = Offer(sellerID=sellerID,buyerID=BuyerID,propertyID=immobilienID,anzahlTokens=AnzahlTokens,preisToken=preis,datum=dt_string)
    db.session.add(new_offer)
    db.session.commit()
    #BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #db_path = os.path.join(BASE_DIR, "chaindomain.db")
    #con = sqlite3.connect(db_path)
    #cursor= con.cursor()
    #BuyerID = null
    #cursor.execute("INSERT INTO Offer (sellerID,buyerID,propertyID,anzahlTokens,preisToken,datum) VALUES (?,?,?,?,?,?)",
    #        (sellerID,BuyerID,immobilienID,AnzahlTokens,preis,dt_string))
    #con.commit
    #con.close()
    return

#@auth.route('/getUserTokens', methods=['GET', 'POST'])
#def getUserTokens():
#Datenbankabfrage nach SELECT anzahlTokens FROM Transaction WHERE user.id = current_user.id AND propertyID = session['immobilienID'] 
 #   return tokens

@auth.route('/angebotBuy', methods=['GET', 'POST'])
#@login_required
def buyOffer():
    if request.method == 'POST':
        immobilienID = session['immobilienID']
        sellerID = null
        preis = session['preis']
        AnzahlTokens = request.form.get('auswählen')
        immobilienID = session['immobilienID']
        # dd/mm/YY H:M:S
        dt_string = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        BuyerID = '5'#current_user.id
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "chaindomain.db")
        con = sqlite3.connect(db_path)
        cursor= con.cursor()
        cursor.execute("INSERT INTO Offer (sellerID,buyerID,propertyID,anzahlTokens,preisToken,datum) VALUES (?,?,?,?,?,?)",
            (sellerID,BuyerID,immobilienID,AnzahlTokens,preis,dt_string))
        cursor.commit
        cursor.close()
        flash('Angebot wurde erstellt', category='success')
    return render_template("immobilie.html")

@auth.route('/angebotSell', methods=['GET', 'POST'])
#@login_required
def sellOffer():
    if request.method == 'POST':
        immobilienID = session['immobilienID']
        sellerID = '6'#current_user.id
        preis = session['preis']
        AnzahlTokens = request.form.get('auswählen')
        immobilienID = session['immobilienID']
        # dd/mm/YY H:M:S
        dt_string = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        BuyerID = null#da verkauft werden soll
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "chaindomain.db")
        con = sqlite3.connect(db_path)
        cursor= con.cursor()
        cursor.execute("INSERT INTO Offer (sellerID,buyerID,propertyID,anzahlTokens,preisToken,datum) VALUES (?,?,?,?,?,?)",
            (sellerID,BuyerID,immobilienID,AnzahlTokens,preis,dt_string))
        cursor.commit
        cursor.close()
        flash('Angebot wurde erstellt', category='success')
    return render_template("immobilie.html")

def transaction(sellerID,buyerID,immobilienID,anzahlTokens,preis):
    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "chaindomain.db")
    con = sqlite3.connect(db_path)
    cursor= con.cursor()
    cursor.execute("INSERT INTO Transaction (sellerID,buyerID,propertyID,anzahlTokens,preisToken,datum) VALUES (?,?,?,?,?,?)",
            (sellerID,buyerID,immobilienID,anzahlTokens,preis,dt_string))
    cursor.commit
    cursor.close()
    flash('Angebot wurde erstellt', category='success')
    return true

#Real-Time-Datenbankabfrage alle 10 Sekunden
def offerAgreement():
    #datenbankzugriff PropertyId = PropertyId
    #buyOrSell != buyOrSell
    #Reihe der Offer nehmen und in Transaction abbilden
    #transaction(sellerID,buyerID,immobilienID,anzahlTokens,preis)
    return