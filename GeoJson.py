import json
import math
import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Cursor

from logs.Log_Color import log_verbose, log_warning, log_info, log_error


class ElevationCalculation:
    def __init__(self):
        self.number_of_points = 0
        self.path_points = []
        self.ar_d_min = []
        self.ar_elevation = []
        self.ar_latlng_min = []
        self.delta_lat = 0.00833  # ~1 km
        self.delta_lng = 0.013  # ~1 km

    def main(self, ar_p: list) -> np.ndarray:
        """

        :param ar_p: [lat0a, lng0a, lat0b, lng0b]
        :return:
        """
        log_verbose("ElevationCalculation: main()")
        start_time_0 = time.perf_counter()

        d_ab = self.distance(ar_p)
        log_info("\td_ab: %.3f km" % d_ab)
        self.number_of_points = int(d_ab) * 1  # количество точек на маршруте

        self.path_points = self.path(ar_p, self.number_of_points)  # [point_in_path, n_points]
        self.number_of_points = self.path_points[1]

        self.ar_d_min = np.zeros(self.number_of_points)  # np.zeros(self.number_of_points) ; [0.0] * p
        self.ar_elevation = np.zeros(self.number_of_points)  # np.zeros(self.number_of_points) ; [0.0] * p
        self.ar_latlng_min = [[0.0, 0.0]] * self.number_of_points  # np.zeros([p, 2]) ; [[0.0, 0.0]] * p

        db_list = self.open_db(ar_p)
        self.find_points(db_list)

        # log_info("\t[" + str(len(self.ar_latlng_min)) + "] latlng_min: " + str(self.ar_latlng_min) +
        #          "\t\n[" + str(len(self.ar_elevation)) + "] elev_min: " + str(self.ar_elevation) +
        #          "\t\n[" + str(len(self.ar_d_min)) + "] d_min: " + str(self.ar_d_min))

        self.create_json(ar_p, self.ar_latlng_min)

        log_info("\ttime_main: %.6f" % (time.perf_counter() - start_time_0))

        return self.ar_elevation

    def open_db(self, _co: list) -> list:
        """
        :_co: [lat0a, lng0a, lat0b, lng0b]
        :return:
        """
        log_verbose("ElevationCalculation: open_db()")
        time0_db = time.perf_counter()

        max_lat = max(_co[0], _co[2]) + self.delta_lat
        max_lng = max(_co[1], _co[3]) + self.delta_lng
        min_lat = min(_co[0], _co[2]) - self.delta_lat
        min_lng = min(_co[1], _co[3]) - self.delta_lng

        row = []
        db = sqlite3.connect('data/db_elev_1m.sqlite3')
        cursor = db.cursor()
        try:
            row = cursor.execute("SELECT * FROM elevation" +
                                 " WHERE lat BETWEEN " + str(min_lat) + " AND " + str(max_lat) +
                                 " AND lng BETWEEN " + str(min_lng) + " AND " + str(max_lng)).fetchall()
        except sqlite3.DatabaseError as err:
            log_error("\tDB Error: %s" % err)
        else:
            db.commit()

        db.close()
        log_warning("\tlen(db_list): %s" % len(row))
        log_info("\ttime_db: %.6f" % (time.perf_counter() - time0_db))
        return row

    def distance(self, _co: list) -> float:
        """
        wiki - https://...
        r = 6363.513 = for BLR, Minsk; evr. r on the Earth = 6378.137 km

        :param _co: [lat A, lng A, lat B, lng B]
        """
        rad_lat_a = math.radians(_co[0])
        rad_lat_b = math.radians(_co[2])
        rad_lng_a = math.radians(_co[1])
        rad_lng_b = math.radians(_co[3])
        central_angle = math.acos(math.sin(rad_lat_a) * math.sin(rad_lat_b) +
                                  math.cos(rad_lat_a) * math.cos(rad_lat_b) * math.cos(rad_lng_a - rad_lng_b))
        r = 6378.137
        dist = r * central_angle  # km
        return dist

    def path(self, _co, n_points: int, delta_lat=0.0, delta_lng=0.0) -> (list, int):
        """ нахождение Х точек на маршруте

        :param _co: [lat A, lng A, lat B, lng B]
        :param n_points:
        :param delta_lat: zero or ~1km
        :param delta_lng: zero or ~1km
        :return:
        """
        log_verbose("ElevationCalculation: path()")
        time0_path = time.perf_counter()

        dif_coord_per_point = [math.fabs(_co[0] - _co[2]) / n_points,  # расстояние в градусах между каждой из
                               math.fabs(_co[1] - _co[3]) / n_points]  # соседних точек на маршруте А - В,
        log_info("\tdif_coord_per_point: %s" % dif_coord_per_point)

        point_in_path = []  # np.zeros([self.number_of_points + 1, 2])       # x3 slower if using numpy
        for cp in range(0, n_points, 1):
            if _co[0] < _co[2] and _co[1] < _co[3]:
                a = _co[0] + (dif_coord_per_point[0] * cp) + delta_lat
                b = _co[1] + (dif_coord_per_point[1] * cp) + delta_lng
                point_in_path.append([a, b])
            elif _co[0] < _co[2] and _co[1] > _co[3]:
                c = _co[0] + (dif_coord_per_point[0] * cp) + delta_lat
                d = _co[1] - (dif_coord_per_point[1] * cp) + delta_lng
                point_in_path.append([c, d])
            elif _co[0] > _co[2] and _co[1] > _co[3]:
                e = _co[0] - (dif_coord_per_point[0] * cp) - delta_lat
                f = _co[1] - (dif_coord_per_point[1] * cp) - delta_lng
                point_in_path.append([e, f])
            elif _co[0] > _co[2] and _co[1] < _co[3]:
                g = _co[0] - (dif_coord_per_point[0] * cp) - delta_lat
                h = _co[1] + (dif_coord_per_point[1] * cp) + delta_lng
                point_in_path.append([g, h])

        point_in_path.append([_co[2], _co[3]])  # add point 'B'
        n_points += 1
        # log_info("\tpoint_in_path: [" + str(n_points) + "]; " + str(point_in_path))

        log_info("\ttime_path: %.6f" % (time.perf_counter() - time0_path))

        return point_in_path, n_points

    def find_points(self, row_db: list):
        """

        :param row_db: data from DB got with .fetchall()
        :return:
        """
        log_verbose("ElevationCalculation: find_points()")
        time0_find_points = time.perf_counter()
        time_i = 0  # timers for benchmarking
        arr_len = 0

        for db_point in row_db:
            start_time_i = time.perf_counter()

            self.main_calculation(db_point)

            time_i += time.perf_counter() - start_time_i
            arr_len += 1

        log_info("\ttime_i: %.6f sec, arr_len: %s, sum: %.6f" % (time_i / arr_len, arr_len, time_i))

        time_find_points = time.perf_counter() - time0_find_points
        log_warning("\tTIME_FIND_POINTS: %.6f sec (%.3f min)" % (time_find_points, time_find_points / 60))

    def main_calculation(self, point: list) -> None:
        lat = point[0]
        lng = point[1]
        elev = point[2]
        for x in range(self.number_of_points):
            lat_x = self.path_points[0][x][0]
            lng_x = self.path_points[0][x][1]

            abs_lat = math.fabs(lat_x - lat)
            abs_lng = math.fabs(lng_x - lng)
            if abs_lat < self.delta_lat and abs_lng < self.delta_lng:

                d_min_x = self.distance([lat_x, lng_x, lat, lng])
                if d_min_x < self.ar_d_min[x]:
                    self.ar_latlng_min[x] = [lat, lng]
                    self.ar_elevation[x] = elev
                    self.ar_d_min[x] = d_min_x
                elif self.ar_latlng_min[x][0] == 0 and self.ar_latlng_min[x][1] == 0:
                    self.ar_latlng_min[x] = [lat, lng]
                    self.ar_elevation[x] = elev
                    self.ar_d_min[x] = d_min_x

    def create_json(self, _co: list, latlng_min: list) -> None:
        """ Use in index_v1.html to a check rial path

        :param _co: [lat A, lng A, lat B, lng B]
        :param latlng_min:
        :return: creates html/test.json file
        """
        log_verbose("ElevationCalculation: create_json()")
        time0_create_json = time.perf_counter()

        json_data = {
            "point": [
                {"lat": _co[0], "lng": _co[2]},  # , "elev_a": elev_min[0]
                {"lat": _co[1], "lng": _co[3]}  # , "elev_b": elev_min[self.number_of_points - 1]
            ],
            "path": latlng_min,
            # "elev": elevation
        }
        with open("html/test.json", "w", encoding="utf8") as write_file:
            json.dump(json_data, write_file)
            write_file.close()

        log_info("\ttime_create_json: %.6f" % (time.perf_counter() - time0_create_json))

    def plot_elevation_in_separate_window(self, n_points: int, elev: list, earth_h: float) -> None:
        log_verbose("ElevationCalculation: plot_elevation_in_separate_window()")
        time0_plot = time.perf_counter()

        x1 = np.linspace(0, n_points, num=n_points)  # km
        y1 = np.sin(2 * np.pi * x1 / (n_points * 2)) * 0.05  # km

        y2 = [0.0] * x1
        for q in range(0, n_points):
            y2[q] = elev[q] / 1000  # km

        labels = ["земля " + format(earth_h, '.3f') + " m", "высоты"]
        fig, ax = plt.subplots()
        ax.stackplot(x1, y1, y2, labels=labels)

        # plotting magic
        plt.legend()
        plt.grid(True)
        plt.tight_layout(0.5, 0.5, 0.5, None)
        plt.autoscale(enable=True, axis='both', tight=True)
        fig.set_size_inches(14, 4)
        cursor = Cursor(ax, useblit=True, color='black', linewidth=1)

        log_info("\ttime_plot: %.6f" % (time.perf_counter() - time0_plot))

        plt.show()

    def earth_height(self, arr_points_ab: list) -> float:
        """ высота земной поверхности над хордой;
        Земля круглая -> т.е. хорда - это наикратчайшее растояние между точками А и Б через Землю

        :param arr_points_ab: [lat A, lng A, lat B, lng B]
        :return: earth height in km !!!
        """
        log_verbose("ElevationCalculation: earth_height()")

        rad_lat_a = math.radians(arr_points_ab[0])  # lat_a
        rad_lat_b = math.radians(arr_points_ab[1])  # lat_b
        rad_lng_a = math.radians(arr_points_ab[2])  # lng_a
        rad_lng_b = math.radians(arr_points_ab[3])  # lng_b

        central_angle = math.acos(math.sin(rad_lat_a) * math.sin(rad_lat_b) +
                                  math.cos(rad_lat_a) * math.cos(rad_lat_b) * math.cos(
            rad_lng_a - rad_lng_b))  # radians

        r = 6378.137  # 6363.513 = for BLR \ Minsk; evr = 6378.137 km
        earth_h = r - (r * math.cos(central_angle / 2))  # km

        log_info("\tearth_height = %.3f" % earth_h)
        return earth_h

    def do_it_with_mp(self, co: list, path_divide=10, workers=4) -> list:
        """ multiprocessing

        :param co: [lat A, lng A, lat B, lng B]
        :param path_divide: path divide coefficient
        :param workers: number of CPU workers
        :return: elevation list
        """
        log_verbose("ElevationCalculation: do_it_with_mp()")
        to = time.perf_counter()

        """divide coordinates from A to B to sub arrays
        10 lines, delta_ ~1km"""
        divided_coordinates = self.path(co, path_divide, self.delta_lat, self.delta_lng)[0]

        new_coordinates_arr = np.zeros((path_divide, 4))  # new arr: [[lat_a, lng_a, lat_p1, lng_p1],
        for i in range(path_divide):  # [lat_p1, lng_p1, lat_p2, lng_p2], [lat_p2, lng_p2, lat_p3...
            new_coordinates_arr[i][0] = divided_coordinates[i][0]
            new_coordinates_arr[i][1] = divided_coordinates[i][1]
            new_coordinates_arr[i][2] = divided_coordinates[i + 1][0]
            new_coordinates_arr[i][3] = divided_coordinates[i + 1][1]

        qq = []  # sum array of elevation from multiprocess

        with ProcessPoolExecutor(max_workers=workers) as executor:  # max_workers=4
            for i, j in zip(new_coordinates_arr, executor.map(self.main, new_coordinates_arr)):
                qq.extend(j)

        eh = self.earth_height(co)  # all path from A to B

        log_warning("\t Multiprocessing time = %.6f" % (time.perf_counter() - to))

        self.plot_elevation_in_separate_window(len(qq), qq, eh)

        return qq

    def do_it_normal_way(self, _coord: list) -> None:
        elevation_array = self.main(_coord)
        eh = self.earth_height(_coord)
        self.plot_elevation_in_separate_window(len(elevation_array), elevation_array, eh)


if __name__ == '__main__':
    log_verbose("ElevationCalculation: Running ElevationCalculation Test")

    test_coordinates = [53.822975, 27.087467, 52.911044, 27.691194]  # 110 km
    # test_coordinates = [53.672568, 23.996519, 52.707798, 28.255368]  # 304 km
    # test_coordinates = [51.742627, 23.964322, 55.404321, 30.621924]  # 600 km

    calculate_elevation = ElevationCalculation()
    # calculate_elevation.do_it_normal_way(test_coordinates)  # normal way
    calculate_elevation.do_it_with_mp(test_coordinates)  # multiprocessing
