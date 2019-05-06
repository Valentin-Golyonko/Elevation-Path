# Elevation-Path
The program is designed to calculate the communication line and the elevation difference on it
using offline OSM map or online google maps.

# Images:
osm map, elevation accuracy 5m, 1 point per 1 km -
<img src="https://github.com/Valentin-Golyonko/Elevation-Path/blob/master/images/osm%20map%2C%20elevation%20accuracy%205m%2C%201%20point%20per%20km.png" alt="web_view">

google map, elevation 100 points per path -
<img src="https://github.com/Valentin-Golyonko/Elevation-Path/blob/master/images/google%20map%2C%20elevation%20512%20points%20per%20path.png" alt="web_view">

# How to:
For Windows i used Python version 3.6.x with Qt5 from <a href="https://winpython.github.io/">winpython</a>.
For Ubuntu all working good without any custom manipulations (python 3.7). 

OpenStreetMap server is installed on Ubuntu 19.04 (+ tested on 18.04 and 18.10) using
<a href="https://switch2osm.org/manually-building-a-tile-server-18-04-lts/">Manually building a tile server (18.04 LTS)</a>

Google Maps is used for <i>online</i> calculation
<a href="https://developers.google.com/maps/documentation/elevation/intro">Elevation API + Maps JavaScript API</a>

Data obtained from the satellite is used for <i>offline</i> calculation, 
they are converted in the QGIS program from images to geojson data.

# TODO:
- <s>redo the program data exchange with the server;</s>
- connection error with local (WAN) server;
- <s>database;</s>
- multithreading;
- 
