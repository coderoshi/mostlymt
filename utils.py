from xml.dom import minidom

def dom(xml):
  return minidom.parseString(xml)

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
