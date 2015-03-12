from flask import Flask, render_template, jsonify, make_response
from PIL import Image
import StringIO
import pin

app = Flask(__name__)
app.debug=True

image = [None]
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/user/boards/<user>')
def boards(user):
    boards = pin.get_boards(user)
    if not boards:
        return jsonify({'status': 'failure', 'message': "Could not find that Pinterest user."})
    return jsonify({'status': 'success', 'boards': boards})

@app.route('/collage/verify/<user>/<board>/<seed>/<preset>')
def verify(user, board, seed, preset):
    img, message = pin.return_image(user, board, seed, preset)
    if not img:
       return jsonify({'status': 'failure', 'message': message})
    else:
        image[0] = img
        return jsonify({'status': 'success', 'message': message})

@app.route('/collage/show/<user>/<board>/<seed>/<preset>')
def show(user, board, seed, preset):
    image_buffer = prepare_image()
    if not image_buffer:
        return None
    response = make_response(image_buffer.getvalue())
    response.headers['Content-Type']= 'image/png'
    return response

@app.route('/collage/download/<user>/<board>/<seed>/<preset>')
def download(user, board, seed, preset):
    image_buffer = prepare_image()
    if not image_buffer:
        return None
    filename = '"%s-%s-%s-%s.png"' % (user, board, seed, preset)
    response = make_response(serve_fileobj(image_buffer))
    response.headers['Content-Type']= 'image/png'
    response.headers['Content-Disposition'] = 'attachment; filename=' + filename
    return response

def prepare_image():
    img = image[0]
    if not img:
        return None
    image_buffer = StringIO.StringIO()
    img.save(image_buffer, 'PNG')
    image_buffer.seek(0)
    return image_buffer


