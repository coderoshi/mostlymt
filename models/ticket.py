from google.appengine.ext import webapp, db

class Ticket( db.Expando ):
	email = db.EmailProperty()
	phone = db.PhoneNumberProperty()
	name = db.StringProperty()
	description = db.TextProperty()
	timestamp = db.DateTimeProperty(auto_now_add=True)
