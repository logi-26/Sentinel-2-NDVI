# Ubuntu base image
FROM ubuntu:focal

# Update base container install
RUN apt-get update

# Setup timezone info
ENV TZ 'GB'
RUN echo $TZ > /etc/timezone && \
    apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

# Install GDAL dependencies
RUN apt-get install -y python3-pip libgdal-dev locales

# Copy the requirments.txt file into the container
COPY requirements.txt /home/

# Install the required libraries from the requirements.txt file
RUN pip3 install -r /home/requirements.txt

# Install GDAL
RUN pip3 install GDAL==3.0.4

# Create the src directory
RUN mkdir -p /home/src

# Copy all of the scripts into the src directory
COPY src/* /home/src/

# Create the band_data directory
RUN mkdir -p /home/band_data

# Copy all of the Sentinel band files into the band_data directory
COPY band_data/* /home/band_data/

# Create the colour-map directory
RUN mkdir -p /home/colour_map

# Copy the colour map file into the directory
COPY colour_map/colour_map.csv /home/colour_map/

# Create the output directory
RUN mkdir -p /home/output

# Set the src directory as the working directory
WORKDIR /home/src/

# Set the entrypoint
ENTRYPOINT ["python3","main.py"]