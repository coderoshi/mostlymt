from google.appengine.ext import webapp, db
import logging, re

class Promo( db.Model ):
	code = db.StringProperty()
	email = db.EmailProperty()
	hours = db.IntegerProperty(default=1)
	used = db.BooleanProperty(default=False)
	timestamp = db.DateTimeProperty(auto_now_add=True)
	
	@classmethod
	def generate_code( cls ):
		import base64, random
		
		letters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
		r = random.random
		n = len(letters)
		lst = [None] * 10
		for i in xrange(10):
			lst[i] = letters[int(r() * n)]
		lst.append(random.choice(re.sub(r'\s', '', letters)))
		
		return "".join(lst)
	
	@classmethod
	def find_promo( cls, string ):
		p = re.compile(r'PROMO:(.+)', re.MULTILINE)
		m = p.search(string)
		if m:
			code = m.group(1)
			if code: return Promo.find_by_code(code)
		
		return None
	
	@classmethod
	def find_by_code( cls, code ):
		query = Promo.all()
		query.filter('code =', code)
		promos = query.fetch(1)
		
		if promos: return promos[0]
		return None
		

