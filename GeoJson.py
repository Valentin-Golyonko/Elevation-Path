import json
import sqlite3
import time

import math
import matplotlib.pyplot as plt
import numpy as np

print("Please wait! Running...")
start_time_0 = time.perf_counter()  # time.perf_counter, time.process_time

run_geojson = False
number_of_points = 0
elev_min = np.zeros(number_of_points)
d_ab = 0
max_betta_a = 0.0
max_betta_b = 0.0
i_beta_a = 0
i_beta_b = 0


# --------------------------------- methods ---------------------------------------
def find_points(lat_0_a, lng_0_a, lat_0_b, lng_0_b):
    global elev_min, latlng_min, number_of_points, d_min, d_ab
    time_20 = time.perf_counter()

    max_lat = int(max(lat_0_a, lat_0_b)) + 1  # int(53.8) = 53
    max_lng = int(max(lng_0_a, lng_0_b)) + 1  # so, if lat_0_a = 53.822975, lat_0_b = 52.911044
    min_lat = int(min(lat_0_a, lat_0_b))  # range(min_lat, max_lat) = 52, 53
    min_lng = int(min(lng_0_a, lng_0_b))  # step = 1

    d_ab = distance(lat_0_a, lng_0_a, lat_0_b, lng_0_b)
    print("d_ab: " + str(d_ab) + " km")

    number_of_points = int(d_ab) * 1  # количество точек на маршруте

    dif_coord_per_point = [math.fabs(lat_0_a - lat_0_b) / number_of_points,  # расстояние в градусах между каждой из
                           math.fabs(lng_0_a - lng_0_b) / number_of_points]  # соседних точек на маршруте А - В,
    print("dif_coord_per_point: " + str(dif_coord_per_point))

    point_in_path = []  # np.zeros([number_of_points + 1, 2])       # 3x slower using numpy
    for cp in range(0, number_of_points, 1):  # нахождение Х точек на маршруте; int(number_of_points / 2)
        if lat_0_a < lat_0_b and lng_0_a < lng_0_b:
            point_in_path.append([lat_0_a + dif_coord_per_point[0] * cp, lng_0_a + dif_coord_per_point[1] * cp])
        elif lat_0_a < lat_0_b and lng_0_a > lng_0_b:
            point_in_path.append([lat_0_a + dif_coord_per_point[0] * cp, lng_0_a - dif_coord_per_point[1] * cp])
        elif lat_0_a > lat_0_b and lng_0_a > lng_0_b:
            point_in_path.append([lat_0_a - dif_coord_per_point[0] * cp, lng_0_a - dif_coord_per_point[1] * cp])
        elif lat_0_a > lat_0_b and lng_0_a < lng_0_b:
            point_in_path.append([lat_0_a - dif_coord_per_point[0] * cp, lng_0_a + dif_coord_per_point[1] * cp])

    point_in_path.append([lat_0_b, lng_0_b])  # add point 'B'
    number_of_points += 1
    print("point_in_path: " + str(point_in_path))

    time_21 = time.perf_counter() - time_20
    print("\ttime_2.1: " + str(time_21))

    d_min = np.zeros(number_of_points)  # np.zeros(number_of_points) ; [0.0] * p
    elev_min = np.zeros(number_of_points)  # np.zeros(number_of_points) ; [0.0] * p
    latlng_min = [[0.0, 0.0]] * number_of_points  # np.zeros([p, 2]) ; [[0.0, 0.0]] * p

    time_x = 0  # timers for benchmarking
    p_len = 0
    time_i = 0
    arr_len = 0
    abs_if = 0

    time_22 = time.perf_counter() - time_20
    print("\ttime_2.2: " + str(time_22))

    db = sqlite3.connect('elev_5m.db')
    cursor = db.cursor()

    try:
        for row in cursor.execute("SELECT * FROM elevation"):
            start_time_i = time.perf_counter()  # timer for benchmarking
            lng = row[1]
            lat = row[0]
            elev = row[2]
            ilat = int(lat)
            ilng = int(lng)

            if ilat in range(min_lat, max_lat):  # (v1) summary speed up  = 18.2x, 1m(1093.9562 sec -> 60.0305 sec)
                if ilng in range(min_lng, max_lng):  # (v2) 1m -> time_2.3: 16.39s, time_all: 39.01s ; 28x

                    for x in range(0, number_of_points):
                        start_time_x = time.perf_counter()  # timer for benchmarking
                        lat_x = point_in_path[x][0]
                        lng_x = point_in_path[x][1]

                        abs_lat = math.fabs(lat_x - lat)
                        abs_lng = math.fabs(lng_x - lng)
                        if abs_lat < 0.00833 and abs_lng < 0.013:  # ~ 1 km; 4x speed up, 5m(192.06705 -> 47.2116)

                            d_min_x = distance(lat_x, lng_x, lat, lng)
                            if d_min_x < d_min[x]:
                                latlng_min[x] = [lat, lng]
                                elev_min[x] = elev
                                d_min[x] = d_min_x
                            elif latlng_min[x][0] == 0 and latlng_min[x][1] == 0:  # -3s speed up, 5m (NOT in one 'if')
                                latlng_min[x] = [lat, lng]
                                elev_min[x] = elev
                                d_min[x] = d_min_x

                            abs_if += 1  # number of 'good' points

                        time_x += time.perf_counter() - start_time_x  # timers for benchmarking
                        p_len += 1
            time_i += time.perf_counter() - start_time_i
            arr_len += 1

    except sqlite3.DatabaseError as err:
        print("\tError: ", err)
    else:
        db.commit()
    db.close()

    # show timers (benchmark)
    print("\ttime_x: " + str(time_x / p_len) + " p_len: " + str(p_len) + " sum: " + str(time_x) +
          " abs_if: " + str(abs_if) +
          "\n\ttime_i: " + str(time_i / arr_len) + " arr_len: " + str(arr_len) + " sum: " + str(time_i))

    print("[" + str(len(latlng_min)) + "] latlng_min: " + str(latlng_min) +
          "\n[" + str(len(elev_min)) + "] elev_min: " + str(elev_min) +
          "\n[" + str(len(d_min)) + "] d_min: " + str(d_min))

    time_23 = time.perf_counter() - time_20
    print("\ttime_2.3: " + str(time_23) + " (" + str(time_23 / 60) + " min)")
    time_3 = time.perf_counter() - start_time_0
    print("\ttime_3: " + str(time_3) + " (" + str(time_3 / 60) + " min)")


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


