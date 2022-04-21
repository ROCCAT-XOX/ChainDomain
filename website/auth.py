from msilib.schema import Property
import os
from datetime import date, datetime
import sqlite3
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from sqlalchemy import null, true
from .models import Besitz, User,Property,Transaction,Offer
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/marketplace', methods=['GET', 'POST'])
@login_required
def marketplace():
    all_offers = Offer.query.all()

    id_immo = []
    immos = []

    for offer in all_offers :
        cur_prop = offer.propertyID
        of_preis = offer.preisToken
        of_menge = offer.anzahlTokens
        of_id = offer.offerId
        single_offer = [cur_prop,of_preis,of_menge,of_id]
        id_immo.append(single_offer)


    for entry in id_immo :
        cur_im_id = entry[0]
        cur_immo = Property.query.filter_by(propertyID= cur_im_id).first()
        straße = cur_immo.straße
        ort = cur_immo.ort
        plz = cur_immo.plz
        hausnummer = cur_immo.hausnummer
        beschreibung = cur_immo.beschreibung
        preis = entry[1]
        anzahlTokens = cur_immo.anzahlTokens
        verfügbareAnteile = entry[2]
        img = cur_immo.img
        offer = entry[3]
        name = cur_immo.name
        
        immo = [straße,ort,plz,hausnummer,beschreibung,preis,anzahlTokens,verfügbareAnteile,img,offer,name]
        
        immos.append(immo)
   
    return render_template("marketplace.html",user = current_user,immos = immos)

@auth.route('/oke')

def oke():

    all_offers = Offer.query.all()

    id_immo = []
    immos = []

    for offer in all_offers :
        cur_prop = offer.propertyID
        id_immo.append(cur_prop)


    for entry in id_immo :
        cur_im_id = entry
        cur_immo = Property.query.filter_by(propertyID= cur_im_id).first()
        straße = cur_immo.straße
        ort = cur_immo.ort
        plz = cur_immo.plz
        hausnummer = cur_immo.hausnummer
        beschreibung = cur_immo.beschreibung
        preis = cur_immo.preis
        anzahlTokens = cur_immo.anzahlTokens
        verfügbareAnteile = cur_immo.verfügbareAnteile
        img = cur_immo.img
        
        immo = [straße,ort,plz,hausnummer,beschreibung,preis,anzahlTokens,verfügbareAnteile,img]
        
        immos.append(immo)



    return oke

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
               
                login_user(user, remember=True)
                return redirect(url_for("auth.marketplace"))
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

@auth.route('/assets', methods=['GET', 'POST'])
@login_required
def assets():
    this_userID = current_user.id
    all_assets = Besitz.query.filter_by(userID = this_userID).all()

    alle_ass = []

    for ass in all_assets:
        ein_ass = []
        ass_id = ass.besitzID
        ass_tok = ass.anzahlToken
        prop_id = ass.propertyID
        trans_id = ass.transactionID 
        prop = Property.query.filter_by(propertyID = prop_id).first()
        trans = Transaction.query.filter_by(transactionID = trans_id).first()
        ass_preis = trans.preisToken
        ass_name = prop.name
        ass_dat = trans.datum
        ass_org = prop.preis
        ass_tot = prop.anzahlTokens
        all_trans = Transaction.query.filter_by(propertyID = prop_id).all()
        latest_trans = all_trans[(len(all_trans)-1)]
        ass_lat = latest_trans.transactionID
        ass_new = latest_trans.preisToken 

        ein_ass.append(ass_tok)
        ein_ass.append(ass_preis)
        ein_ass.append(ass_name)
        ein_ass.append(ass_dat)
        ein_ass.append(ass_org)
        ein_ass.append(ass_tot)
        ein_ass.append(ass_lat)
        ein_ass.append(ass_new)
        ein_ass.append(prop_id)
        ein_ass.append(ass_id)

        alle_ass.append(ein_ass)

        if request.method == "POST" :
            sell_preis = request.form.get('price')
            sell_meng = request.form.get('am_sell')
            sell_prop = request.form.get('propId')
            sell_besitz = request.form.get('besitzId')
            
            cur_date = date.today()

            userID = current_user.id

            new_offer = Offer(sellerID=userID,buyerID=0,propertyID=sell_prop,anzahlTokens=sell_meng,preisToken=sell_preis,datum=cur_date)
        
            db.session.add(new_offer)
            db.session.commit()


            alter_besitz = Besitz.query.filter_by(besitzID= sell_besitz).one()
            tok_be = int(alter_besitz.anzahlToken)
            sell_meng = int(sell_meng)
            diff = tok_be - sell_meng
            alter_besitz.anzahlToken = diff
            db.session.commit()

            flash('Ihr Verkauf wurde veranslasst', category='success')
            return render_template('base.html', user=current_user)






    return render_template("assets.html",user = current_user,assets = alle_ass)

