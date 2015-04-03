from bs4 import BeautifulSoup
from PIL import Image
from PIL import ImageEnhance
from cStringIO import StringIO
import random
import math
import requests
import re

resolutions = {
	'iphone4': {
		'width': 640,
		'height': 960,
		'columns': 4,
		'padding': 0
		},
	'iphone':  {
		'width': 320, 
		'height': 480, 
		'columns': 3,
		'padding': 0
		},
	'ipad': {
		'width': 768, 
		'height': 1024, 
		'columns': 4,
		'padding': 0
	},
	'ipad3': {
		'width': 1536, 
		'height': 2048, 
		'columns': 8,
		'padding': 0
	}
}

origurl = 'https://www.pinterest.com/resource/BoardFeedResource/get/?source_url=%2F{user}%2F{board}%2F&data=%7B%22options\
%22%3A%7B%22board_id%22%3A%{boardid}%22%2C%22board_url%22%3A%22%2F{user}%2F{board}%2F%22%2C%22page_size%22%3Anu\
ll%2C%22prepend%22%3Atrue%2C%22access%22%3A%5B%22write%22%2C%22delete%22%5D%2C%22board_layout%22%3A%22default%2\
2%2C%22bookmarks%22%3A%5B%22{bookmark}%3D%3D%22%5D%7D%2C%22context%22%3A%7B%7D%7D&_=1425920710678'

headers = {
    'Pragma': 'no-cache',
    'X-Pinterest-AppState': 'background',
    'X-APP-VERSION': '77477f7',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36',
    'X-NEW-APP': '1',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Cache-Control': 'no-cache',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://www.pinterest.com/'}

def get_boards(user):
	resp = requests.get('https://www.pinterest.com/%s' % user, verify=False)
	if resp.status_code != 200:
		return None
	soup = BeautifulSoup(resp.content)
	board_divs = soup.select('.boardLinkWrapper')
	boards = [{'name': board.select('.title')[0].text,
               'url': board['href'].split('/')[2]} for board in board_divs]
	return sorted(boards, key=lambda board: board['name'])

def get_image_urls(user, board, seed):    
    resp = requests.get('https://www.pinterest.com/%s/%s/' % (user, board), verify=False)
    if resp.status_code != 200:
        return None
    r = resp.content
    soup = BeautifulSoup(r)
    pins = soup.select('.pinImg')
    images = [image['src'] for image in pins]
    bookmark = '-end-'
    for m in re.finditer('bookmarks": \["(.*?)"\]', r):
        x = m.groups()[0]
        if x != '-end-':
            bookmark = x
            break
    for m in re.finditer('board_id": "(.*?)"', r):
        x = m.groups()[0]
        if x != '?{bid}':
            boardid = x
            break
    boardid = '22'+boardid
    while bookmark != '-end-':
        url = origurl.format(user=user,board=board,boardid=boardid,bookmark=bookmark)
        resp = requests.get(url, headers=headers, verify=False)
        j = resp.json()
        pins = j['resource_response']['data']
        images.extend([pins[i]['images']['236x']['url'] for i in range(len(pins))])
        bookmark = j['resource']['options']['bookmarks'][0]
    random.seed(int(seed))
    random.shuffle(images)
    return images

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
		padding = 0
		columns = int(math.ceil((img_width + padding) / float(thumb_width)))
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
