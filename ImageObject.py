from PIL import Image


class ImageObject(object):
	image = None
	filename = None
	mimetype = None

	def __init__(self, image_path):
		self.image = image_path
		image_obj = self._get_image()
		self.filename = image_obj.filename
		self.mimetype = Image.MIME[image_obj.format]

	def type(self):
		"""
		Get the mime type of the image.
		:return: The image mime type
		"""
		return self.mimetype

	def get(self):
		"""
		Get the image filename for retrieval.
		:return: The image filename
		"""
		return self.filename

	def _get_image(self):
		"""
		Open up the image for a transformation.
		:return: The Pillow Image object
		"""
		return Image.open(self.image)

	def flip(self, horizontal=True):
		"""
		Flip an image horizontally or vertically.
		:param horizontal: Indicator to flip horizontally, otherwise vertically
		"""
		image_obj = self._get_image()
		flip = Image.FLIP_LEFT_RIGHT if horizontal else Image.FLIP_TOP_BOTTOM
		image_obj.transpose(flip).save(image_obj.filename)

	def rotate(self, degrees):
		"""
		Rotate an image the number of degrees specified.
		:param degrees: The number of degrees to rotate the image
		"""
		image_obj = self._get_image()
		image_obj.rotate(degrees, expand=True).save(image_obj.filename)

	def grayscale(self):
		"""
		Convert an image to grayscale.
		"""
		image_obj = self._get_image()
		image_obj.convert('LA').save(image_obj.filename)

	def resize(self, size):
		"""
		Resize the image to the specified size
		"""
		# make sure that we are getting a dimension, not a number
		if isinstance(size, float):
			return

		dimensions = [int(dimension) for dimension in size.split('x') if dimension.isnumeric()]
		if len(dimensions) == 2:
			image_obj = self._get_image()
			image_obj.resize((dimensions[0], dimensions[1])).save(image_obj.filename)

	def thumbnail(self, size):
		"""
		Generate a 100px thumbnail of the image.
		:param size: The size of the thumbnail
		"""
		image_obj = self._get_image()
		image_obj.thumbnail((size, size))
		image_obj.save(image_obj.filename)
