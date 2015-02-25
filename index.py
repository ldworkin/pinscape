import cherrypy
from cherrypy.lib import file_generator
from cherrypy.lib.static import serve_fileobj
from jinja2 import Environment, FileSystemLoader
import StringIO
from PIL import Image
import pin
import json

env = Environment(loader=FileSystemLoader('templates'))

class User(object):

	def boards(self, user):
		boards = pin.get_boards(user)
		if not boards:
			return json.dumps({'status': 'failure', 'message': "Could not find that Pinterest user."})
		return json.dumps({'status': 'success', 'boards': boards})

	boards.exposed = True

class Collage(object):

	def verify(self, user, board, seed, preset):
		image, message = pin.return_image(user, board, seed, preset)
		if not image:
			return json.dumps({'status': 'failure', 'message': message})
		else:
			self.image = image
			return json.dumps({'status': 'success', 'message': message})

	verify.exposed = True

	def show(self, user, board, seed, preset):
		image_buffer = self.prepare_image()
		if not image_buffer:
			return None
		cherrypy.response.headers['Content-Type']= 'image/png'
		return image_buffer.getvalue()
		
	show.exposed = True

	def download(self, user, board, seed, preset):
		image_buffer = self.prepare_image()
		if not image_buffer:
			return None
		filename = '"%s-%s-%s-%s.png"' % (user, board, seed, preset)
		cherrypy.response.headers['Content-Type']= 'image/png'
		cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=' + filename
		return serve_fileobj(image_buffer)

	download.exposed = True

	def prepare_image(self):
		image = self.image
		if not image:
			return None
		image_buffer = StringIO.StringIO()
		image.save(image_buffer, 'PNG')
		image_buffer.seek(0)
		return image_buffer
    
class Main(object):
	collage = Collage()
	user = User()

	def index(self):
		tmpl = env.get_template('index.html')
		return tmpl.render()

	index.exposed = True

#cherrypy.server.socket_host = '0.0.0.0'
cherrypy.quickstart(Main(),  config='index.conf')
