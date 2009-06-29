#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp, db
import featureset

def get_featureset( handler ):
	"""
		Grabs an appropriate featureset.
		Note: This is a good place to add debugging code to, say, force a given feature set for testing.
	"""
	fs = featureset.featureset( handler.request.params.get("key") or handler.request.cookies.get("key") )
	#fs.price = 11.99
	#fs.stylesheet = "contender"
	set_cookie( handler.response, "key", fs.key().id_or_name() )
	return fs
	
def get_options( fs ):
	"""
		Returns a safely modifiable dictionary from a FeatureSet.
	"""
	return fs._dynamic_properties.copy()

def set_cookie( response, name, value ):
	""" Simple cookie setting routine.  Sets a cookie for 10 years in the future. """
	expires = time.time() + 60 * 60 * 24 * 365 * 10 # 10 years from today
	format = time.strftime( "%a, %d-%b-%Y 23:59:59 GMT", time.gmtime( expires ) )
	cookie = "%s=%s; expires=%s; path=/" % ( name, value, format )
	response.headers["Set-Cookie"] = str(cookie)

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
		options = get_options( get_featureset( self ) )
		options["content"] = render( "index", options )
		self.response.out.write( render( "outer", options ) )

class CheckoutHandler( webapp.RequestHandler ):
	""" Handles requests for the checkout page. """
	def get( self ):
		options = get_options( get_featureset( self ) )
		options["content"] = render( "checkout", options )
		options["tagline"] = "Checkout"
		self.response.out.write( render( "outer", options ) )
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
