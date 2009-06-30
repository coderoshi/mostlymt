#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext import webapp, db
from HandlerBase import HandlerBase
from models.tickets import Tickets

class MainHandler( HandlerBase ):
	""" Handles requests for the main page. """
	def get( self ):
		""" Handles HTTP GET requests. """
		options = self.get_options()
		options["content"] = self.render( "index", options )
		self.response.out.write( self.render( "outer", options ) )

class FAQHandler( HandlerBase ):
	""" Handles requests for the FAQ page. """
	def get( self ):
		options = self.get_options()
		options["content"] = self.render( "faq", options )
		self.response.out.write( self.render( "outer", options ) )

class CheckoutHandler( HandlerBase ):
	""" Handles requests for the checkout page. """
	def get( self ):
		options = self.get_options()
		options["content"] = self.render( "checkout", options )
		options["tagline"] = "Checkout"
		self.response.out.write( self.render( "outer", options ) )

	def post( self ):
		ticket = self.create( Tickets, ('email', 'name', 'phone', 'description') )
		ticket.put()
		
		message = mail.EmailMessage(sender="eric.redmond@gmail.com",
		                            subject="Someone gave you a task")
		
		message.to = "Jim Wilson <wilson.jim.r@gmail.com>, Eric Redmond <eric.redmond@gmail.com>"
		message.body = """Dear Sirs:

Please perform the following task for %s <%s>

%s""" % (ticket.name, str(ticket.email), ticket.description)
		
		message.send()
		
		return self.get()

def main():
	application = webapp.WSGIApplication([
		('/', MainHandler),
		('/faq', FAQHandler),
		('/checkout', CheckoutHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
