#!/usr/bin/env python
# main.py
# 
# Copy pasta:
# import time

import os, yaml, random, time, uuid, logging, base64
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext import webapp, db
from handlers import HandlerBase
from models.ticket import Ticket
from xml.dom import minidom


def first_el(dom, str):
  if dom:
    tag = dom.getElementsByTagName(str)
    if tag and tag[0]: return tag[0]
  return None

def el_val(el):
  if el and el.firstChild: return el.firstChild.data
  return ''

def first_el_val(dom, str):
  return el_val(first_el(dom, str))


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

class GPayNotifyHandler( webapp.RequestHandler ):
  """ Handles google checkout callback """
  def get(self):
    self.post()
  
  def post(self):
    logging.debug(self.request.body)
    
    body = self.request.body
    
    dom = minidom.parseString(body)
    
    non_el = first_el(dom, 'new-order-notification')
    if non_el:
      #bid = first_el_val(non_el, 'buyer-id')
      gon = first_el_val(non_el, 'google-order-number')
      
      bba_el = first_el(non_el, 'buyer-billing-address')
      email = first_el_val(bba_el, 'email')  # get the user who made this purchase
      
      account = get_account_by_user(email)
      
      purchase = vm.Purchase(account=account)
      purchase.order_number = gon
      
      sc_el = first_el(non_el, 'shopping-cart')
      item_el = first_el(sc_el, 'item')
      item_name = first_el_val(item_el, 'item-name')
      unit_price = first_el_val(item_el, 'unit-price')
      
      # TODO: This should be managed by the DB in memcache
      tokens = 0
      if item_name == '20 tokens':    tokens = 20
      if item_name == '110 tokens':   tokens = 110
      if item_name == '250 tokens':   tokens = 250
      if item_name == '1000 tokens':  tokens = 1000
      
      purchase.tokens = tokens
      purchase.save()
      
      logging.debug('Save Purchases')
    else:
      oscn_el = first_el(dom, 'order-state-change-notification')
      gon = first_el_val(oscn_el, 'google-order-number')
      nfos_val = first_el_val(oscn_el, 'new-financial-order-state')
      if nfos_val == 'CHARGED':
        # set charged == True
        query = Purchase.all()
        query.filter('order_number =', gon)
        purchase = query.fetch(1)
        if purchase:
          purchase = purchase[0]
        else:
          #throw some exception?
          # TODO: Make a new purchase if not exists - set status to PURCHASE_CHARGED_UNSET ?
          logging.error('Trying to charge an unmade purchase')
          return
        
        # no need to make a change if tokens already added
        if purchase.order_state == PURCHASE_CHARGED:
          self.response.out.write('')
          return
        
        purchase.order_state = PURCHASE_CHARGED
        purchase.account.total_tokens += purchase.tokens
        purchase.account.save()
        purchase.save()
        
        logging.debug('Purchase Charged')
    
    self.response.out.write('')

class GPayCheckoutBuyHandler( webapp.RequestHandler ):
  # redirect to checkout w/ error messages... flash-system similar to rails?
  # def get(self):
  #   self.post()
  
  def post(self):
    # hours = self.request.get('item_selection_1')
    # if not hours:
    #   self.response.out.write('No hours given')
    #   return
    
    hours = '1'
    item_name = "%s-hours" % hours
    item_desc = "%s Hours" % hours
    unit_price = '11.99'
    return_url = 'http://mostlymt.appspot.com/'

    form_data = '''<?xml version="1.0" encoding="UTF-8"?>
    <checkout-shopping-cart xmlns="http://checkout.google.com/schema/2">
      <shopping-cart>
        <items>
          <item>
            <item-name>%s</item-name>
            <item-description>%s</item-description>
            <unit-price currency="USD">%s</unit-price>
            <quantity>1</quantity>
            <digital-content>
              <display-disposition>PESSIMISTIC</display-disposition>
              <description>
                When your payment is processed, your task will be worked on. 
                View your task&apos;s status
                &amp;lt;a href="%s"&amp;gt;here&amp;lt;/a&amp;gt;.
              </description>
            </digital-content>
          </item>
        </items>
      </shopping-cart>
      <checkout-flow-support>
        <merchant-checkout-flow-support/>
      </checkout-flow-support>
    </checkout-shopping-cart>''' % (item_name, item_desc, unit_price, return_url)
    
    basicauth = base64.encodestring('%s:%s' % ('875093275712045','qNztxsdPtwA9f_dICQmjhg')).replace('\n', '')
    url = 'https://sandbox.google.com/checkout/api/checkout/v2/merchantCheckout/Merchant/875093275712045'
    result = urlfetch.fetch(url=url,
                           payload=form_data,
                           method=urlfetch.POST,
                           headers={'Authorization': 'Basic %s' % basicauth})
    body = result.content
    
    dom = minidom.parseString(body)
    
    cr_el = first_el(dom, 'checkout-redirect')
    if not cr_el:
      log.error(body)
      return
    #serial_number = cr_el.getAttribute('serial-number')
    redirect_url = first_el_val(cr_el, 'redirect-url')
    redirect_url = redirect_url.replace('&amp;', '&')
    
    self.redirect(redirect_url, False)


class CheckoutHandler( HandlerBase ):
	""" Handles requests for the checkout page. """
	def get( self ):
		options = self.get_options()
		options["content"] = self.render( "checkout", options )
		options["tagline"] = "Checkout"
		self.response.out.write( self.render( "outer", options ) )

	def post( self ):
	
		# TODO: Form checking

		# Create ticket, pulling required fields from form data, tacking on feature values
		fields = ( 'email', 'name', 'phone', 'description' )
		ticket = self.create( Ticket, fields )
		for k, v in self.get_options().iteritems():
			if not hasattr( ticket, k ): setattr( ticket, k, v )
		ticket.put()

		# Create options hash from ticket standard fields
		options = {}
		for field in fields: options[field] = getattr( ticket, field )

		# Create and send email message
		message = mail.EmailMessage(
			sender="eric.redmond@gmail.com",
            subject="Someone gave you a task",
            to="Jim Wilson <wilson.jim.r@gmail.com>, Eric Redmond <eric.redmond@gmail.com>",
            body=self.render( "messagebody", options )
        )
		message.send()
		
		return self.get()

def main():
	application = webapp.WSGIApplication([
		('/faq', FAQHandler),
		('/checkout', CheckoutHandler),
		('/gcheckout', GPayCheckoutBuyHandler),
		('/gpaynotify', GPayNotifyHandler),
		('/.*', MainHandler), # must be listed last since this regex matches anything
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
	main()
