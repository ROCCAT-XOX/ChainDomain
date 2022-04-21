from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    #user_id = db.Column(db.Integer, db.ForeignKey('User.id'))


class User(db.Model, UserMixin):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    #notes = db.relationship('Note')

class Offer(db.Model):
    __tablename__ = 'Offer'

    offerId       = db.Column(db.Integer, primary_key=True)
    sellerID      = db.Column(db.Integer)
    buyerID       = db.Column(db.Integer)
    propertyID    = db.Column(db.Integer)
    anzahlTokens  = db.Column(db.Integer)
    preisToken    = db.Column(db.Float)
    datum         = db.Column(db.String(120))

    
class Property(db.Model):
    __tablename__ = 'Property'

    propertyID  	    = db.Column(db.Integer,     primary_key=True)
    name                = db.Column(db.String(120))
    sellerID            = db.Column(db.Integer)
    straße              = db.Column(db.String(120))
    hausnummer          = db.Column(db.String(12))
    ort                 = db.Column(db.String(120))
    plz                 = db.Column(db.Integer)
    beschreibung        = db.Column(db.Text)
    preis               = db.Column(db.Float)
    anzahlTokens        = db.Column(db.Integer)
    verfügbareAnteile   = db.Column(db.Float)
    img                 = db.Column(db.String(300), unique = True)
    


class Transaction(db.Model):
    __tablename__ = 'Transaction'

    transactionID   = db.Column(db.Integer,     primary_key=True)
    sellerID        = db.Column(db.Integer)
    buyerID         = db.Column(db.Integer)
    propertyID      = db.Column(db.Integer)
    anzahlTokens    = db.Column(db.Integer)
    preisToken      = db.Column(db.Float)
    datum           = db.Column(db.String(120))

class Besitz(db.Model): 
    __tablename__ = 'Besitz'
    besitzID        = db.Column(db.Integer, primary_key=True)
    userID          = db.Column(db.Integer)
    propertyID      = db.Column(db.Integer)
    anzahlToken     = db.Column(db.Integer)
    transactionID   = db.Column(db.Integer)