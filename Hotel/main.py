import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True
)

class MyBookings(ndb.Model):

	start_date = ndb.DateProperty()
	to_date = ndb.DateProperty()

class MyRooms(ndb.Model):

	bookings = ndb.StructuredProperty(MyBookings, repeated = True)

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		welcome = 'Welcome back'
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_string = 'logout'
		
		else:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
			
		room_array = MyRooms.query()
		room_array = room_array.fetch()
		
		try:
			date = datetime.strptime(self.request.get('date'),"%Y-%m-%d").date()
		except BaseException, e:
			date = None
			
		if date is not None:
			for myrooms in room_array:
				for mybookings in myrooms.bookings:
					if mybookings.start_date <= date <= mybookings.to_date:
						myrooms.bookings = [mybookings]
						break
					else:
							myrooms.bookings = []
								
		template_values = {
			'url' : url,
			'url_string' : url_string,
			'user' : user,
			'welcome' : welcome,
			'room_array' : room_array,
        }

		template = JINJA_ENVIRONMENT.get_template('main.html')
		self.response.write(template.render(template_values))

	def post(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		if not user:
			return self.redirect("/")
			
		name = self.request.get("name")
		if not name:
			return self.redirect("/")
			
		myrooms_key = ndb.Key('MyRooms', name)
		myrooms = myrooms_key.get()
		
		if myrooms:
			return self.redirect("/")
		
		myrooms = MyRooms(id = name)
		myrooms.put()
		
		self.redirect("/")

class AddBookings(webapp2.RequestHandler):
	def get(self):				
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		welcome = 'Welcome back'
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_string = 'logout'
		
		else:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
			
		if not user:
			return self.redirect("/")

		name = self.request.get('name')		
		myrooms_key = ndb.Key('MyRooms',name)
		myrooms = myrooms_key.get()
		if not myrooms:
			return self.redirect("/")
		
		template_values = {
			'url' : url,
			'url_string' : url_string,
			'user' : user,
			'welcome' : welcome,
			'myrooms' : myrooms,
        }
		template = JINJA_ENVIRONMENT.get_template('add.html')
		self.response.write(template.render(template_values))

	def post(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		if not user:
			return self.redirect("/")
		if self.request.get("cancel"):
			return self.redirect("/")
		action = self.request.get('button')
		name = self.request.get('name')
		if not name:
			return self.redirect("/")
			
		myrooms_key = ndb.Key('MyRooms',name)
		myrooms = myrooms_key.get()
		
		if not myrooms:
			return self.redirect("/")
		
		if action == 'AddBookings':
			start_date = datetime.strptime(self.request.get('start_date'),"%Y-%m-%d").date()
			to_date = datetime.strptime(self.request.get('to_date'),"%Y-%m-%d").date()
			current_date = datetime.now().date()
			if start_date < current_date:
				return self.redirect("/add?name="+name)
			if to_date < start_date:
				return self.redirect("/add?name="+name)
			
			for mybookings in myrooms.bookings:
				if start_date <= mybookings.start_date <= to_date:
					return self.redirect("/add?name="+name)
				if start_date <= mybookings.to_date <= to_date:
					return self.redirect("/add?name="+name)
			myrooms.bookings.append(MyBookings(start_date=start_date,to_date=to_date))
			
		elif action ==	'delete':
			del myrooms.bookings[int(self.request.get('index'))-1]
		myrooms.put()	
		self.redirect("/add?name="+name)

app = webapp2.WSGIApplication([
    ("/",MainPage),
	("/add",AddBookings),
], debug = True)		
		