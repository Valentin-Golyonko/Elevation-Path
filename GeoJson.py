import json
import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Cursor

import logs.Log_Color as Logs

Logs.log_start("Please wait! Running...")
run_geojson = True

# time_x = 0
# p_len = 0
# abs_if = 0
number_of_points = 0
path_points = []
ar_d_min = []
ar_elevation = []
ar_latlng_min = []


# --------------------------------- methods ---------------------------------------
def main(ar_p):
    Logs.log_verbose("GeoJson: main()")
    start_time_0 = time.perf_counter()
    global path_points, ar_d_min, ar_elevation, ar_latlng_min, number_of_points

    # ar_p = [53.822975, 27.087467, 52.911044, 27.691194]  # Вертники, h = 292 - Слуцк, h = 146; 109.148167 km
    lat0a = ar_p[0]
    lng0a = ar_p[1]
    lat0b = ar_p[2]
    lng0b = ar_p[3]

    db_list = open_db(lat0a, lng0a, lat0b, lng0b)

    d_ab = distance(lat0a, lng0a, lat0b, lng0b)
    Logs.log_info("\td_ab: " + str(d_ab) + " km")
    number_of_points = int(d_ab) * 1  # количество точек на маршруте

    path_points = path(lat0a, lng0a, lat0b, lng0b, number_of_points)  # [point_in_path, n_points]
    number_of_points = path_points[1]

    ar_d_min = np.zeros(number_of_points)  # np.zeros(number_of_points) ; [0.0] * p
    ar_elevation = np.zeros(number_of_points)  # np.zeros(number_of_points) ; [0.0] * p
    ar_latlng_min = [[0.0, 0.0]] * number_of_points  # np.zeros([p, 2]) ; [[0.0, 0.0]] * p

    # (number_of_points, path_points, ar_d_min, ar_elevation, ar_latlng_min, db_list)
    find_points(db_list)

    Logs.log_info("\t[" + str(len(ar_latlng_min)) + "] latlng_min: " + str(ar_latlng_min) +
                  "\t\n[" + str(len(ar_elevation)) + "] elev_min: " + str(ar_elevation) +
                  "\t\n[" + str(len(ar_d_min)) + "] d_min: " + str(ar_d_min))

    create_json(lat0a, lng0a, lat0b, lng0b, ar_latlng_min)

    eh = earth_height(lat0a, lng0a, lat0b, lng0b)
    plot_elevation_in_separate_window(number_of_points, ar_elevation, eh)

    time_all = time.perf_counter() - start_time_0
    Logs.log_info("\ttime_all: " + str(time_all) + "\n")


def open_db(lat_0_a, lng_0_a, lat_0_b, lng_0_b):
    Logs.log_verbose("GeoJson: open_db()")
    time0_db = time.perf_counter()

    max_lat = int(max(lat_0_a, lat_0_b)) + 1  # int(53.8) = 53
    max_lng = int(max(lng_0_a, lng_0_b)) + 1  # so, if lat_0_a = 53.822975, lat_0_b = 52.911044
    min_lat = int(min(lat_0_a, lat_0_b))  # range(min_lat, max_lat) = 52, 53
    min_lng = int(min(lng_0_a, lng_0_b))  # step = 1

    row = []
    db = sqlite3.connect('data/elev_1m.db')
    cursor = db.cursor()
    try:
        row = cursor.execute("SELECT * FROM elevation" +
                             " WHERE lat BETWEEN " + str(min_lat) + " AND " + str(max_lat) +
                             " AND lng BETWEEN " + str(min_lng) + " AND " + str(max_lng)).fetchall()
    except sqlite3.DatabaseError as err:
        Logs.log_error("\tDB Error: " + str(err))
    else:
        db.commit()

    db.close()
    time_db = time.perf_counter() - time0_db
    Logs.log_info("\ttime_db: " + str(time_db))
    return row


def distance(lat_a, lng_a, lat_b, lng_b, ):
    rad_lat_a = math.radians(lat_a)
    rad_lat_b = math.radians(lat_b)
    rad_lng_a = math.radians(lng_a)
    rad_lng_b = math.radians(lng_b)
    central_angle = math.acos(math.sin(rad_lat_a) * math.sin(rad_lat_b) +
                              math.cos(rad_lat_a) * math.cos(rad_lat_b) * math.cos(rad_lng_a - rad_lng_b))
    r = 6378.137  # 6363.513 = for BLR \ Minsk; evr = 6378.137 km
    dist = r * central_angle  # km
    return dist


