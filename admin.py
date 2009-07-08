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
		query = Ticket.all()
		query.filter('financial_order_state =', 'CHARGEABLE')
		query.order('-timestamp')
		active_tickets = query.fetch(250)
		
		query = Ticket.all()
		query.filter('financial_order_state !=', 'CHARGEABLE')
		query.order('-financial_order_state')
		reviewing_tickets = query.fetch(250)
		
		options = self.get_options()
		options["active_tickets"] = active_tickets
		options["reviewing_tickets"] = reviewing_tickets
		options["content"] = self.render( "tickets.html", options )
		self.response.out.write( self.render( "admin.html", options ) )

def main():
	application = webapp.WSGIApplication([
		('/admin/tickets', TicketsHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
