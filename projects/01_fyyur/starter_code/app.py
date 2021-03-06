#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db_setup, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
	areas = db.session.query(Venue.city, Venue.state).order_by('state').all()
	data = []
	for area in areas:
		venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).order_by('name').all()
		v_data = []
		data.append({
			"city": area.city,
			"state": area.state,
			"venues": v_data
		})
		for venue in venues:
			shows = Show.query.filter_by(venue_id=venue.id).order_by('id').all()
			v_data.append({
				"id": venue.id,
				"name": venue.name,
				"num_upcoming_shows": len(shows)
			})
	return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
	search_term = request.form.get('search_term', '')
	new_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
	data = []

	for result in new_results:
		data.append({
			'id': result.id,
			'name': result.name,
			'num_upcoming_shows': len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > str(datetime.now())).all()),
		})

	response={
    "count": len(new_results),
    "data": data
  }

	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
	venue = Venue.query.filter_by(id=venue_id).first_or_404()
	past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
		Show.venue_id == venue_id,
		Show.artist_id == artist_id,
		Show.start_time > str(datetime.now()).all()
	)
	data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "shows": venue.shows,
		"past_shows": [{
      "artist_id": aritst.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time
    } for artist, show in past_shows],
    "upcoming_shows": [{
			"artist_id": aritst.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time
		} for artist, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

	return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	try:	
		# add data from form to venue object
		venue = Venue(
			name = request.form.get('name'),
			city = request.form.get('city'),
			state = request.form.get('state'),
			address = request.form.get('address'),
			phone = request.form.get('phone'),
			genres = request.form.getlist('genres'),
			image_link = request.form.get('image_link'),
			facebook_link = request.form.get('facebook_link'),
			website = request.form.get('website'),
			seeking_talent = True if 'seeking_talent' in request.form else False,
			seeking_description = request.form.get('seeking_description')
		)
		db.session.add(venue)
		db.session.commit()
		flash('Venue ' + request.form['name'] + ' was successfully listed!') # on successful db insert, flash success
	except ValueError as e:
		print(e)
		# on unsuccessful db insert, flash an error instead.
		flash('Venue ' + request.form['name'] + ' was not listed!')
		db.session.rollback()
	finally:
		db.session.close()
	
	return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
	try:
		venue = Venue.query.get(venue_id)
		db.session.delete(venue)
		db.session.commit()
		flash('Venue ' + venue.name + ' was deleted!')
	except:
		db.session.rollback()
		flash('Venue ' + venue.name + ' was not deleted!')
	finally:
		db.session.close()
    
  # TODO: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
	return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

	search_term = request.form.get('search_term', '')
	new_results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
	
	data = []
	for result in new_results:
		data.append(result)

	response={
    "count": len(new_results),
    "data": data
  }

	return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# gets the artist at specified id
	artist = Artist.query.get(artist_id)

	# gets shows of artist with artist_id
	shows = Show.query.get(artist_id)

	def upcoming_shows():
		upcoming_shows = []

		if shows is not None:
			for show in shows:
				if show.start_time > datetime.now():
					upcoming_shows.append({
						"venue_id": show.venue_id,
						"venue_name": show.Venue.name,
						"venue_image_link": show.Venue.image_link,
						"start_time": format_datetime(str(show.start_time))
					})
		return upcoming_shows

	def past_shows():
		past_shows = []

		if shows is not None:
			for show in shows:
				if show.start_time < datetime.now():
					past_shows.append({
						"venue_id": show.venue_id,
						"venue_name": show.venue.name,
						"venue_image_link": show.venue.image_link,
						"start_time": format_datetime(str(show.start_time))
					})
		return past_shows
  # shows the artist page with the given artist_id
	data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
  	"website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows(),
    "upcoming_shows": upcoming_shows(),
    "past_shows_count": len(past_shows()),
    "upcoming_shows_count": len(upcoming_shows()),
  }
 
	return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()

	# gets artist by id
	artist = Artist.query.get(artist_id)

	if artist is not None:
		form.name.data = artist.name
		form.genres.data = artist.genres
		form.city.data = artist.city
		form.state.data = artist.state
		form.phone.data = artist.phone
		form.website.data = artist.website
		form.facebook_link.data = artist.facebook_link
		form.seeking_venue.data = artist.seeking_venue
		form.seeking_description.data = artist.seeking_description
		form.image_link.data = artist.image_link

	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # artist record with ID <artist_id> using the new attributes
	form = ArtistForm()
	try:
		artist = Artist.query.get(artist_id)

		artist.name = form.request.get('name')
		aritst.city = form.request.get('city')
		artist.state = form.request.get('state')
		artist.phone = form.request.get('phone')
		artist.genres = form.request.getlist('genres')
		artist.facebook_link = form.request.get('facebook_link')
		artist.website = form.request.get('website')
		artist.seeking_venue = True if 'seeking_venue' in request.form else False
		artist.seeking_description = request.form.get('seeking_description')

		db.session.commit()
		flash('Artist ' + request.form['name'] + ' was successfully updated!')

	except:
		db.session.rollback()
		flash('Artist ' + request.form['name'] + ' was not updated!')
	finally:
		db.session.close()

		return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()

	venue = Venue.query.get(venue_id)

	if artist is not None:
		form.name.data = venue.name
		form.genres.data = venue.genres
		form.city.data = venue.city
		form.state.data = venue.state
		form.phone.data = venue.phone
		form.website.data = venue.website
		form.facebook_link.data = venue.facebook_link
		form.seeking_talent.data = venue.seeking_talent
		form.seeking_description.data = venue.seeking_description
		form.image_link.data = venue.image_link

	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

	try:
		venue = Venue.query.get(venue_id)

		venue.name = form.request.get('name')
		venue.city = form.request.get('city')
		venue.state = form.request.get('state')
		venue.phone = form.request.get('phone')
		venue.genres = form.request.getlist('genres')
		venue.facebook_link = form.request.get('facebook_link')
		venue.website = form.request.get('website')
		venue.seeking_talent = True if 'seeking_talent' in request.form else False
		venue.seeking_description = request.form.get('seeking_description')

		db.session.commit()
		flash('Venue ' + request.form['name'] + ' was successfully updated!')

	except:
		db.session.rollback()
		flash('Venue ' + request.form['name'] + ' was not updated!')
	finally:
		db.session.close()
		# venue record with ID <venue_id> using the new attributes
	return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
	try:	
		# add data from form to venue object
		artist = Artist(
			name = request.form.get('name'),
			city = request.form.get('city'),
			state = request.form.get('state'),
			phone = request.form.get('phone'),
			genres = request.form.getlist('genres'),
			image_link = request.form.get('image_link'),
			facebook_link = request.form.get('facebook_link'),
			website = request.form.get('website'),
			seeking_venue = True if 'seeking_venue' in request.form else False,
			seeking_description = request.form.get('seeking_description')
		)
		db.session.add(artist)
		db.session.commit()
		flash('Artist ' + request.form['name'] + ' was successfully listed!') # on successful db insert, flash success
	except ValueError as e:
		print(e)
		# on unsuccessful db insert, flash an error instead.
		flash('Artist ' + request.form['name'] + ' was not listed!')
		db.session.rollback()
	finally:
		db.session.close()
  
	return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
	shows = db.session.query(Show).join(Artist).join(Venue).all()

	data = []

	for show in shows:
		data.append({
			"venue_id": show.venue_id,
			"artist_id": show.artist_id,
			"start_time": str(show.start_time)
		})
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
	return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	# called to create new shows in the db, upon submitting new show listing form
	error = False
	form = ShowForm()
	if form.validate:
		try:
			show = Show(
				venue_id = form['venue_id'].data,
				artist_id = form['artist_id'].data,
				start_time = form['start_time'].data
			)
			db.session.add(show)
			db.session.commit()
			
		except Exception as e:
			error = True
			db.session.rollback()
			
		finally:
			db.session.close()
	if error:
		flash('Show was not listed!')
	else:
		# on successful db insert, flash success
		flash('Show was successfully listed!')
	
	return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
