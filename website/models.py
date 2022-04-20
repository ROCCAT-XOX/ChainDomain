from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class Offer(db.Model):

    offerId       = db.Column(db.Integer, primary_key=True)
    UserId        = db.Column(db.Integer, unique = True)
    PropertyId    = db.Column(db.Integer, unique = True)
    buyOrSell     = db.Column(db.Boolean)
    anzahlTokens  = db.Column(db.Integer)
    preisPerToken = db.Column(db.Float)

    
class Property(db.Model):
    propertyID  	    = db.Column(db.Integer,     primary_key=True)
    sellerID            = db.Column(db.Integer, unique = True)
    straße              = db.Column(db.String(120))
    hausnummer          = db.Column(db.String(12))
    ort                 = db.Column(db.String(120))
    plz                 = db.Column(db.Integer)
    beschreibung        = db.Column(db.Text)
    preis               = db.Column(db.Float)
    anzahlTokens        = db.Column(db.Integer)
    verfügbareAnteile   = db.Column(db.Float)
    #import os
    #from flask import Flask, flash, request, redirect, url_for
    #from werkzeug.utils import secure_filename
    #UPLOAD_FOLDER = '/path/to/the/uploads'
    
    #app = Flask(__name__)
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    img                 = db.Column(db.String(300), unique = True)
    


class Transaction(db.Model):
    transactionID   = db.Column(db.Integer,     primary_key=True)
    sellerID        = db.Column(db.Integer, unique = True)
    buyerID         = db.Column(db.Integer, unique = True)
    propertyID      = db.Column(db.Integer, unique = True)
    anzahlTokens    = db.Column(db.Integer)
    preisToken      = db.Column(db.Float)
    datum           = db.Column(db.DateTime)