#!/usr/bin/env python
# HandlerBase.py
# 

import os, time, re
from urlparse import urlparse
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import users
from models import featureset
from features import features
import settings

class HandlerBase( webapp.RequestHandler ):
	"""
		Base class for microtasking handlers of all sorts.
	"""

	def get_featureset( self, promo=None ):
		"""
			Grabs an appropriate featureset.
		"""
		# Short-circuit if a featureset has already been established
		if hasattr( self, "fs" ): return getattr( self, "fs" )
		allfeatures = features()
		
		# Parse out the first path segment and use it if it's a legit promo
		m = re.compile("^/?([^/\\?]*)").findall( self.request.path )
		path = m[0] or "default" if m and len(m) else None
		promo = path if path in allfeatures else None
		
		# If the path doesn't indicate a promotion, check params and cookies
		promo = promo or self.request.params.get("promo") or self.request.cookies.get("promo")
		
		# Retrieve featureset
		key = self.request.params.get("key") or self.request.cookies.get("key")
		fs = featureset.featureset( key, promo )
		
		# Set HTTP cookies to remember the key and promotion
		self.set_cookie( "key", fs.key().id_or_name() )
		if hasattr( fs, "promo" ): self.set_cookie( "promo", fs.promo )
		
		# Set local reference to featureset and return
		setattr( self, "fs", fs )
		return fs
	
	def get_options( self, promo=None ):
		"""
			Returns a safely modifiable dictionary based on the provided object.
		"""
		options = self.get_featureset(promo)._dynamic_properties.copy()
		if not hasattr( self, "data_options" ) or not isinstance( self.data_options, dict ): return options
		for k, v in self.data_options.iteritems(): options[k] = v
		return options
		
		
	def is_prod( self, override_prod=False ):
		if not hasattr(self, '__is_prod__'):
			self.__is_prod__ = override_prod or urlparse( self.request.url ).hostname == "www.microtasking.net"
		return self.__is_prod__
		
	def get_settings( self, override_prod=False ):
		"""
			Returns a settings hash appropriate to the environment.
		"""
		if hasattr( self, "ENV" ): return self.ENV
		env = settings.PRODUCTION if self.is_prod( override_prod=override_prod ) else settings.SANDBOX
		setattr( self, "ENV", env )
		return self.ENV
		
	def protect_sandbox( self ):
		"""
			Returns True if this is the Sandbox and the user is not an admin, so should
			stop rendering, False if it is ok to continue rendering the Handler
		"""
		options = self.get_options()
		sandbox = not(self.is_prod())
		if sandbox and not users.is_current_user_admin():
			options["content"] = self.render( "404.html", options )
			self.response.out.write( self.render( "outer.html", options ) )
			return True
		return False
	

	def set_cookie( self, name, value ):
		"""
			Simple cookie setting routine.
			Sets a cookie for 10 years in the future (forever).
		"""
		expires = time.time() + 60 * 60 * 24 * 365 * 10 # 10 years from today
		format = time.strftime( "%a, %d-%b-%Y 23:59:59 GMT", time.gmtime( expires ) )
		cookie = "%s=%s; expires=%s; path=/" % ( name, value, format )
		self.response.headers.add_header( "Set-Cookie", str( cookie ) )

	def template_path( self, name ):
		"""
			Gets the full path to a template by its name.
		"""
		return os.path.join( os.path.dirname( __file__ ), '..', 'templates', name )

	def render( self, name, options={} ):
		"""
			Gets and renders a given named template.
		"""
		return template.render( self.template_path( name ), options )


	def create( self, klass, attrs ):
		"""
			Creates a new class instance of type klass, and populate 
			attributes with names that match the attrs sequence (or list)
			via self.set(...)
			eg:
			  food = self.create( Breakfast, ('spam', 'eggs') )
		"""
		obj = klass()
		for attr in attrs:
			self.set( obj, attr )
		return obj

	def set( self, obj, attr ):
		"""
			Takes an object and sets an attribute with the same name of a similar
			self.request.get(...) field.
			eg:
			  self.set( food, 'rice' )
			is equivalent to
			  if self.request.get('rice'):
			    food.rice = self.request.get('rice').strip()
		"""
		val = self.request.get(attr)
		if val:
			val = val.strip()
			if hasattr( obj, attr ):
				setattr( obj, attr, val )

