#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
import dateutil.parser
import babel
import collections
import collections.abc
from flask_migrate import Migrate

from datetime import datetime
collections.Callable = collections.abc.Callable

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# import models
from models import *

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
  return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Complete: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    area_list = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
    
    for area in area_list:
        venues_in_area = db.session.query(Venue).filter(Venue.city == area[0]).filter(Venue.state == area[1])
        print(venues_in_area)
        print(area[0], area[1])
        data.append({
            'city': area[0],
            'state': area[1],
            'venues': venues_in_area
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    print(f'search_term: "{search_term}"' )
    venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
    print(venues)
    data = []
    if venues:
        for venue in venues:
            data.append({
                'id': venue.id,
                'name': venue.name
                # 'num_upcoming_shows' : num_upcoming_shows
            })
            #response = {}
            results = {
                'count': len(venues),
                'data': data
            }
        print(data)
    else:
        return render_template('errors/404.html')
        
    return render_template('pages/search_venues.html', results=results, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # Done: replace with real venue data from the venues table, using venue_id
    
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
            Show.venue_id == venue_id,
            Show.artist_id == Artist.id,
            Show.start_time < datetime.now()
        ).\
        all()

    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
            Show.venue_id == venue_id,
            Show.artist_id == Artist.id,
            Show.start_time > datetime.now()
        ).\
        all()

    data = {
            'id': venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            'past_shows': [{
                'artist_id': artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for artist, show in past_shows],
            'upcoming_shows': [{
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for artist, show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
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
    # insert form data as a new Venue record in the db
    form = VenueForm(request.form)
    if form.validate_on_submit():
        try:
            venue = Venue(
                name=form.name.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            print(str(venue.name) + ' added.')
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('Error. Venue ' +
                form.name.data + ' could not be listed. ' + 'code ' + e)
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
        return render_template('forms/new_venue.html', form=form)

    return render_template('pages/home.html')


#  Edit Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    # Done: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Done: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(request.form)
    if form.validate_on_submit():
        try:
            venue.name = form.name.data
            venue.address = form.address.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website_link = form.website_link.data
            if form.seeking_talent.data:
                venue.seeking_talent = True
            else:
                venue.seeking_talent = False
            venue.seeking_description = form.seeking_description.data
            
            print(str(venue.name) + ' updated.')
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] +
                    ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('Error. Venue ' +
                    form.name.data + ' could not be listed. ' + 'code ' + e)
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    return redirect(url_for('show_venue', venue_id=venue_id))



#  Delete Venue
#  ----------------------------------------------------------------


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Done: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        # venue = Venue.query.get_or_404(venue_id)
        # db.session.delete(venue)  # or
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue ' + venue_id +
              ' was successfully deleted!')
    except ValueError as e:
        print(e)
        flash('Error. Venue ' +
              venue_id + ' could not be deleted. ' + 'code ' + e)
        db.session.rollback()
    finally:
        db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return None




#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
  # Done: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    print(f'search_term: "{search_term}"' )
    artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
    print(artists)
    data = []
    if artists:
        for artist in artists:
            data.append({
                'id': artist.id,
                'name': artist.name
            })
            results = {
                'count': len(artists),
                'data': data
            }
        print(data)
    else:
        return render_template('errors/404.html')
        
    return render_template('pages/search_artists.html', results=results, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # Done: replace with real artist data from the artist table, using artist_id
        
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
        filter(
            Show.venue_id == Venue.id,
            Show.artist_id == artist_id,
            Show.start_time < datetime.now()
        ).\
        all()

    upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
        filter(
            Show.venue_id == Venue.id,
            Show.artist_id == artist_id,
            Show.start_time > datetime.now()
        ).\
        all()

    data = {
            'id': artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            'past_shows': [{
                'venue_id': venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for venue, show in past_shows],
            'upcoming_shows': [{
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for venue, show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }

    return render_template('pages/show_artist.html', artist=data)



#  Edit Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Done: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(request.form)
    if form.validate_on_submit():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website_link = form.website_link.data
            if form.seeking_venue.data:
                artist.seeking_venue = True
            else:
                artist.seeking_venue = False
            artist.seeking_description = form.seeking_description.data

            print(str(artist.name) + ' updated.')
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')
        except ValueError as e:
            print(e)
            flash('Error. Artist ' +
                  form.name.data + ' could not be updated. ' + 'code ' + e)
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        print(str(message))
        flash('Errors ' + str(message))
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    
    return redirect(url_for('show_artist', artist_id=artist_id))



#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    if form.validate_on_submit():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            print(str(artist.name) + ' added.')
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('Error. Artist ' +
                  form.name.data + ' could not be listed. ' + 'code ' + e)
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        print(str(message))
        flash('Errors ' + str(message))
        return render_template('forms/new_artist.html', form=form)

    return render_template('pages/home.html')
 
  

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # Done: replace with real venues data.
    shows = Show.query.all()

    data = []
    if shows:
        for show in shows:
            data.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm()
    if form.validate_on_submit():
        try:
            show = Show(
                artist_id = form.artist_id.data,
                venue_id = form.venue_id.data,
                start_time = form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
            flash('Show on ' + request.form['start_time'] + ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('Error. Show date ' + form.start_time.data + ' could not be added.' + e)
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        print(str(message))
        flash('Errors ' + str(message))
        return render_template('forms/new_show.html', form=form)

    return render_template('pages/home.html')
 

#  ----------------------------------------------------------------
#  Error Handlers
#  ----------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
