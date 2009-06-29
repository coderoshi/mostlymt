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
import featureset

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
		return self.get()

def main():
	application = webapp.WSGIApplication([
		('/', MainHandler),
		('/checkout', CheckoutHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
