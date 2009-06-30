#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid
import wsgiref.handlers
from google.appengine.ext.webapp import template
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
		return self.get()

class FAQHandler( HandlerBase ):
	""" Handles requests for the FAQ page. """
	def get( self ):
		options = self.get_options()
		options["content"] = self.render( "faq", options )
		self.response.out.write( self.render( "outer", options ) )

def main():
	application = webapp.WSGIApplication([
		('/', MainHandler),
		('/checkout', CheckoutHandler),
		('/faq', FAQHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
