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
- elevation chart scale;
- <s>redo the program data exchange with the server;</s>
- <s>database;</s>
- <s>multiprocessing</s>;
- <s>speed up DB</s>.

# Benchmark results:
<p>1st test_coordinates = [53.822975, 27.087467, 52.911044, 27.691194] - 110 km</p>
<p>2d test_coordinates = [51.742627, 23.964322, 55.404321, 30.621924] - 600 km</p>

- For simple python without MP (ProcessPoolExecutor):
<p>1 TIME_FIND_POINTS: 3.4808 sec (0.058 min); 110 km, extracted data from the database = 67.418</p>
<p>2 TIME_FIND_POINTS: 852.0257 sec (14.2 min, before 06/06/19 it was 26.4 min); 600 km, extracted data from the database = 2.979.379</p>

- With MP!!!
<p>1 Multiprocessing time = 2.4771784 sec; 110 km, extracted data from the database = 10.446‬</p>
<p>2 Multiprocessing time = 6.7197512 sec; 600 km, extracted data from the database = 303.636</p>