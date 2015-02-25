from bs4 import BeautifulSoup
from PIL import Image
from PIL import ImageEnhance
from cStringIO import StringIO
import random
import math
import requests


resolutions = {
	'iphone4': {
		'width': 640,
		'height': 960,
		'columns': 4,
		'padding': 5
		},
	'iphone':  {
		'width': 320, 
		'height': 480, 
		'columns': 3,
		'padding': 5
		},
	'ipad': {
		'width': 768, 
		'height': 1024, 
		'columns': 4,
		'padding': 10
	},
	'ipad3': {
		'width': 1536, 
		'height': 2048, 
		'columns': 8,
		'padding': 10
	}
}

def get_boards(user):
	resp = requests.get('https://www.pinterest.com/%s' % user)
	if resp.status_code != 200:
		return None
	soup = BeautifulSoup(resp.content)
	board_divs = soup.select('.boardLinkWrapper')
	boards = [{'name': board.select('.title')[0].text,
               'url': board['href'].split('/')[2]} for board in board_divs]
	return sorted(boards, key=lambda board: board['name'])

def get_image_urls(user, board, seed):
    resp = requests.get('https://www.pinterest.com/%s/%s' % (user, board))
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.content)
    # fullimages = soup.select('.pinImageWrapper')
    # base_url = 'https://www.pinterest.com'
    # fullurls = [base_url + image['href'] for image in images]
    images = soup.select('.pinImg')
    urls = [image['src'] for image in images]
    random.seed(int(seed))
    random.shuffle(urls)
    return urls

def split_image_urls(urls, columns):
	rows = []
	for i in range(0, len(urls), columns):
		rows.append(urls[i:i+columns])
	return rows

def print_row(image, images, heights, columns, thumb_width, thumb_max_height, padding):
	for i in range(columns):
		page = requests.get(images[i])
		im = Image.open(StringIO(page.content))
		im.thumbnail((thumb_width, thumb_max_height), Image.ANTIALIAS)
		heights.append(heights[i] + im.size[1] + padding)
		image.paste(im, ((thumb_width + padding) * i, heights[i]))
	return heights[columns:]
	
def return_image(user, board, seed, template):
	if template in resolutions:
		img_width = resolutions[template]['width']
		img_height = resolutions[template]['height']
		columns = resolutions[template]['columns']
		padding = resolutions[template]['padding']
		thumb_width = int(math.floor((img_width - (columns - 1) * padding) / columns))
	else:
		dimensions = template.split('-')[1].split('x')
		img_width = int(dimensions[0])
		img_height = int(dimensions[1])
		thumb_width = 180
		padding = 20
		columns = int(math.ceil((img_width + padding) / thumb_width))
	thumb_max_height = 500
	urls = get_image_urls(user, board, seed)
	if not isinstance(urls, list):
		return None, "<strong>Error:</strong> Username/board combination not found."
	rows = split_image_urls(urls, columns)
	num_rows = len(rows)
	heights = [0] * columns
	#image = Image.open('static/img/light.png')
	image = Image.new("RGB", (img_width, img_height), "white")
	for i in range(num_rows - 1):
		heights = print_row(image, rows[i], heights, columns, thumb_width, thumb_max_height, padding)
	if heights[0] < img_height:
		return image, "<strong>Warning:</strong> Not enough images on this board to fill the template."
	return image, ""
