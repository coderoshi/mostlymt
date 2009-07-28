#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid, logging, base64, re
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.api import mail, urlfetch, datastore_errors
from google.appengine.ext import webapp, db
from handlers import HandlerBase
from models.ticket import Ticket
from models.promo import Promo
from xml.dom import minidom
import checkout

class MainHandler( HandlerBase ):
	""" Handles requests for the main page. """
	def get( self ):
		""" Handles HTTP GET requests. """

		if self.protect_sandbox(): return
		
		# Parse out the first path segment and use it if it's a legit page template
		m = re.compile("^/?([^/\\?]*)").findall( self.request.path )
		path = m[0] or "main" if m and len(m) else "main"
		
		# Check whether template exists
		f = os.path.join( os.path.dirname( __file__ ), 'templates', 'pages', "%s.html" % path )
		if not os.path.exists( f ): path = "main"
		
		# Render desired page
		options = self.get_options()
		options["sandbox"] = not(self.is_prod())
		options["form"] = self.render( "form.html", options )
		options["content"] = self.render( "pages/%s.html" % path, options )
		self.response.out.write( self.render( "outer.html", options ) )

	def post(self):
		""" Handle HTTP POST requests. (formerly CheckoutHandler) """
		if self.protect_sandbox(): return
		
		# Grab options
		options = self.get_options()

		# Form validation
		fields = ( 'description', 'hours', 'additional' )
		any_errors = False
		data = {}
		for field in fields: data[field] = self.request.get( field ) or ""

		# Check description
		if not data["description"] or len(data["description"]) < 20:
			any_errors = True
			data["description_error"] = options["description_too_short"]
			
		# Coerce number of hours to legal value
		try:
			data["hours"] = int( data["hours"] )
			if data["hours"] < 1: data["hours"] = 1
			if data["hours"] > 4: data["hours"] = 4
		except TypeError:
			data["hours"] = 1
	
		# Check the "additional" ammount
		max_additional = options["max_additional"]
		if not data["additional"]: data["additional"] = 0.0
		try:
			data["additional"] = float(data["additional"])
			if data["additional"] < 0.0: data["additional"] = 0.0
			if data["additional"] > max_additional:
				any_errors = True
				data["additional_error"] = options["additional_too_high"]
		except ValueError:
			data["additional"] = 0.0
			
		# If any data didn't validate, send them back through the MainHandler
		if any_errors:
			data["validation_error"] = options["please_check"]
			self.data_options = data
			return self.get()

		suffix = "s" if data["hours"] > 1 else ""
		item_name = "%s Hour%s" % ( data["hours"], suffix )
		item_desc = "A microtask of %s hours time" % data["hours"]
		unit_price = options["price"]
		base_url = self.request.url[0 : len(self.request.url) - len(self.request.path)]
		# return_url = "%s/%s" % ( base_url, options["promo"] or "" )

		# This is a PENDING ticket. Does not become 'active' until CC is Authorized
		ticket = Ticket(
			description = data["description"],
			price = options["price"],
			hours = data["hours"],
			additional = data["additional"],
			total = options["price"] * data["hours"] + data["additional"]
		)
		ticket.production = self.is_prod()
		promo = Promo.find_promo(ticket.description)
		if promo:
			ticket.promo_code = promo.code
			ticket.hours = promo.hours
		ticket.put()
		
		return_url = "%s/ticket/%s" % ( base_url, str(ticket.key()) )
		
		if not promo:
			env = self.get_settings()
			google_co = checkout.Google(
				item_name, item_desc, unit_price, data["hours"],
				data["additional"], options["additional_name"], options["additional_desc"],
				return_url, ticket.key()
			)
			google_co.fetch(env['google-co-username'], env['google-co-password'], env['google-co'])
			redirect_url = google_co.get_redirect_url()
			
			self.redirect(redirect_url, False)
			
		else:
			self.redirect(return_url, False)
			
		

