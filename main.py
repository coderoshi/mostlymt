#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid, logging, base64, re
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.api import mail, urlfetch
from google.appengine.ext import webapp, db
from handlers import HandlerBase
from models.ticket import Ticket
from xml.dom import minidom
import checkout

class MainHandler( HandlerBase ):
	""" Handles requests for the main page. """
	def get( self ):
		""" Handles HTTP GET requests. """
		options = self.get_options()
		options["content"] = self.render( "index.html", options )
		self.response.out.write( self.render( "outer.html", options ) )

class FAQHandler( HandlerBase ):
	""" Handles requests for the FAQ page. """
	def get( self ):
		options = self.get_options()
		options["content"] = self.render( "faq.html", options )
		self.response.out.write( self.render( "outer.html", options ) )

class GPayNotifyHandler( HandlerBase ):
  """ Handles google checkout callback """
  def get(self):
	self.post()
  
  def post(self):
	checkout_gn = checkout.GoogleNotified()
	if not self.request.body:
	  return
	checkout_gn.parse(self.request.body)
	
	if checkout_gn.new_purchase:
	
		ticket = db.get( db.Key( checkout_gn.ticket_key ) )
		
		# TODO: fail ticket if it isn't found - attempt to send error email to checkout_gn.email?
		if not ticket:
			logging.error('No idea what to do here... ticket not found for email \'%s\'' % checkout_gn.email)
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
		fields = ( 'email', 'name', 'phone', 'description', 'hours' )
		options = {}
		for field in fields: options[field] = getattr( ticket, field )
		
		# Create and send email message
		ENV = self.get_settings()
		message = mail.EmailMessage(
				sender=ENV['email-sender'],
				subject=ENV['email-subject'],
				to=ENV['email-to'],
				body=self.render( "messagebody.txt", options )
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

class CheckoutHandler( HandlerBase ):
  # redirect to checkout w/ error messages... flash-system similar to rails?
  """ Handles requests for the checkout page. """
  def get( self ):
	options = self.get_options()
	options["content"] = self.render( "checkout.html", options )
	options["tagline"] = "Checkout"
	self.response.out.write( self.render( "outer.html", options ) )
  
  def post(self):

	# Grab options
  	options = self.get_options()
  
  	# Form validation
	fields = ( 'email', 'name', 'phone', 'description' )
	any_errors = False
  	data = {}
  	for field in fields: data[field] = self.request.get( field ) or ""
  	
  #     # Check email
  #     if data["email"]:
  #     pattern = re.compile( "^\\s*[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\\s*$", re.I )
  #     if not pattern.match( data["email"] ):
  #       any_errors = True
  #       data["email_error"] = options["email_invalid"]
  # else:
  #   any_errors = True
  #   data["email_error"] = options["email_required"]
  #       
  #     # Check name
  #     if not data["name"]:
  #       any_errors = True
  #       data["name_error"] = options["name_required"]
  	
  	# Check description
  	if not data["description"] or len(data["description"]) < 20:
  		any_errors = True
  		data["description_error"] = options["description_too_short"]
  		
  	# If any data didn't validate, send them back through the MainHandler
  	if any_errors:
  		data["validation_error"] = options["please_check"]
	  	handler = MainHandler()
	  	handler.initialize( self.request, self.response )
	  	handler.data_options = data
	  	return handler.get()
	  	
	hours = '1'
	item_name = "%s Hour" % hours
	item_desc = "A microtask of %s hours time" % hours
	unit_price = options["price"]
	base_url = self.request.url[0 : len(self.request.url) - len(self.request.path)]
	return_url = "%s/%s" % ( base_url, options["promo"] or "" )
	
	# This is a PENDING ticket. Does not become 'active' until CC is Authorized
	ticket = self.create( Ticket, fields )
	ticket.put()
	
	ENV = self.get_settings()
	google_co = checkout.Google( item_name, item_desc, unit_price, 1, return_url, ticket.key() )
	google_co.fetch(ENV['google-co-username'], ENV['google-co-password'], ENV['google-co'])
	redirect_url = google_co.get_redirect_url()
	
	self.redirect(redirect_url, False)


def main():
	application = webapp.WSGIApplication([
		('/faq', FAQHandler),
		('/checkout', CheckoutHandler),
		('/gpaynotify', GPayNotifyHandler),
		('/.*', MainHandler), # must be listed last since this regex matches anything
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
