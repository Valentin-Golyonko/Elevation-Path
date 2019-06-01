import json
import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor

import math
import matplotlib.pyplot as plt
import numpy as np

print("Please wait! Running...")
run_geojson = True
# time_x = 0
# p_len = 0
# abs_if = 0


# --------------------------------- methods ---------------------------------------
def main_calculation(point):
    # (position, path_points, ar_d_min, ar_elevation, ar_latlng_min, db_row)
    # global row, points_in_path, d_min, elev_min, latlng_min  # , abs_if, time_x, p_len

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


def find_points(row_db):
    # (number_points, path_p, ar_d, ar_elev, ar_ll, row_db)
    print("GeoJson: find_points()")
    # global number_of_points, d_ab, point_in_path, d_min, elev_min, latlng_min  # , time_x, p_len, abs_if,
    time0_find_points = time.perf_counter()
    time_i = 0  # timers for benchmarking
    arr_len = 0
    # timex = [0.0, 0, 0]
    # time_x = 0
    # p_len = 0
    # abs_if = 0

    # with ProcessPoolExecutor() as executor:
    #     for count, rez in zip(row_db, executor.map(main_calculation, row_db)):
    #         start_time_i = time.perf_counter()
    #
    #         count += 1
    #         print("\t count = %d %s" % (count, rez))
    #
    #         time_i += time.perf_counter() - start_time_i
    #         arr_len += 1

    # for db_point in row_db:
    #     start_time_i = time.perf_counter()
    #
    #     executor = ProcessPoolExecutor(max_workers=2)
    #     task1 = executor.submit(main_calculation, db_point)
    #     print("\t task1 is %s" % str(task1))
    #
    #     time_i += time.perf_counter() - start_time_i
    #     arr_len += 1

    for db_point in row_db:
        start_time_i = time.perf_counter()

        main_calculation(db_point)

        time_i += time.perf_counter() - start_time_i
        arr_len += 1

    # time_i: 4.337876795356802e-05 arr_len: 190561 sum: 8.266301399999875
    # time_find_points: 8.8459885 (0.14743314166666668 min)

    # print("\ttime_x: " + str(time_x / p_len) + " p_len: " + str(p_len) + " sum: " + str(time_x) +
    #       " abs_if: " + str(abs_if))
    print("\ttime_i: " + str(time_i / arr_len) + " arr_len: " + str(arr_len) + " sum: " + str(time_i))
    time_find_points = time.perf_counter() - time0_find_points
    print("\t!time_find_points: " + str(time_find_points) + " (" + str(time_find_points / 60) + " min)")


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


def earth_height(lat_a, lng_a, lat_b, lng_b):
    print("GeoJson: earth_height()")

    rad_lat_a = math.radians(lat_a)
    rad_lat_b = math.radians(lat_b)
    rad_lng_a = math.radians(lng_a)
    rad_lng_b = math.radians(lng_b)

    central_angle = math.acos(math.sin(rad_lat_a) * math.sin(rad_lat_b) +
                              math.cos(rad_lat_a) * math.cos(rad_lat_b) * math.cos(rad_lng_a - rad_lng_b))  # radians

    r = 6378.137  # 6363.513 = for BLR \ Minsk; evr = 6378.137 km
    earth_h = r - (r * math.cos(central_angle / 2))  # km, высота земной поверхности дан хордой
    print("\tearth_height = " + str(earth_h))
    return earth_h


def create_json(lat_0_a, lng_0_a, lat_0_b, lng_0_b, latlng_min):
    print("GeoJson: create_json()")
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
    print("\ttime_create_json: " + str(time_create_json))


def plot_elevation_in_separate_window(n_points, elev):
    print("GeoJson: plot_elevation_in_separate_window()")
    time0_plot = time.perf_counter()

    x = range(0, n_points)
    y1 = np.zeros(n_points)
    for q in range(0, n_points):
        y1[q] = elev[q]

    labels = ["elev_min_5m ", "d_min", "Odds"]
    fig, ax = plt.subplots()
    ax.stackplot(x, y1, labels=labels)
    ax.legend(loc='upper left')
    fig.set_size_inches(15, 5)

    time_plot = time.perf_counter() - time0_plot
    print("\ttime_plot: " + str(time_plot))

    plt.show()


def open_db(lat_0_a, lng_0_a, lat_0_b, lng_0_b):
    print("GeoJson: open_db()")
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
                             " AND lng BETWEEN " + str(min_lng) + " AND " + str(max_lng))
    except sqlite3.DatabaseError as err:
        print("\tError: ", err)
    else:
        db.commit()

    time_db = time.perf_counter() - time0_db
    print("\ttime_db: " + str(time_db))
    return row


def path(lat_0_a, lng_0_a, lat_0_b, lng_0_b, n_points):
    print("GeoJson: path()")
    time0_path = time.perf_counter()

    dif_coord_per_point = [math.fabs(lat_0_a - lat_0_b) / n_points,  # расстояние в градусах между каждой из
                           math.fabs(lng_0_a - lng_0_b) / n_points]  # соседних точек на маршруте А - В,
    print("\tdif_coord_per_point: " + str(dif_coord_per_point))

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
    print("\tpoint_in_path: [" + str(n_points) + "]; " + str(point_in_path))

    time_path = time.perf_counter() - time0_path
    print("\ttime_path: " + str(time_path))

    return [point_in_path, n_points]


def main():
    print("GeoJson: main()")
    start_time_0 = time.perf_counter()
    global db_row, path_points, ar_d_min, ar_elevation, ar_latlng_min, number_of_points

    lat0a = 53.822975  # Вертники, h = 292
    lng0a = 27.087467
    lat0b = 52.911044  # Слуцк, h = 146
    lng0b = 27.691194
    # d_ab: 109.148167 km
    # time_2.1: 0.0002782 s
    # time_2.3: 5.1453380 s     5m
    # time_2.3: 12-16 s     1m

    db_row = open_db(lat0a, lng0a, lat0b, lng0b)

    d_ab = distance(lat0a, lng0a, lat0b, lng0b)
    print("\td_ab: " + str(d_ab) + " km")
    number_of_points = int(d_ab) * 1  # количество точек на маршруте

    path_points = path(lat0a, lng0a, lat0b, lng0b, number_of_points)    # [point_in_path, n_points]
    number_of_points = path_points[1]

    ar_d_min = np.zeros(number_of_points)  # np.zeros(number_of_points) ; [0.0] * p
    ar_elevation = np.zeros(number_of_points)  # np.zeros(number_of_points) ; [0.0] * p
    ar_latlng_min = [[0.0, 0.0]] * number_of_points  # np.zeros([p, 2]) ; [[0.0, 0.0]] * p

    # (number_of_points, path_points, ar_d_min, ar_elevation, ar_latlng_min, db_row)
    find_points(db_row)

    db_row.close()
    print("\t[" + str(len(ar_latlng_min)) + "] latlng_min: " + str(ar_latlng_min) +
          "\t\n[" + str(len(ar_elevation)) + "] elev_min: " + str(ar_elevation) +
          "\t\n[" + str(len(ar_d_min)) + "] d_min: " + str(ar_d_min))

    create_json(lat0a, lng0a, lat0b, lng0b, ar_latlng_min)

    time_all = time.perf_counter() - start_time_0
    print("\ttime_all: " + str(time_all) + "\n")

    plot_elevation_in_separate_window(number_of_points, ar_elevation)


# ------------------------------------- main --------------------------------------------- if need to test something
if __name__ == '__main__':
    if run_geojson:
        main()
