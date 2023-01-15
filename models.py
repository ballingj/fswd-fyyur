from app import db

#----------------------------------------------------------------------------#
# Models (See ER_diagram in the root directory of the project)
#----------------------------------------------------------------------------#

# Venue will be the Parent model
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # relations
    artists = db.relationship('Show', back_populates='venue')

    def __repr__(self):
        return f'<Venue {self.id!r}: {self.name!r}>'

# Artist will be the Child model
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # relations
    venues = db.relationship('Show', back_populates='artist')

    def __repr__(self):
        return f'<Artist {self.id!r}: {self.name!r}>'


# Show is the Association model
class Show(db.Model):
    __tablename__ = 'show'
    venue_id = db.Column(db.ForeignKey('venue.id'), primary_key=True)  # left - parent
    artist_id = db.Column(db.ForeignKey('artist.id'), primary_key=True)  # right - child
    start_time = db.Column(db.DateTime(), primary_key=True)
    venue = db.relationship('Venue', back_populates='artists')
    artist = db.relationship('Artist', back_populates='venues')

    def __repr__(self):
        return f'<Venue {self.venue.name!r} Artist {self.artist.name!r} Date {self.start_time!r}>'


#----------------------------------------------------------------------------#
# Perform flask db init, followed by flask db migrate, flask db upgrade in 
# the terminal
#----------------------------------------------------------------------------#

