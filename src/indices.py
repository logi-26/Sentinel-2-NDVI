# System imports
from os import remove
from numpy import arange, seterr, float32
from gdal import Open as gdal_open
from gdal import GDT_Float32, Translate, DEMProcessing, GetDriverByName, UseExceptions, PushErrorHandler, PopErrorHandler


class IndicesGenerator:
	"""
	Class to generate indices files from Sentinel band data
	"""

	def _gdal_error_handler(self, error_class, error_number, error_message):
		"""
		Custom GDAL error handler 
		(used to suppress warning messages in the console and for debugging purposes)
		:param error_class: 
        :param error_number:
		:param error_message:
		"""
		error_type = {CE_None: "None", CE_Debug: "Debug", CE_Warning: "Warning", CE_Failure: "Failure", CE_Fatal: "Fatal"}
		error_message = error_message.replace('\n', ' ')
		error_class = error_type.get(error_class, "None")

	def _get_colour_array(self, map_number):
		"""
		Get the array of colours
		:param map_number: int
		"""
		if map_number == 1:
			return (
				(48,100,102),
				(156,171,104),
				(204,204,102),
				(156,132,72),
				(110,70,44)
			)
		else:
			return (
				(100,0,0),
				(255,0,0),
				(255,255,0),
				(0,200,0),
				(0,100,0)
			)
		
	def _parse_colour_value(self, colour):
		"""
		Parse the colour values
		:param colour: tuple
		"""
		return f"{colour[0]} {colour[1]} {colour[2]}"

	def _write_colour_map_file(self, colour_map_path, first_value, masked_cloud, masked_no_data, converted_value_array, map_number):
		"""
		Write the colour-map CSV file
		:param colour_map_path: string
		:param first_value: float
		:param masked_cloud: float
		:param masked_no_data: float
		:param converted_value_array: array
		:param map_number: int
		"""

		# Create the dynamic colour map CSV file
		with open(colour_map_path, mode="w+") as colour_map_file:

			# Write the first value to the new file
			colour_map_file.write(f"{first_value}\n")

			# Write the rest of the value using a loop
			for i in range(len(self._get_colour_array(map_number))):
				the_colour = self._parse_colour_value(self._get_colour_array(map_number)[i])
				colour_map_file.write(f"{converted_value_array[i]}    {the_colour}\n")

			# Write the cloud-mask and no-data values
			colour_map_file.write(f"{masked_cloud}\n")
			colour_map_file.write(f"{masked_no_data}\n")

	def _generate_dynamic_colour_map(self, data_min, data_max, colour_map_path, map_number):
		"""
		This generates a dynamic colour map
		:param data_min: float
		:param data_max: float
		:param colour_map_path: string
		:param map_number: int
		"""

		# Get the colour array
		colour_array = self._get_colour_array(map_number)

		# Calculate the number of increments required
		increment_number = data_max - data_min
		increment_number = increment_number / len(colour_array)

		# Reverse the values in the array
		converted_value_array = []
		for value in reversed(arange(data_min, data_max, increment_number)):
			converted_value_array.append(round(value, 2))

		# This is for condensing the colour scale above and below our min/max values
		first = self._parse_colour_value(self._get_colour_array(map_number)[0])

		first_value = f"1       {first}"
		masked_cloud = "0       175 175 175"
		masked_no_data = "-1    0 0 0 0"

		# Create the dynamic colour map CSV file
		self._write_colour_map_file(colour_map_path, first_value, masked_cloud, masked_no_data, converted_value_array, map_number)

	def _calculate_ndvi(self, red, nir):
		"""
		Performs NDVI calculation on the red and NIR bands
		:param red: numpy 2d array
        :param nir: numpy 2d array
		:return: numpy 2d array
		"""
		return (nir - red) / (nir + red)

	def generate_ndvi(self, red_file, nir_file, outfile_name):
		"""
		Generate an NDVI geotiff file from the Sentinel band files
		:param red_file: 
        :param nir_file: 
		:param outfile_name: 
		"""
		seterr(divide = "ignore", invalid = "ignore")

		# Use our own custom GDAL error handler to suppress the unnecessary messages
		UseExceptions()
		PushErrorHandler(self._gdal_error_handler)
		try:
			# Open each band using gdal
			red_band = gdal_open(red_file)
			nir_band = gdal_open(nir_file)

			# Read in each band as array and convert to float for calculations
			red = red_band.ReadAsArray().astype(float32)
			nir = nir_band.ReadAsArray().astype(float32)

			# Call the ndvi() function on red, NIR bands
			ndvi = self._calculate_ndvi(red, nir)

			x_pixels = ndvi.shape[0]  # Number of pixels in x
			y_pixels = ndvi.shape[1]  # Number of pixels in y

			# Set up output GeoTIFF
			driver = GetDriverByName("GTiff")

			# Create driver using output filename, x and y pixels, # of bands, and data type
			ndvi_data = driver.Create(outfile_name, x_pixels, y_pixels, 1, GDT_Float32)

			# Set NDVI array as the 1 output raster band
			ndvi_data.GetRasterBand(1).WriteArray(ndvi)

			# Get the GeoTransform and projection information from the red band
			geo_transform = red_band.GetGeoTransform()
			proj = red_band.GetProjection()

			# Set GeoTransform and projection of the output file
			ndvi_data.SetGeoTransform(geo_transform)
			ndvi_data.SetProjection(proj)
			ndvi_data.FlushCache()
			ndvi_data = None
			red_band = None
			nir_band = None

		except Exception as exception:
			print(f"Exception: {exception}")
		finally:
			PopErrorHandler()

	def colour_map_image(self, input_image, output_image, colour_map_path, map_number):
		"""
		Generate a coloured tiff image using a colour map file
		:param input_image: tiff file
		:param output_image: tiff file
		:param colour_map_path: string (path to colour map)
		:param map_number: int
		"""

		# Generate a dynamic colour-map if the boolean is true
		if colour_map_path is not None:
			# Use GDAL DEMP processing to apply the predefined colour-map
			DEMProcessing(output_image, input_image, processing="color-relief", colorFilename=colour_map_path, addAlpha=True)
		else:
			colour_map_path = "/home/colour_map/custom_colour_map.csv"

			# Open the black and white NDVI tiff file
			black_white_ndvi = gdal_open(input_image)

			# Get the stats for the first band
			src_band = black_white_ndvi.GetRasterBand(1)
			raster_stats = src_band.GetStatistics(True, True)

			# get the min and max NDVI values
			data_min = raster_stats[0]
			data_max = raster_stats[1]

			# Generate the dynamic colour-map
			IndicesGenerator()._generate_dynamic_colour_map(data_min, data_max, colour_map_path, map_number)

			# Use GDAL DEMP processing to apply the dynamic colour-map
			DEMProcessing(output_image, input_image, processing="color-relief", colorFilename=colour_map_path, addAlpha=True)

			# Delete the custom colour-map file
			remove(colour_map_path)

			black_white_ndvi = None

	def tiff_to_png(self, input_tiff, output_png):
		"""
		Convert the tiff file to a png using GDAL translate
		:param input_tiff: tiff file
		:param output_png: string (png file path)
		"""
		Translate(output_png, input_tiff, format="PNG", widthPct=100, heightPct=100)
