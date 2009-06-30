#!/usr/bin/env python
# HandlerBase.py
# 

import os, time
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from models import featureset

class HandlerBase( webapp.RequestHandler ):
	"""
		Base class for microtasking handlers of all sorts.
	"""

	def get_featureset( self ):
		"""
			Grabs an appropriate featureset.
		"""
		if hasattr( self, "fs" ): return getattr( self, "fs" )
		fs = featureset.featureset(
			self.request.params.get("key") or self.request.cookies.get("key")
		)
		self.set_cookie( "key", fs.key().id_or_name() )
		setattr( self, "fs", fs )
		return fs
	
	def get_options( self ):
		"""
			Returns a safely modifiable dictionary based on this handlers feature set.
		"""
		return self.get_featureset()._dynamic_properties.copy()

	def set_cookie( self, name, value ):
		"""
			Simple cookie setting routine.
			Sets a cookie for 10 years in the future (forever).
		"""
		expires = time.time() + 60 * 60 * 24 * 365 * 10 # 10 years from today
		format = time.strftime( "%a, %d-%b-%Y 23:59:59 GMT", time.gmtime( expires ) )
		cookie = "%s=%s; expires=%s; path=/" % ( name, value, format )
		self.response.headers["Set-Cookie"] = str( cookie )

	def template_path( self, name ):
		"""
			Gets the full path to a template by its name.
		"""
		return os.path.join( os.path.dirname( __file__ ), 'templates/%s.html' % name )

	def render( self, name, options={} ):
		"""
			Gets and renders a given named template.
		"""
		return template.render( self.template_path( name ), options )

	def write_render( self, name, options={} ):
		"""
			Gets and renders a given named template and writes to the response.
		"""
		return self.response.out.write( self.render( name, options ) )