def path(lat_0_a, lng_0_a, lat_0_b, lng_0_b, n_points):
    Logs.log_verbose("GeoJson: path()")
    time0_path = time.perf_counter()

    dif_coord_per_point = [math.fabs(lat_0_a - lat_0_b) / n_points,  # расстояние в градусах между каждой из
                           math.fabs(lng_0_a - lng_0_b) / n_points]  # соседних точек на маршруте А - В,
    Logs.log_info("\tdif_coord_per_point: " + str(dif_coord_per_point))

    point_in_path = []  # np.zeros([number_of_points + 1, 2])       # 3x slower if using numpy
    for cp in range(0, n_points, 1):  # нахождение Х точек на маршруте; int(number_of_points / 2)
        if lat_0_a < lat_0_b and lng_0_a < lng_0_b:
            point_in_path.append([lat_0_a + dif_coord_per_point[0] * cp, lng_0_a + dif_coord_per_point[1] * cp])
        elif lat_0_a < lat_0_b and lng_0_a > lng_0_b:
            point_in_path.append([lat_0_a + dif_coord_per_point[0] * cp, lng_0_a - dif_coord_per_point[1] * cp])
        elif lat_0_a > lat_0_b and lng_0_a > lng_0_b:
            point_in_path.append([lat_0_a - dif_coord_per_point[0] * cp, lng_0_a - dif_coord_per_point[1] * cp])
        elif lat_0_a > lat_0_b and lng_0_a < lng_0_b:
            point_in_path.append([lat_0_a - dif_coord_per_point[0] * cp, lng_0_a + dif_coord_per_point[1] * cp])

    point_in_path.append([lat_0_b, lng_0_b])  # add point 'B'
    n_points += 1
    Logs.log_info("\tpoint_in_path: [" + str(n_points) + "]; " + str(point_in_path))

    time_path = time.perf_counter() - time0_path
    Logs.log_info("\ttime_path: " + str(time_path))

    return [point_in_path, n_points]


def find_points(row_db):
    Logs.log_verbose("GeoJson: find_points()")
    time0_find_points = time.perf_counter()
    time_i = 0  # timers for benchmarking
    arr_len = 0
    # timex = [0.0, 0, 0]
    # time_x = 0
    # p_len = 0
    # abs_if = 0

    # !!! Normal Python
    for db_point in row_db:
        start_time_i = time.perf_counter()

        main_calculation(db_point)

        time_i += time.perf_counter() - start_time_i
        arr_len += 1

    # print("\ttime_x: " + str(time_x / p_len) + " p_len: " + str(p_len) + " sum: " + str(time_x) +
    #       " abs_if: " + str(abs_if))
    Logs.log_info("\ttime_i: " + str(time_i / arr_len) + " sec, arr_len: " + str(arr_len) + " sum: " + str(time_i))

    # -------- BENCHMARK RESULT HERE --------
    time_find_points = time.perf_counter() - time0_find_points
    Logs.log_warning("\tTIME_FIND_POINTS: " + str(time_find_points) + " sec (" + str(time_find_points / 60) + " min)")

    # For simple python without MP (ProcessPoolExecutor)
    # time_i: 4.337876795356802e-05 sec, arr_len: 190561 sum: 8.266301399999875
    # TIME_FIND_POINTS: 6.977238956000008 sec (0.11628731593333347 min)

    # For MP - no result !!!


def main_calculation(point):  # (position, path_points, ar_d_min, ar_elevation, ar_latlng_min, db_row)
    global ar_d_min, ar_elevation, ar_latlng_min  # , abs_if, time_x, p_len

    lat = point[0]
    lng = point[1]
    elev = point[2]
    # print("\tpoint = %s" % str(point))
    for x in range(number_of_points):
        # start_time_x = time.perf_counter()
        lat_x = path_points[0][x][0]
        lng_x = path_points[0][x][1]

        abs_lat = math.fabs(lat_x - lat)
        abs_lng = math.fabs(lng_x - lng)
        # print("\tabs")
        if abs_lat < 0.00833 and abs_lng < 0.013:  # ~ 1 km; 4x speed up, 5m(192.06705 -> 47.2116)

            d_min_x = distance(lat_x, lng_x, lat, lng)
            # print("\td_min %.2f" % d_min_x)
            if d_min_x < ar_d_min[x]:
                ar_latlng_min[x] = [lat, lng]
                ar_elevation[x] = elev
                ar_d_min[x] = d_min_x
            elif ar_latlng_min[x][0] == 0 and ar_latlng_min[x][1] == 0:  # -3s slow down, 5m (NOT in one 'if')
                ar_latlng_min[x] = [lat, lng]
                ar_elevation[x] = elev
                ar_d_min[x] = d_min_x

            # abs_if += 1  # number of 'good' points
        # time_x += time.perf_counter() - start_time_x  # timers for benchmarking
        # p_len += 1

        # print("\tx = %d" % x)

    return True


