from flask import Flask, Response, send_file, request
import json
import uuid
import os
from io import BytesIO

from ImageObject import ImageObject

app = Flask(__name__)
UPLOAD_FOLDER = './Temp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# region Helper Methods

def get_response(code, data):
	"""
	Get a Flask Response object for the provided response code and JSON data.
	:param code: The response code to encode
	:param data: The response data to encode
	:return: The Flask Response object containing the response code and data
	"""
	return Response(json.dumps(data), status=code, mimetype="application/json")


def get_transformations_list(raw):
	"""
	Turn the transformations request into a usable list of instructions.
	:param raw: The raw transformation request data
	:return: The formatted list of transformation instructions
	"""
	instructions = []

	# first split up into individual instructions
	split_raw = raw.split(',')

	for instruction in [a.strip() for a in split_raw]:
		# then split the instruction into operation and value
		split_instruct = instruction.split(' ')
		if len(split_instruct) == 2:
			# convert value to a number if necessary
			if split_instruct[1].lstrip('-').isnumeric():
				split_instruct[1] = float(split_instruct[1])
		else:
			split_instruct.append(None)

		instructions.append({split_instruct[0]: split_instruct[1]})

	return instructions


def valid_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(image_obj):
	"""
	Save a copy of the file that was sent to the server.
	:param image_obj: The request.files object
	:return: The location of the uploaded file
	"""
	filename = str(uuid.uuid1()) + "." + image_obj.filename.rsplit('.', 1)[1].lower()
	upload_location = os.path.join(UPLOAD_FOLDER, filename)
	image_obj.save(upload_location)
	return upload_location


def handle_transformation(image_obj, tf):
	"""
	Interpret a transformation command and complete the transformation.
	:param image_obj: The image to be transformed
	:param tf: The transformation to be completed
	"""
	if 'rotate' in tf and not tf['rotate'] is None:
		image_obj.rotate(tf['rotate'])
	if 'rotate_left' in tf:
		image_obj.rotate(-90)
	if 'rotate_right' in tf:
		image_obj.rotate(90)
	if 'grayscale' in tf and not image_obj.mimetype == 'image/jpeg':
		image_obj.grayscale()
	if 'flip' in tf and not tf['flip'] is None:
		image_obj.flip(tf['flip'] == 'horizontal')
	if 'resize' in tf and not tf['resize'] is None:
		image_obj.resize(tf['resize'])
	if 'thumbnail' in tf and not tf['thumbnail'] is None:
		image_obj.thumbnail(tf['thumbnail'])


# endregion


@app.route('/', methods=['POST'])
def image_manipulation():
	"""
	The main endpoint for the image manipulation API.
	:return: The resulting image object, or error
	"""
	# make sure that an image has been properly provided
	if 'ImageFile' not in request.files or\
		len(request.files['ImageFile'].filename) == 0 or not valid_file(request.files['ImageFile'].filename):
		return get_response(400, 'Missing ImageFile image upload!')

	# make sure that they asked for some transformations to be done
	if 'Transformations' not in request.form or len(request.form['Transformations']) == 0:
		return get_response(400, 'Missing or empty Transformations field!')

	# copy the image to the temp directory, create handler
	file = upload_image(request.files['ImageFile'])
	image_obj = ImageObject(file)

	# interpret the transformations
	transformations = get_transformations_list(request.form['Transformations'])

	# do each transformation on disk
	for tf in transformations:
		handle_transformation(image_obj, tf)

	# load the result into memory
	buffer = BytesIO(open(file, 'rb').read())
	buffer.seek(0)

	# delete the file
	os.remove(file)

	# send the result
	result_filename = request.files['ImageFile'].filename
	return send_file(buffer, as_attachment=True, attachment_filename=result_filename, mimetype=image_obj.mimetype)


if __name__ == '__main__':
	app.run()
