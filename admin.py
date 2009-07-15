#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp, db
from google.appengine.api import users
from handlers.HandlerBase import HandlerBase
from models.ticket import Ticket

class TicketsHandler( HandlerBase ):
	""" Handles requests for the tickets page. """
	def get( self ):
		""" Handles HTTP GET requests. """
		query = Ticket.all()
		query.filter('financial_order_state =', 'CHARGEABLE')
		query.filter('production =', self.is_prod())
		query.order('-timestamp')
		active_tickets = query.fetch(250)
		
		query = Ticket.all()
		query.filter('financial_order_state !=', 'CHARGEABLE')
		query.filter('production =', self.is_prod())
		query.order('-financial_order_state')
		reviewing_tickets = query.fetch(250)
		
		options = self.get_options()
		options["active_tickets"] = active_tickets
		options["reviewing_tickets"] = reviewing_tickets
		options["logout_url"] = users.create_logout_url('/')
		options["content"] = self.render( "admin/tickets.html", options )
		self.response.out.write( self.render( "admin.html", options ) )


class MainHandler( HandlerBase ):
	""" Handles requests for the admin index page. """
	def get( self ):
		""" Handles HTTP GET requests. """
		options = self.get_options()
		options["content"] = self.render( "admin/index.html", options )
		options["logout_url"] = users.create_logout_url('/')
		self.response.out.write( self.render( "admin.html", options ) )


def main():
	application = webapp.WSGIApplication([
		('/admin/tickets', TicketsHandler),
		('/admin', MainHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
