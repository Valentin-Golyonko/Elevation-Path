# Elevation-Path
The program is designed to calculate the communication line and the elevation difference on it
using offline OSM map or online google maps.

# Images:
<img src="https://github.com/Valentin-Golyonko/Elevation-Path/blob/master/images/osm%20map%20and%20altitude%20line.png" alt="web_view">

<img src="https://github.com/Valentin-Golyonko/Elevation-Path/blob/master/images/google%20map%20and%20altitude%20line.png" alt="web_view">

# How to:
OpenStreetMap server is installed on Ubuntu 18.10 using
<a href="https://switch2osm.org/manually-building-a-tile-server-18-04-lts/">Manually building a tile server (18.04 LTS)</a>

Google Maps is used for <i>online</i> calculation.
<a href="https://developers.google.com/maps/documentation/elevation/intro">Elevation API + Maps JavaScript API</a>

Data obtained from the satellite is used for <i>offline</i> calculation, 
they are converted in the QGIS program from images to geojson data.

# TODO:
- redo the program data exchange with the server;
- database;
- multithreading;
- 
