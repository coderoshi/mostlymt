#!/usr/bin/env python
# GoogleNotified.py
# 

import logging
from utils import *

class GoogleNotified(object):
  def __init__(self):
    pass
  
  def parse(self, body):
    logging.debug(body)
    
    notif_dom = dom(body)
    
    self.new_purchase = False
    
    non_el = first_el(notif_dom, 'new-order-notification')
    if non_el:
      self.buyer_id = first_el_val(non_el, 'buyer-id')
      self.order_number = first_el_val(non_el, 'google-order-number')
      self.financial_order_state = first_el_val(non_el, 'financial-order-state')
      self.email_allowed = True
      if first_el_val(non_el, 'email-allowed') == 'false': self.email_allowed = False
      
      bba_el = first_el(non_el, 'buyer-billing-address')
      self.billing = False
      if bba_el:
        self.billing = True
        self.billing_email = first_el_val(bba_el, 'email')
        self.billing_address_1 = first_el_val(bba_el, 'address1')
        self.billing_address_2 = first_el_val(bba_el, 'address2')
        self.billing_first_name = first_el_val(bba_el, 'first-name')
        self.billing_last_name = first_el_val(bba_el, 'last-name')
        self.billing_country_code = first_el_val(bba_el, 'country-code')
        self.billing_city = first_el_val(bba_el, 'city')
        self.billing_region = first_el_val(bba_el, 'region')
        self.billing_postal_code = first_el_val(bba_el, 'postal-code')
      
      bsa_el = first_el(non_el, 'buyer-shipping-address')
      self.shipping = False
      if bsa_el:
        self.shipping = True
        self.shipping_email = first_el_val(bsa_el, 'email')
        self.shipping_address_1 = first_el_val(bsa_el, 'address1')
        self.shipping_address_2 = first_el_val(bsa_el, 'address2')
        self.shipping_first_name = first_el_val(bsa_el, 'first-name')
        self.shipping_last_name = first_el_val(bsa_el, 'last-name')
        self.shipping_country_code = first_el_val(bsa_el, 'country-code')
        self.shipping_city = first_el_val(bsa_el, 'city')
        self.shipping_region = first_el_val(bsa_el, 'region')
        self.shipping_postal_code = first_el_val(bsa_el, 'postal-code')
      
      # account = get_account_by_user(email)
      # 
      # purchase = vm.Purchase(account=account)
      # purchase.order_number = self.order_number
      
      sc_el = first_el(non_el, 'shopping-cart')
      
      item_el = first_el(sc_el, 'item')
      self.item_name = first_el_val(item_el, 'item-name')
      self.unit_price = first_el_val(item_el, 'unit-price')
      try:
        self.hours = int(first_el_val(item_el, 'quantity'))
      except ValueError:
        self.hours = 1
      
      mpd_el = first_el(sc_el, 'merchant-private-data')
      self.ticket_key = first_el_val(mpd_el, 'ticket-key')
      
      # purchase.tokens = tokens
      # purchase.save()
      # logging.debug('Save Purchases')
      
      self.new_purchase = True
    else:
      self.new_purchase = False
      oscn_el = first_el(notif_dom, 'order-state-change-notification')
      
      self.new_financial_order_state = None
      if oscn_el:
        self.order_number = first_el_val(oscn_el, 'google-order-number')
        self.new_financial_order_state = first_el_val(oscn_el, 'new-financial-order-state')
      
    