#!/usr/bin/env python
# Google.py
# 

import base64, logging
from google.appengine.api import urlfetch
from utils import *

class Google(object):
  """
    Google Checkout utility
  """
  
  def __init__( self, name, desc, price, hours, return_url, key ):
    self.name = name
    self.desc = desc
    self.price = price
    self.hours = hours
    self.return_url = return_url
    self.key = str(key)
  
  def fetch( self, username, password, url ):
    basicauth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    result = urlfetch.fetch(url=url,
                           payload=self.payload(),
                           method=urlfetch.POST,
                           headers={'Authorization': 'Basic %s' % basicauth})
    self.return_content = result.content
    logging.debug(self.return_content)
    return self.return_content
  
  def get_redirect_url( self ):
    if self.return_content:
      cr_el = first_el( dom( self.return_content ), 'checkout-redirect' )
      if not cr_el:
        log.error( self.return_content )
        log.error( 'No checkout-redirect... body:' )
        return None
      redirect_url = first_el_val( cr_el, 'redirect-url' )
      return redirect_url.replace( '&amp;', '&' )
      
    return None
  
  def payload( self ):
    return '''<?xml version="1.0" encoding="UTF-8"?>
    <checkout-shopping-cart xmlns="http://checkout.google.com/schema/2">
      <shopping-cart>
        <items>
          <item>
            <item-name>%s</item-name>
            <item-description>%s</item-description>
            <unit-price currency="USD">%s</unit-price>
            <quantity>%s</quantity>
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
        <merchant-private-data><ticket-key>%s</ticket-key></merchant-private-data>
      </shopping-cart>
    </checkout-shopping-cart>''' % (self.name, self.desc, self.price, self.hours, self.return_url, self.key)
  
  