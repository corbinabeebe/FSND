from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form

#connect to a local postgresql database
db = SQLAlchemy()
def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
	__tablename__ = 'Venue'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False)
	city = db.Column(db.String(120), nullable=False)
	state = db.Column(db.String(120), nullable=False)
	address = db.Column(db.String(120), nullable=False)
	phone = db.Column(db.String(120), nullable=False)
	image_link = db.Column(db.String(500), default="https://i.imgur.com/FNlOjiR.jpg")
	facebook_link = db.Column(db.String(120))
	website = db.Column(db.String(), nullable=True)
	seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
	seeking_description = db.Column(db.String(), nullable=True)
	shows = db.relationship('Show', backref='Venue', lazy=True)
	genres = db.Column(db.ARRAY(db.String(120)), nullable=False)

class Artist(db.Model):
	__tablename__ = 'Artist'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	genres = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))
	website = db.Column(db.String(120), nullable=True)
	seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
	seeking_description = db.Column(db.String(), nullable=True)
	past_shows = db.relationship('Show', backref='Artist', lazy=True)
	genres = db.Column(db.ARRAY(db.String(120)), nullable=False)

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)