def create_json(lat_0_a, lng_0_a, lat_0_b, lng_0_b, latlng_min):
    Logs.log_verbose("GeoJson: create_json()")
    time0_create_json = time.perf_counter()

    json_data = {
        "point": [
            {"lat": lat_0_a, "lng": lng_0_a},  # , "elev_a": elev_min[0]
            {"lat": lat_0_b, "lng": lng_0_b}  # , "elev_b": elev_min[number_of_points - 1]
        ],
        "path": latlng_min,
        # "elev": elevation
    }
    with open("html/test.json", "w", encoding="utf8") as write_file:
        json.dump(json_data, write_file)
        write_file.close()

    time_create_json = time.perf_counter() - time0_create_json
    Logs.log_info("\ttime_create_json: " + str(time_create_json))


def plot_elevation_in_separate_window(n_points, elev, earth_h):
    Logs.log_verbose("GeoJson: plot_elevation_in_separate_window()")
    time0_plot = time.perf_counter()

    x1 = np.linspace(0, n_points, num=n_points)  # km
    y1 = np.sin(2 * np.pi * x1 / (n_points * 2)) * earth_h  # km

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

    time_plot = time.perf_counter() - time0_plot
    Logs.log_info("\ttime_plot: " + str(time_plot))

    plt.show()


def earth_height(lat_a, lng_a, lat_b, lng_b):
    Logs.log_verbose("GeoJson: earth_height()")

    rad_lat_a = math.radians(lat_a)
    rad_lat_b = math.radians(lat_b)
    rad_lng_a = math.radians(lng_a)
    rad_lng_b = math.radians(lng_b)

    central_angle = math.acos(math.sin(rad_lat_a) * math.sin(rad_lat_b) +
                              math.cos(rad_lat_a) * math.cos(rad_lat_b) * math.cos(rad_lng_a - rad_lng_b))  # radians

    r = 6378.137  # 6363.513 = for BLR \ Minsk; evr = 6378.137 km
    earth_h = r - (r * math.cos(central_angle / 2))  # km, высота земной поверхности дан хордой

    Logs.log_info("\tearth_height = " + str(earth_h))
    return earth_h


def do_it_with_mp(co):
    with ProcessPoolExecutor() as ex:  # max_workers=4
        re = ex.submit(main, co)
        Logs.log_info("\tProcessPoolExecutor Done: " + str(re))


# ------------------------------------- main --------------------------------------------- if need to test something
if __name__ == '__main__':
    if run_geojson:
        Logs.log_verbose("Running GeoJson Test")
        ar = [53.822975, 27.087467, 52.911044, 27.691194]   # Вертники, h = 292 - Слуцк, h = 146; 109.148167 km

        sr_lat = (ar[0] + ar[2]) / 2
        sr_lng = (ar[1] + ar[3]) / 2

        ar_1 = [ar[0], ar[1], sr_lat, sr_lng]
        ar_2 = [sr_lat, sr_lng, ar[2], ar[3]]
        ar_3 = [ar_1, ar_2]

        # main(ar)

        # import multiprocessing as mp
        # pr = []
        # for i in range(1):
        #     p = mp.Process(target=main, args=(ar, ))
        #     pr.append(p)
        #     p.start()
        # for prs in pr:
        #     prs.join()

        # !!! multiprocessing, multi threads
        with ProcessPoolExecutor() as executor:  # max_workers=4
            rez_1 = executor.map(main, ar_3)
            # rez_2 = executor.submit(main, ar_2)
            Logs.log_info("\tProcessPoolExecutor Done: " + str(rez_1))
            # Logs.log_info("\tProcessPoolExecutor Done: " + str(rez_2))
