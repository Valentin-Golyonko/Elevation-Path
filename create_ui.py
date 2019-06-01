# from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets  +  QtWebEngineWidgets.QWebEngineView
# from mplwidget import MplWidget

import time
import numpy as np
from PyQt5 import QtCore, QtWidgets

import GeoJson
from gui.elevation_path import UiMainWindow


class CreateUi(QtWidgets.QMainWindow, UiMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.fill_forms()

        self.pb_do_path.clicked.connect(self.do_path)

    #
    def do_path(self):
        print("do_path()")
        time_60 = time.perf_counter()

        self.get_points_ab()

        if latitude_a != -1 and longitude_a != -1 and latitude_b != -1 and longitude_b != -1:
            # select map server
            if self.rb_osm_map.isChecked():
                self.gv_osm_plot.show()
                self.webView.setGeometry(QtCore.QRect(0, 159, 1101, 511))

                # calculate GeoJson data
                GeoJson.find_points(latitude_a, longitude_a, latitude_b, longitude_b)
                GeoJson.create_json(latitude_a, longitude_a, latitude_b, longitude_b)

                self.plot_elevation()
                self.load_osm_map()

            elif self.rb_google_map.isChecked():
                self.gv_osm_plot.hide()
                self.webView.setGeometry(QtCore.QRect(0, 159, 1101, 741))

                self.load_google_maps()
        else:
            print("\tcoordinates input ERROR")

        time_61 = time.perf_counter() - time_60
        print("\ttime_6.1: " + str(time_61) + " (" + str(time_61 / 60) + " min)\n")

    def get_points_ab(self):
        print("get_points_ab()")
        global latitude_a, longitude_a, latitude_b, longitude_b

        latitude_a = self.input_check(self.le_lat_a.text(), self.le_lat_a)
        longitude_a = self.input_check(self.le_lng_a.text(), self.le_lng_a)
        latitude_b = self.input_check(self.le_lat_b.text(), self.le_lat_b)
        longitude_b = self.input_check(self.le_lng_b.text(), self.le_lng_b)

    def plot_elevation(self):
        nop = GeoJson.number_of_points
        elev = GeoJson.elev_min
        e_height = GeoJson.earth_height(latitude_a, longitude_a, latitude_b, longitude_b)

        x1 = np.linspace(0, nop, num=nop)
        y1 = np.sin(2 * np.pi * x1 / (nop * 2)) * (e_height * 1000)
        y2 = [0.0] * x1
        for q in range(0, nop):
            y2[q] = elev[q]

        # clear the Axes to ensure that the next plot will seem a completely new one
        self.gv_osm_plot.canvas.ax.clear()

        labels = ["земля " + format(e_height, '.3f') + " m", "высоты"]
        self.gv_osm_plot.canvas.ax.stackplot(x1, y1, y2, labels=labels)

        self.gv_osm_plot.canvas.ax.grid(True)
        self.gv_osm_plot.canvas.fig.legend()
        self.gv_osm_plot.canvas.fig.tight_layout(None, 0.7, 0.7, 0.7, None)
        self.gv_osm_plot.canvas.ax.autoscale(enable=True, axis='both', tight=False)
        self.gv_osm_plot.canvas.draw()

    def load_osm_map(self):
        self.webView.setUrl(QtCore.QUrl("http://localhost/index.html" +
                                        "?lata=" + str(latitude_a) + "&lnga=" + str(longitude_a) +
                                        "&latb=" + str(latitude_b) + "&lngb=" + str(longitude_b)))
        # or "http://Your Server IP/index.html" + same

        self.webView.update()

    def load_google_maps(self):
        google_html_page = str('''
                        <!DOCTYPE html>
                        <html>
                            <head>
                                <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
                                <meta charset="utf-8">
                                <title>Showing Elevation Along a Path</title>
                                <style>
                                    /* Always set the map height explicitly to define the size of the div
                                    * element that contains the map. */
                                    #map {
                                        height: 100%;
                                    }
                                    /* Optional: Makes the sample page fill the window. */
                                    html, body {
                                        height: 100%;
                                        margin: 0;
                                        padding: 0;
                                    }
                                </style>
                                <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                                <script src="https://www.google.com/jsapi"></script>
                            </head>
                            <body>
                                <div>
                                    <div id="map" style="height:500px;"></div>
                                    <div id="output" style="height: 25px">
                                        <p>Расстояние: <input type="text" readonly id="distance_ab"> km;
                                         Высота точки А: <input type="text" readonly id="a_hight"> m;
                                         Высота точки Б: <input type="text" readonly id="b_hight"> m</p>
                                    </div>
                                    <div id="elevation_chart"></div>
                                    <!--
                                        <div id="t_a_hight"></div>
                                        <div id="t_b_hight"></div>
                                        <div id="t_d_ab"></div>
                                        <div id="t_distance"></div>
                                        <div id="t_elevation"></div>
                                        <div id="t_result"></div>
                                    -->
                                    <script>
                                        // Load the Visualization API and the columnchart package. corechart
                                        google.load('visualization', '1', {packages: ['corechart']});

                                        var point_a_lat = 0;
                                        var point_a_lng = 0;
                                        var point_b_lat = 0;
                                        var point_b_lng = 0;
                                        var marker1, marker2;               // points A and B on the map
                                        var point_a_hight, point_b_hight;   // hight of the points A and B
                                        var distance_ab_km;                 // distance between points A and B
                                        var point_distance = new Array();   // distance from A to point in the Path to B
                                        var point_elevation = new Array();  // elevation of the avery point in the path AB

                                        loadJson();

                                        function loadJson(){
                                            '''
                               + str("point_a_lat = " + str(latitude_a) + ";" +
                                     "point_a_lng = " + str(longitude_a) + ";" +
                                     "point_b_lat = " + str(latitude_b) + ";" +
                                     "point_b_lng = " + str(longitude_b) + ";") +
                               '''
                            }

                            function initMap() {
                                // The following path marks a path from Mt. Whitney, the highest point in the
                                // continental United States to Badwater, Death Valley, the lowest point.
                                var path = [
                                    {lat: point_a_lat, lng: point_a_lng},
                                    {lat: point_b_lat, lng: point_b_lng}
                                ];

                                var mapOptions = {
                                  zoom: 7,
                                  center: {lat: 53.9021935, lng: 27.5619195}, // Minsk
                                  // mapTypeId: https://developers.google.com/maps/documentation/javascript/maptypes
                                  mapTypeId: 'terrain',
                                  scaleControl: true,
                                  rotateControl: true,
                                };

                                var map = new google.maps.Map(document.getElementById('map'), mapOptions);

                                // Create an ElevationService.
                                var elevator = new google.maps.ElevationService;

                                // Draw the path, using the Visualization API and the Elevation service.
                                displayPathElevation(path, elevator, map);

                                marker1 = new google.maps.Marker({
                                    map: map,
                                    label: 'A',
                                    position: {lat: point_a_lat, lng: point_a_lng}
                                });

                                marker2 = new google.maps.Marker({
                                    map: map,
                                    label: 'Б',
                                    position: {lat: point_b_lat, lng: point_b_lng}
                                });

                                var bounds = new google.maps.LatLngBounds(
                                    marker1.getPosition(), marker2.getPosition());
                                map.fitBounds(bounds);
                            }

                            function displayPathElevation(path, elevator, map) {
                                // Display a polyline of the elevation path.
                                new google.maps.Polyline({
                                  path: path,
                                  strokeColor: '#FF0000',
                                  strokeOpacity: 1.0,
                                  strokeWeight: 3,
                                  map: map
                                });

                                // Create a PathElevationRequest object using this array.
                                // Ask for 256 samples along that path.
                                // Initiate the path request.
                                elevator.getElevationAlongPath({
                                  'path': path,
                                  'samples': ''' + str(1 * GeoJson.number_of_points) + '''
                                }, plotElevation);
                            }

                            // Takes an array of ElevationResult objects, draws the path on the map
                            // and plots the elevation profile on a Visualization API ColumnChart.
                            function plotElevation(elevations, status) {
                                var chartDiv = document.getElementById('elevation_chart');
                                if (status !== 'OK') {
                                    // Show the error code inside the chartDiv.
                                    chartDiv.innerHTML = 'Cannot show elevation: request failed because ' +
                                    status;
                                    return;
                                }
                                // Create a new chart in the elevation_chart DIV.
                                // Google chart tools: https://developers.google.com/chart/
                                var chart = new google.visualization.AreaChart(chartDiv);

                                var between_ab = [marker1.getPosition(), marker2.getPosition()];
                                var distance_ab = 
                                    google.maps.geometry.spherical.computeDistanceBetween(between_ab[0], between_ab[1]);
                                var round_distance = Math.round(distance_ab);
                                distance_ab_km = round_distance / 1000;
                                document.getElementById('distance_ab').value = distance_ab_km;

                                var e_length = elevations.length;
                                point_a_hight = Math.round(elevations[0].elevation * 100) / 100;
                                point_b_hight = Math.round(elevations[e_length - 1].elevation * 100) / 100;
                                document.getElementById('a_hight').value = point_a_hight;
                                document.getElementById('b_hight').value = point_b_hight;

                                // Extract the data from which to populate the chart.
                                // Because the samples are equidistant, the 'Sample'
                                // column here does double duty as distance along the X axis.
                                var data = new google.visualization.DataTable();
                                data.addColumn('string', 'UNIX');
                                data.addColumn('number', 'Elevation');
                                for (var i = 0; i < e_length; i++) {
                                    var e_point = Math.round(elevations[i].elevation * 100) / 100;
                                    var e_location = elevations[i].location;
                                    var distance_a_e = 
                                        google.maps.geometry.spherical.computeDistanceBetween(
                                            marker1.getPosition(), e_location);
                                    var d_point = Math.round(distance_a_e) / 1000;  // km

                                    data.addRow(['' + d_point, e_point]);

                                    point_distance.push(String(d_point)); 
                                    point_elevation.push(String(e_point)); 
                                }

                                var options = {
                                    titleY: 'Elevation (m)',
                                    curveType: 'function',
                                    legend: 'none',
                                    height: 300,
                                };

                                // Draw the chart using the data within its DIV.
                                chart.draw(data, options);

                                // Save data to JSON file
                                /*
                                    var json_distance_ab = JSON.stringify(String(distance_ab_km));
                                    var json_a_hight = JSON.stringify(String(point_a_hight));
                                    var json_b_hight = JSON.stringify(String(point_b_hight));
                                    var json_distance = JSON.stringify(point_distance);
                                    var json_elevation = JSON.stringify(point_elevation);
                                    document.getElementById("t_d_ab").innerHTML = json_distance_ab;
                                    document.getElementById("t_a_hight").innerHTML = json_a_hight;
                                    document.getElementById("t_b_hight").innerHTML = json_b_hight;
                                    document.getElementById("t_distance").innerHTML = json_distance;
                                    document.getElementById("t_elevation").innerHTML = json_elevation;
                                */
                            }

                            // Release channels and version numbers:
                            // https://developers.google.com/maps/documentation/javascript/versions
                            // Localizing the Map:
                            // https://developers.google.com/maps/documentation/javascript/localization
                        </script>
                        <script async defer
                            src="https://maps.googleapis.com/maps/api/YOUR_API">
                        </script>
                    </div>
                </body>
            </html>
        ''')

        self.webView.setHtml(google_html_page)

    # проверка неправильного ввода (посимвольный перебор)
    def input_check(self, input_str, style):
        if input_str != "" \
                and not input_str.__eq__("-.") \
                and not input_str.__eq__(".") \
                and not input_str.__eq__("-") \
                and input_str.__len__() < 16:

            is_float = False
            dot = 0
            minus = 0
            style_from_coordinates = [self.le_lat_a, self.le_lng_a,
                                      self.le_lat_b, self.le_lng_b]
            style_sheet_coord = "background-color: rgb(179, 229, 252);"  # blue
            style_sheet_main = "background-color: rgb(197, 225, 165);"  # green
            style_sheet_else = "background-color: rgb(224, 224, 224);"  # grey

            for i in input_str:
                if i.isnumeric() or i == ".":  # add (or i == "-" in input_str[0]) --
                    #  if you want minus values like -53.25 but not 5-3.25
                    if i == ".":
                        dot += 1
                    if i == "-":
                        minus += 1

                    if dot < 2 and minus < 2:
                        # print("i = " + str(i))
                        is_float = True
                        # print("is_float: " + str(is_float))
                        if style in style_from_coordinates:
                            style.setStyleSheet(style_sheet_coord)
                        else:
                            style.setStyleSheet(style_sheet_else)
                    else:
                        is_float = False
                        dot = 0  # do NOT dell
                        minus = 0  # do NOT dell
                        # print(" - 2 dot or 2 minus")
                        style.setStyleSheet("background-color: rgb(239, 41, 41);")  # red
                        break
                else:
                    is_float = False
                    # print("is_float: " + str(is_float))
                    style.setStyleSheet("background-color: rgb(239, 41, 41);")  # red
                    # print(" - error: char in the input")
                    break
            if is_float:
                # print("obj = " + str(float(obj)))
                return float(input_str)
        else:
            style.setStyleSheet("background-color: rgb(239, 41, 41);")  # red
            # print(" - error: wrong input " + str(input_str))

        return -1

    # заполнение форм случайными значениями из диапазона
    def fill_forms(self):
        print("fill_forms()")

        self.webView.setUrl(QtCore.QUrl("http://localhost/index.html"))

        # lat_a = random.randint(53156653, 54082254) / 1000000
        # lng_a = random.randint(24884033, 26976929) / 1000000
        # lat_b = random.randint(53156653, 54082254) / 1000000
        # lng_b = random.randint(24884033, 26976929) / 1000000

        lat_a = 53.822975
        lng_a = 27.087467
        lat_b = 52.911044
        lng_b = 27.691194

        self.le_lat_a.setText(str(lat_a))
        self.le_lng_a.setText(str(lng_a))
        self.le_lat_b.setText(str(lat_b))
        self.le_lng_b.setText(str(lng_b))

        print("\tOK - fill_forms()")
