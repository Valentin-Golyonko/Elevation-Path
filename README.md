# Elevation-Path
The program is designed to calculate the communication line and the elevation difference on it
using offline OSM map or online google maps.

# Images:
Offline Open Street Map, elevation accuracy 1 point per 1 km -
<img src="https://github.com/Valentin-Golyonko/Elevation-Path/blob/master/images/Screenshot_OSM.png" alt="web_view">

Online Google Maps, elevation accuracy 1 point per 1 km -
<img src="https://github.com/Valentin-Golyonko/Elevation-Path/blob/master/images/Screenshot_Google_maps.png" alt="web_view">

# How to:
Python:
- Install PyQt5, PyQt5-sip, PyQtWebEngine, Matplotlib, NumPy, QtDesigner (to do UI), pyqt5-tools (convert .ui-file to .py-file)
- For Windows i used Python version 3.6.x with Qt5 from <a href="https://winpython.github.io/">winpython</a>.
- For Ubuntu all working good without any custom manipulations (python 3.7.x). 

Maps:
- OpenStreetMap server is installed on Ubuntu 19.04 (+ tested on 18.04 and 18.10) using
<a href="https://switch2osm.org/manually-building-a-tile-server-18-04-lts/">Manually building a tile server (18.04 LTS)</a>.
- If you have Win 10 build 16215+, you can install ubuntu 18.04 with <a href="https://docs.microsoft.com/en-us/windows/wsl/install-win10">Windows Subsystem for Linux</a>
- Google Maps is used for <i>online</i> calculation
<a href="https://developers.google.com/maps/documentation/elevation/intro">Elevation API + Maps JavaScript API</a>

Data obtained from the satellite is used for <i>offline</i> calculation, 
they are converted in the QGIS program from images to geojson data.

You may change (in the build v.1.0):
 - data base from 5m to 1m accuracy - line 72 "GeoJson.py" <code>db = sqlite3.connect('elev_5m.db')</code>;
 - number of points per km:
    - line 35 in "GeoJson.py" <code>number_of_points = int(d_ab) * <b>1</b></code>
    - line 212 in "create_ui.py" <code>'samples': ''' + str(<b>1</b> * GeoJson.number_of_points) + '''</code>

# TODO:
- <s>redo the program data exchange with the server;</s>
- connection error with local (WAN) server;
- <s>database;</s>
- multithreading;
- elevation chart scale;
- speed up DB;
- 
