# Sentinel-2-NDVI
Docker container to generate a Normalised Difference Vegetation Index GeoTIFF from the Sentinel-2 red and near-Infrared bands.

The scripts also generate a colour-mapped GeoTIFF using a predefined colour-map file or using one of two dynamic colour-maps that the scripts can generate.<br/><br/>
The scripts then generate a PNG image from the colour-mapped GeoTIFF.<br/><br/>

![alt text](https://github.com/logi-26/simplify-polygon/blob/main/image1.png?raw=true)


## Info
The container uses the Sentinel-2 red and nir bands from the "bands" directory.
Any Sentinel-2 red and nir bands can be used from any Sentinel-2 image.

The container can use the predefined colour-map file from the "colour-map" directory.
(This can be edited before building the container).<br/>
Or the container can generate two different colour-maps dynamically using the paramatrers passed to the container.

## Usage
