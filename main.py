#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time
# expires = time.time() + 60 * 60 * 24 * 365 * 10 # 10 years from today
# format = time.strftime( "%a, %d-%b-%Y 23:59:59 GMT", time.gmtime( expires ) )
# cookie = "test=yes; expires=%s; path=/" % ( format, )
# self.response.headers["Set-Cookie"] = cookie

import os
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp, db

def template_path( name ):
	""" Gets the full path to a template by its name. """
	return os.path.join( os.path.dirname( __file__ ), 'templates/%s.html' % ( name, ) )

def render( name, options={} ):
	""" Gets and renders a given named template. """
	return template.render( template_path( name ), options )

class MainHandler( webapp.RequestHandler ):
	""" Handles requests for the main page. """
	def get( self ):
		""" Handles HTTP GET requests. """
		self.response.out.write( render( 'outer', {
			'title': 'We do stuff for you',
			'content': render( 'index', {} )
		} ) )

class CheckoutHandler( webapp.RequestHandler ):
	""" Handles requests for the checkout page. """
	def get( self ):
		self.response.out.write( render( 'outer', {
			'title': 'Checkout',
			'content': render( 'checkout', {} )
		} ) )

def main():
	application = webapp.WSGIApplication([
		('/', MainHandler),
		('/checkout', CheckoutHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