@auth.route('/immobilie', methods=['GET', 'POST'])
@login_required
def immobilie():
    if request.method == 'GET':
        immobilienID = request.args.get('immobilienID', None)#so kriegt man Daten aus Jinja von der HTML-Seite
        return render_template("immobilie.html", immobilienID=immobilienID)

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
@login_required
def immobilieAnlegen():
    if request.method == 'POST':
        name = request.form.get('name')
        SellerID = current_user.id
        Straße = request.form.get('straße')
        Hausnummer = request.form.get('hausnummer')
        Ort = request.form.get('ort')
        PLZ = request.form.get('plz')
        Beschreibung = request.form.get('beschreibung')
        Gesamtwert= int(request.form.get('preis'))
        VerfügbareAnteile = int(request.form.get('prozentanteil'))
        AnzahlTokens = VerfügbareAnteile
        prozentsatz = Gesamtwert*0.49
        Preis = float(prozentsatz/AnzahlTokens)
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
        cursor.execute("INSERT INTO Property (name,sellerID,straße,hausnummer,ort,plz,beschreibung,preis,anzahlTokens,verfügbareAnteile,img) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (name,SellerID,Straße,Hausnummer,Ort,PLZ,Beschreibung,Preis,AnzahlTokens,VerfügbareAnteile,filename))
        con.commit()
        immobilienID = cursor.lastrowid
        con.close()

        besitzerTokens = AnzahlTokens-VerfügbareAnteile
        initialTransaction(SellerID,immobilienID,besitzerTokens,Preis)#Tokens des Besitzers
        initialOffer(SellerID,immobilienID,VerfügbareAnteile,Preis)#Tokens, die verkauft werden sollen
        zuverkaufendeTokens = str(VerfügbareAnteile)
        flash('Immobilie wurde gechained - momentan zu verkaufende Tokens: '+zuverkaufendeTokens, category='success')

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

@auth.route('/testuser')
def testuser():
    email = 'moritz.backhaus@gmx.de'
    password = generate_password_hash('1234567')
    first_name = 'Moritz'
    new_user = User(email=email,password=password,first_name=first_name)
    db.session.add(new_user)
    db.session.commit()
    return 'User'

@auth.route('/testoffer')
def testoffer():
    sellerID      = 11
    propertyID    = 7
    anzahlTokens  = 10000
    preisToken    = 900
    dt_string = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    BuyerID = 99
    new_offer = Offer(sellerID=sellerID,buyerID=BuyerID,propertyID=propertyID,anzahlTokens=anzahlTokens,preisToken=preisToken,datum=dt_string)
    db.session.add(new_offer)
    db.session.commit()
    return 'Offer'

@auth.route('/testproperty')
def testproperty():
    
    name                = 'Schönes MFH'
    sellerID            = 55
    straße              = "H2"
    hausnummer          = "6"
    ort                 = "Mannheim"
    plz                 = 68159
    beschreibung        = "Töfte hier"
    preis               = 300
    anzahlTokens        = 10000
    verfügbareAnteile   = 4999
    img                 = "YOLO.jpg"
    new_property = Property(name=name,sellerID=sellerID,straße=straße,hausnummer=hausnummer,ort=ort,plz=plz,beschreibung=beschreibung,preis=preis,anzahlTokens=anzahlTokens,verfügbareAnteile=verfügbareAnteile,img=img)
    db.session.add(new_property)
    db.session.commit()
    return 'Property'

@auth.route('/testtransaction')
def testtransaction():
    
    sellerID        = 44
    BuyerID         = 33
    immobilienID     = 8
    AnzahlTokens    = 1235
    Preis      = 250
    dt_string = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    BuyerID = 0
    new_transaction = Transaction(sellerID=sellerID,buyerID=BuyerID,propertyID=immobilienID,anzahlTokens=AnzahlTokens,preisToken=Preis,datum=dt_string)
    db.session.add(new_transaction)
    db.session.commit()
    return 'Transaction'

#Besitz test
@auth.route('/testbesitz')
def testbesitz():
        
        userID          = 1
        propertyID      = 1
        anzahlToken     = 1
        transactionID   = 1
        transactionID   = 1
        propertyID      = 1
        new_besitzer = Besitz(userID=userID, propertyID=propertyID, anzahlToken=anzahlToken, transactionID=transactionID)
            
        db.session.add(new_besitzer)
        db.session.commit()
        return 'ok'

@auth.route('/sell',methods=['GET' , 'POST'])
@login_required

def sell():
    this_userID = current_user.id

    all_offers = Offer.query.filter_by(sellerID = this_userID).all()

    all_off = []

    for off in all_offers :
        single_off = []
        prop_id = off.propertyID
        a_tok = off.anzahlTokens
        p_tok = off.preisToken
        off_d = off.datum

        prop = Property.query.filter_by(propertyID = prop_id).first()
        name = prop.name
        img = prop.img

        single_off.append(name)
        single_off.append(a_tok)
        single_off.append(p_tok)
        single_off.append(off_d)
        single_off.append(img)

        all_off.append(single_off)

    return render_template("sell.html",user = current_user,all_off = all_off)

@auth.route('/viewbuy',methods=['GET' , 'POST'])
@login_required
def viewbuy():
    if request.method == "GET" :
        args = request.args
        offerId = args.get('offerId')


        this_offer = Offer.query.filter_by(offerId = offerId).first()
        this_prop_id = this_offer.propertyID
        this_prop = Property.query.filter_by(propertyID  = this_prop_id).first()

        #offer infos
        for_view = []

        preis         = this_offer.preisToken
        sellerID      = this_offer.sellerID
        this_seller   = User.query.filter_by(id  = sellerID).first()
        name          = this_seller.first_name
        anzahlTokens  = this_offer.anzahlTokens
        datum         = this_offer.datum

        #immo infos

        straße              = this_prop.straße
        hausnummer          = this_prop.hausnummer
        ort                 = this_prop.ort
        plz                 = this_prop.plz
        beschreibung        = this_prop.beschreibung
        preis_org           = this_prop.preis
        anzahlTokens_org    = this_prop.anzahlTokens
        img                 = this_prop.img
        name_prop           = this_prop.name

        for_view.append(preis)
        for_view.append(name)
        for_view.append(anzahlTokens)
        for_view.append(datum)
        for_view.append(straße)
        for_view.append(hausnummer)
        for_view.append(ort)
        for_view.append(plz)
        for_view.append(beschreibung)
        for_view.append(preis_org)
        for_view.append(anzahlTokens_org)
        for_view.append(img)
        for_view.append(name_prop)
        for_view.append(offerId)


        return render_template("immobilie.html",user = current_user, for_view = for_view)

    if request.method == "POST" :
        mng_tokens = request.form.get('menge_tokens')
        this_offerId = request.form.get('offerId')
        this_offer = Offer.query.filter_by(offerId = this_offerId).first()
        
        userID = current_user.id

        avail_token = this_offer.anzahlTokens
        seller = this_offer.sellerID
        prop = this_offer.propertyID
        preis = this_offer.preisToken
        datum = date.today()

        


        new_transaction = Transaction(sellerID=seller,buyerID=userID,propertyID=prop,anzahlTokens=mng_tokens,preisToken=preis,datum=datum)
        
        db.session.add(new_transaction)
        db.session.commit()

        #session.refresh(new_transaction)
        trans_key = new_transaction.transactionID


        new_besitz = Besitz(userID =userID,propertyID = prop,anzahlToken = mng_tokens,transactionID =trans_key)

        db.session.add(new_besitz)
        db.session.commit()
    
        check_1 = int(mng_tokens)
        check_2 = int(avail_token)
        if (check_1<check_2) :
            diff = check_2-check_1
            besitzID = 2

            alter_offer = Offer.query.filter_by(offerId= this_offerId).one()
            alter_offer.anzahlTokens = diff
            db.session.commit()

            alter_besitz = Besitz.query.filter_by(besitzID= besitzID).one()
            alter_besitz.anzahlToken = diff
            db.session.commit()
          
            
        else :
            besitzID = 2
            
            del_offer = Offer.query.filter_by(offerId= this_offerId).one()
            db.session.delete(del_offer)
            db.session.commit()

            del_besitz = Besitz.query.filter_by(besitzID= 1).one()
            db.session.delete(del_besitz)
            db.session.commit()

        flash('Ihr Kauf wurde durchgeführt', category='success')
        return render_template('marketplace.html', user=current_user)

@auth.route('/buy')
def buy():

        #besitz aus session hier eine form triggern
        offerID = 1 #aus get
        besitzID =1 #auch

        besitzID        = 1
        userID          = 1
        propertyID      = 1
        anzahlToken     = 1
        transactionID   = 1

        #transaction

        transactionID   = 1
        sellerID        = 2
        buyerID         = 1
        propertyID      = 1
        anzahlTokens    = 1
        preisToken      = 1
        datum           =   str(date.today())

        new_besitz = Besitz(userID =userID,propertyID = propertyID,anzahlToken = anzahlToken,transactionID =transactionID)

        db.session.add(new_besitz)
        db.session.commit()
       
        new_transaction = Transaction(sellerID=sellerID,buyerID=buyerID,propertyID=propertyID,anzahlTokens=anzahlTokens,preisToken=preisToken,datum=datum)
        
        db.session.add(new_transaction)
        db.session.commit()

          
        mengeTokenswahl = 1
        mengeTokensmax = 1
        if (mengeTokenswahl<mengeTokensmax) :
            diff = mengeTokensmax-mengeTokenswahl
            besitzID = 2

            alter_offer = Offer.query.filter(offerId= offerID).one()
            alter_offer.anzahlTokens = diff
            db.session.commit()

            alter_besitz = Besitz.query.filter(besitzID= besitzID).one()
            alter_besitz.anzahlToken = diff
            db.session.commit()
          
            
        else :
            besitzID = 2
            
            del_offer = Offer.query.filter_by(offerId= offerID).one()
            db.session.delete(del_offer)
            db.session.commit()

            del_besitz = Besitz.query.filter_by(besitzID= 1).one()
            db.session.delete(del_besitz)
            db.session.commit()
        return "ok"

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