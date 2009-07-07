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
    
    non_el = first_el(notif_dom, 'new-order-notification')
    if non_el:
      self.buyer_id = first_el_val(non_el, 'buyer-id')
      self.order_number = first_el_val(non_el, 'google-order-number')
      
      bba_el = first_el(non_el, 'buyer-billing-address')
      self.email = first_el_val(bba_el, 'email')  # get the user who made this purchase
      
      # account = get_account_by_user(email)
      # 
      # purchase = vm.Purchase(account=account)
      # purchase.order_number = self.order_number
      
      sc_el = first_el(non_el, 'shopping-cart')
      
      item_el = first_el(sc_el, 'item')
      self.item_name = first_el_val(item_el, 'item-name')
      self.unit_price = first_el_val(item_el, 'unit-price')
      
      mpd_el = first_el(sc_el, 'merchant-private-data')
      self.ticket_key = first_el_val(mpd_el, 'ticket-key')
      
      # purchase.tokens = tokens
      # purchase.save()
      
      logging.debug('Save Purchases')
      
      self.new_purchase = True
    else:
      self.new_purchase = False
    #   oscn_el = first_el(notif_dom, 'order-state-change-notification')
    #   self.order_number = first_el_val(oscn_el, 'google-order-number')
    #   self.new_financial_order_state = first_el_val(oscn_el, 'new-financial-order-state')
    #   if self.new_financial_order_state == 'CHARGED':
    #     # set charged == True
    #     # query = Purchase.all()
    #     # query.filter('order_number =', self.order_number)
    #     # purchase = query.fetch(1)
    #     # if purchase:
    #     #   purchase = purchase[0]
    #     # else:
    #     #   #throw some exception?
    #     #   # TODO: Make a new purchase if not exists - set status to PURCHASE_CHARGED_UNSET ?
    #     #   logging.error('Trying to charge an unmade purchase')
    #     #   return
    #     #
    #     # # no need to make a change if tokens already added
    #     # if purchase.order_state == PURCHASE_CHARGED:
    #     #   self.response.out.write('')
    #     #   return
    #     # 
    #     # purchase.order_state = PURCHASE_CHARGED
    #     # purchase.account.total_tokens += purchase.tokens
    #     # purchase.account.save()
    #     # purchase.save()
    #     #
    #     logging.debug('Purchase Charged')