class TicketHandler( HandlerBase ):
	""" Handles requests for individual tickets """
	def post(self):
		if self.protect_sandbox(): return
		
		ticket_key = self.request.path[8:]
		ticket = db.get( db.Key( ticket_key ) )
		
		if self.request.get('name'): ticket.full_name = self.request.get('name')
		if self.request.get('email'): ticket.given_email = self.request.get('email')
		if self.request.get('street'): ticket.shipping_address_1 = self.request.get('street')
		if self.request.get('city'): ticket.shipping_city = self.request.get('city')
		if self.request.get('region'): ticket.shipping_region = self.request.get('region')
		if self.request.get('postal_code'): ticket.shipping_postal_code = self.request.get('postal_code')
		if self.request.get('country_code'): ticket.shipping_country_code = self.request.get('country_code')
		
		if not ticket.needs_completion():
			promo = Promo.find_by_code(ticket.promo_code)
			promo.used = True
			promo.put()
			
			ticket.financial_order_state = 'CHARGEABLE'
			
			# Create options hash from ticket standard fields
			# fields = ( 'email', 'name', 'phone', 'description', 'hours', 'additional' )
			options = {'email':ticket.email(), 'name':ticket.name(), 'description':ticket.description, 'hours':ticket.hours, 'additional':0}
			# for field in fields: options[field] = getattr( ticket, field )
			
			# Create and send email message
			env = self.get_settings( ticket.production )
			body = self.render( "messagebody.txt", options )
			message = mail.EmailMessage(
					sender=env['email-sender'],
					subject=env['email-subject'],
					to=env['email-to'],
					body=body
				)
			message.send()
		
		ticket.put()
		
		self.redirect(self.request.path, False)
		
	def get(self):
		if self.protect_sandbox(): return
		
		options = self.get_options()
		ticket_key = self.request.path[8:]
		try:
			options["ticket"] = db.get( db.Key( ticket_key ) )
			options["content"] = self.render( "ticket.html", options )
		except datastore_errors.BadKeyError:
			options["content"] = self.render( "404.html", options )
		options["sandbox"] = not(self.is_prod())
		self.response.out.write( self.render( "outer.html", options ) )


class GPayNotifyHandler( HandlerBase ):
  """ Handles google checkout callback """
  def get(self):
	self.post()
  
  def post(self):
	logging.info(self.request.body)
	if not self.request.body:
	  return
	checkout_gn = checkout.GoogleNotified()
	checkout_gn.parse(self.request.body)
	
	if checkout_gn.new_purchase:
	
		ticket = db.get( db.Key( checkout_gn.ticket_key ) )
		
		# TODO: fail ticket if it isn't found - attempt to send error email to checkout_gn.email?
		if not ticket:
			logging.error('No idea what to do here... ticket not found for email \'%s\'' % checkout_gn.billing_email)
			# 502?
			self.response.out.write('')
			return
			
		ticket.google_order_number = checkout_gn.order_number
		ticket.google_buyer_id = checkout_gn.buyer_id
		ticket.email_allowed = checkout_gn.email_allowed
		ticket.financial_order_state = checkout_gn.financial_order_state
		ticket.hours = checkout_gn.hours

		if checkout_gn.billing:
			ticket.billing_email = checkout_gn.billing_email
			ticket.billing_first_name = checkout_gn.billing_first_name
			ticket.billing_last_name = checkout_gn.billing_last_name
			ticket.billing_address_1 = checkout_gn.billing_address_1
			ticket.billing_address_2 = checkout_gn.billing_address_2
			ticket.billing_city = checkout_gn.billing_city
			ticket.billing_region = checkout_gn.billing_region
			ticket.billing_postal_code = checkout_gn.billing_postal_code
			ticket.billing_country_code = checkout_gn.billing_country_code
			
			ticket.email = ticket.billing_email
			ticket.name = "%s %s" % (ticket.billing_first_name, ticket.billing_last_name)

		if checkout_gn.shipping:
			ticket.shipping_email = checkout_gn.shipping_email
			ticket.shipping_first_name = checkout_gn.shipping_first_name
			ticket.shipping_last_name = checkout_gn.shipping_last_name
			ticket.shipping_address_1 = checkout_gn.shipping_address_1
			ticket.shipping_address_2 = checkout_gn.shipping_address_2
			ticket.shipping_city = checkout_gn.shipping_city
			ticket.shipping_region = checkout_gn.shipping_region
			ticket.shipping_postal_code = checkout_gn.shipping_postal_code
			ticket.shipping_country_code = checkout_gn.shipping_country_code
			
			ticket.email = ticket.shipping_email
			ticket.name = "%s %s" % (ticket.shipping_first_name, ticket.shipping_last_name)
			
		ticket.put()
		
		# Create options hash from ticket standard fields
		fields = ( 'email', 'name', 'phone', 'description', 'hours', 'additional' )
		options = {}
		for field in fields: options[field] = getattr( ticket, field )
		
		# Create and send email message
		env = self.get_settings( ticket.production )
		body = self.render( "messagebody.txt", options )
		message = mail.EmailMessage(
				sender=env['email-sender'],
				subject=env['email-subject'],
				to=env['email-to'],
				body=body
			)
		message.send()
	else:
		# The ticket sits in limbo until it is CHARGEABLE
		if checkout_gn.new_financial_order_state == 'CHARGEABLE':
			query = Ticket.all()
			query.filter('google_order_number =', checkout_gn.order_number)
			ticket = query.fetch(1)
			if ticket: 
				ticket = ticket[0]
				ticket.financial_order_state = 'CHARGEABLE'
				ticket.put()
		
	self.response.out.write('')


def main():
	application = webapp.WSGIApplication([
		('/gpaynotify', GPayNotifyHandler),
		('/ticket/.*', TicketHandler),
		('/.*', MainHandler), # must be listed last since this regex matches anything
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
