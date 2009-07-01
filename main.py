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
from handlers import HandlerBase
from models.ticket import Ticket

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
		fields = ('email', 'name', 'phone', 'description')
		ticket = self.create( Ticket, fields )
		ticket.put()
		
		options = {}
		for field in fields: options[field] = getattr( ticket, field )
		
		message = mail.EmailMessage(sender="eric.redmond@gmail.com",
		                            subject="Someone gave you a task")
		
		message.to = "Jim Wilson <wilson.jim.r@gmail.com>, Eric Redmond <eric.redmond@gmail.com>"
		message.body = self.render( "messagebody", options )
		
		message.send()
		
		return self.get()

def main():
	application = webapp.WSGIApplication([
		('/faq', FAQHandler),
		('/checkout', CheckoutHandler),
		('/.*', MainHandler), # must be listed last since this regex matches anything
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
