# Sentinel-2-NDVI
Docker container to generate a Normalised Difference Vegetation Index GeoTIFF from the Sentinel-2 red and near-Infrared bands.

The scripts also generate a colour-mapped GeoTIFF using a predefined colour-map file or using one of two dynamic colour-maps that the scripts can generate.<br/><br/>
The scripts then generate a PNG image from the colour-mapped GeoTIFF.<br/><br/>

Dynamic colour-map 1:
![alt text](https://github.com/logi-26/sentinel-2-ndvi/blob/main/git_images/ndvi_1.png?raw=true)
![alt text](https://github.com/logi-26/sentinel-2-ndvi/blob/main/git_images/ndvi_1_big.png?raw=true)

Dynamic colour-map 2:
![alt text](https://github.com/logi-26/sentinel-2-ndvi/blob/main/git_images/ndvi_2.png?raw=true)
![alt text](https://github.com/logi-26/sentinel-2-ndvi/blob/main/git_images/ndvi_2_big.png?raw=true)

Static colour-map (can be edited):
![alt text](https://github.com/logi-26/sentinel-2-ndvi/blob/main/git_images/ndvi_3.png?raw=true)
![alt text](https://github.com/logi-26/sentinel-2-ndvi/blob/main/git_images/ndvi_3_big.png?raw=true)

## Info
The container generates an NDVI from Sentinel-2 red and nir bands.
The red and nir bands should be placed into the "bands" directory before building the container.
Any Sentinel-2 red and nir bands can be used from any Sentinel-2 image.

The container can use the predefined colour-map file from the "colour-map" directory.
(This can be edited before building the container).<br/>
Or the container can generate two different colour-maps dynamically using the paramatrers passed to the container.

After generating the colour-mapped NDVI GeoTIFF file, the container will generate a PNG file.

## Usage
Clone the repo.<br/>
Put the red and nir bands into the "bands" directory.<br/>

**Open a terminal in the repo root directory and build the image:**<br/>
docker build -t indices_generator.<br/>

**Run the container (replace the output path with a directory on the host system):**<br/>
docker run -e PYTHONUNBUFFERED=1 -v /home/user/Desktop/indices_ndvi/output:/home/output indices_generator true 1<br/>

**Paramaters explained:**<br/>
1. **-e PYTHONUNBUFFERED=1** (directs the Python print statements to the terminal)<br/>
1. **-v /home/user/Desktop/indices_ndvi/output:/home/output** (this mounts a directory from the host)<br/>
1. **indices_generator** (image name)<br/>
1. **true** (this tells the scripts to use a dynamic colour-map)<br/>
1. **1** (this is the dynamic colour-map number)

