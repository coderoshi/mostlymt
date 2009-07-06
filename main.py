#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid, logging, base64
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
    
    # TODO: save more purchase notification data to ticket
    
    if checkout_gn.new_purchase:
      
      ticket = Ticket.all().filter('email =', checkout_gn.email).order('-timestamp').fetch(1)
      if ticket:
        ticket = ticket[0]
        
        # Create options hash from ticket standard fields
        fields = ( 'email', 'name', 'phone', 'description' )
        options = {}
        for field in fields: options[field] = getattr( ticket, field )
        
        # Create and send email message
        message = mail.EmailMessage(
          sender="eric.redmond@gmail.com",
                subject="Someone gave you a task",
                to="Jim Wilson <wilson.jim.r@gmail.com>, Eric Redmond <eric.redmond@gmail.com>",
                body=self.render( "messagebody.txt", options )
            )
        message.send()
      else:
        logging.error('No idea what to do here... email \'%s\' doesn\'t match active ticket' % checkout_gn.email)
    
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
    hours = '1'
    item_name = "%s Hour" % hours
    item_desc = "A microtask of %s hours time" % hours
    unit_price = '11.99'
    return_url = 'http://mostlymt.appspot.com/'
    
    # This is a PENDING ticket. Does not become 'active' until CC is Authorized
    fields = ( 'email', 'name', 'phone', 'description' )
    ticket = self.create( Ticket, fields )
    ticket.put()
    
    google_co = checkout.Google(item_name, item_desc, unit_price, return_url)
    url = 'https://sandbox.google.com/checkout/api/checkout/v2/merchantCheckout/Merchant/875093275712045'
    google_co.fetch('875093275712045','qNztxsdPtwA9f_dICQmjhg', url)
    redirect_url = google_co.get_redirect_url()
    
    self.redirect(redirect_url, False)


# class CheckoutHandler( HandlerBase ):
# 
#   def post( self ):
#   
#     # TODO: Form checking
# 
#     # Create ticket, pulling required fields from form data, tacking on feature values
#     fields = ( 'email', 'name', 'phone', 'description' )
#     ticket = self.create( Ticket, fields )
#     for k, v in self.get_options().iteritems():
#       if not hasattr( ticket, k ): setattr( ticket, k, v )
#     ticket.put()
# 
#     # Create options hash from ticket standard fields
#     options = {}
#     for field in fields: options[field] = getattr( ticket, field )
# 
#     # Create and send email message
#     message = mail.EmailMessage(
#       sender="eric.redmond@gmail.com",
#             subject="Someone gave you a task",
#             to="Jim Wilson <wilson.jim.r@gmail.com>, Eric Redmond <eric.redmond@gmail.com>",
#             body=self.render( "messagebody", options )
#         )
#     message.send()
#     
#     return self.get()

def main():
	application = webapp.WSGIApplication([
		('/faq', FAQHandler),
    # ('/checkout', CheckoutHandler),
		('/checkout', CheckoutHandler),
		('/gpaynotify', GPayNotifyHandler),
		('/.*', MainHandler), # must be listed last since this regex matches anything
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
