#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp, db
from handlers.HandlerBase import HandlerBase
from models.ticket import Ticket

class TicketsHandler( HandlerBase ):
	""" Handles requests for the tickets page. """
	def get( self ):
		""" Handles HTTP GET requests. """
		tickets = Ticket.all().order('-timestamp').fetch(250)
		options = self.get_options()
		options["tickets"] = tickets
		options["content"] = self.render( "tickets", options )
		self.response.out.write( self.render( "admin", options ) )

def main():
	application = webapp.WSGIApplication([
		('/tickets', TicketsHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()