def create_json(lat_0_a, lng_0_a, lat_0_b, lng_0_b):
    print("GeoJson: create_json()")

    json_data = {
        "point": [
            {"lat": lat_0_a, "lng": lng_0_a},  # , "elev_a": elev_min[0]
            {"lat": lat_0_b, "lng": lng_0_b}  # , "elev_b": elev_min[number_of_points - 1]
        ],
        "path": latlng_min,
        # "elev": elevation
    }
    with open("html/test.json", "w") as write_file:  # TODO: 'user'
        json.dump(json_data, write_file)
        # write_file.close()

    time_4 = time.perf_counter() - start_time_0
    print("\ttime_4: " + str(time_4))


def plot_elevation_in_separate_window():
    print("GeoJson: plot_elevation()")

    x = range(0, number_of_points)
    y1 = np.zeros(number_of_points)
    for q in range(0, number_of_points):
        y1[q] = elev_min[q]

    labels = ["elev_min_5m ", "d_min", "Odds"]
    fig, ax = plt.subplots()
    ax.stackplot(x, y1, labels=labels)
    ax.legend(loc='upper left')
    fig.set_size_inches(15, 5)

    time_5 = time.perf_counter() - start_time_0
    print("\ttime_5: " + str(time_5))

    plt.show()


# ------------------------------------- main --------------------------------------------- if need to test something
if run_geojson:
    lat0a = 53.822975  # Вертники, h = 292
    lng0a = 27.087467
    lat0b = 52.911044  # Слуцк, h = 146
    lng0b = 27.691194
    # d_ab: 109.148167 km
    # time_2.1: 0.0002782 s
    # time_2.3: 5.1453380 s

    find_points(lat0a, lng0a, lat0b, lng0b)

    create_json(lat0a, lng0a, lat0b, lng0b)

    plot_elevation_in_separate_window()

    time_all = time.perf_counter() - start_time_0
    print("\ttime_all: " + str(time_all) + "\n")
