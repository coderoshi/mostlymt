from google.appengine.ext import webapp, db

class Ticket( db.Model ):
	email = db.EmailProperty()
	phone = db.PhoneNumberProperty()
	name = db.StringProperty()
	description = db.TextProperty()
	hours = db.IntegerProperty(default=1)
	timestamp = db.DateTimeProperty(auto_now_add=True)
	google_order_number = db.StringProperty()
	google_buyer_id = db.StringProperty()
	email_allowed = db.BooleanProperty(default=True)
	financial_order_state = db.StringProperty()
	billing_email = db.EmailProperty()
	billing_first_name = db.StringProperty()
	billing_last_name = db.StringProperty()
	billing_address_1 = db.StringProperty()
	billing_address_2 = db.StringProperty()
	billing_city = db.StringProperty()
	billing_region = db.StringProperty()
	billing_postal_code = db.StringProperty()
	billing_country_code = db.StringProperty()
	shipping_email = db.EmailProperty()
	shipping_first_name = db.StringProperty()
	shipping_last_name = db.StringProperty()
	shipping_address_1 = db.StringProperty()
	shipping_address_2 = db.StringProperty()
	shipping_city = db.StringProperty()
	shipping_region = db.StringProperty()
	shipping_postal_code = db.StringProperty()
	shipping_country_code = db.StringProperty()
	
	def first_name( self ):
		if self.shipping_first_name: return self.shipping_first_name
		if self.billing_first_name: return self.billing_first_name
		return ''

	def last_name( self ):
		if self.shipping_last_name: return self.shipping_last_name
		if self.billing_last_name: return self.billing_last_name
		return ''
	
	def name( self ):
		return "%s %s" % (self.first_name(), self.last_name())
	
	def email( self ):
		if self.shipping_email: return self.shipping_email
		if self.billing_email: return self.billing_email
		return ''
	
	def street_address( self ):
		addr = ''
		if self.shipping_address_1: 
			addr += self.shipping_address_1
		
		if self.shipping_address_2:
			addr += ' '
			addr += self.shipping_address_2
		
		if addr: return addr
		
		if self.billing_address_1: 
			addr += self.billing_address_1
		
		if self.billing_address_2:
			addr += ' '
			addr += self.billing_address_2
		
		if addr: return addr
		return ''
	
	def city( self ):
		if self.shipping_city: return self.shipping_city
		if self.billing_city: return self.billing_city
		return ''
		
	def region( self ):
		if self.shipping_region: return self.shipping_region
		if self.billing_region: return self.billing_region
		return ''
	
	def postal_code( self ):
		if self.shipping_postal_code: return self.shipping_postal_code
		if self.billing_postal_code: return self.billing_postal_code
		return ''
	
	def country_code( self ):
		if self.shipping_country_code: return self.shipping_country_code
		if self.billing_country_code: return self.billing_country_code
		return ''
	

