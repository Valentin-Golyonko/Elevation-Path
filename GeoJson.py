import json
import math
import time

import geojson
import matplotlib.pyplot as plt
import numpy as np

print("Please wait! Running...")
start_time_0 = time.perf_counter()  # time.perf_counter, time.process_time

test_json = False
run_geojson = False
number_of_points = 0
elev_min = np.zeros(number_of_points)
d_ab = 0
max_betta_a = 0.0
max_betta_b = 0.0


# --------------------------------- methods ---------------------------------------
def open_geojson_5m():
    global data
    with open('blr_elev_5m_v2.geojson') as f:  # blr_elev_1m_v1.geojson / blr_elev_5m_v2.geojson / test.geojson
        data = geojson.load(f)

    time_1 = time.perf_counter() - start_time_0
    print("\ttime_1: " + str(time_1))


def open_geojson_1m():
    global data
    with open('blr_elev_1m_v1.geojson') as f:  # blr_elev_1m_v1.geojson / blr_elev_5m_v2.geojson / test.geojson
        data = geojson.load(f)

    time_1 = time.perf_counter() - start_time_0
    print("\ttime_1: " + str(time_1))


def test_geojson():
    count = 0
    len_arr = 0

    for feature_t in data['features']:
        arr_t = feature_t['geometry']['coordinates']

        if len(arr_t) > 1:
            len_arr += 1

        for i in arr_t[0]:
            count += 1
            lng = i[0]
            lat = i[1]
            elev = feature_t['properties']['ELEV']
            # print(str(count) + ": " + str(lng) + " " + str(lat) + " " + str(elev))
    print("len_arr = " + str(len_arr) + "; count = " + str(count))


def find_points(lat_0_a, lng_0_a, lat_0_b, lng_0_b):
    global elev_min, latlng_min, number_of_points, d_min, d_ab
    time_20 = time.perf_counter()

    max_lat = int(max(lat_0_a, lat_0_b)) + 1  # int(53.8) = 53
    max_lng = int(max(lng_0_a, lng_0_b)) + 1  # so, if lat_0_a = 53.822975, lat_0_b = 52.911044
    min_lat = int(min(lat_0_a, lat_0_b))  # range(min_lat, max_lat) = 52, 53
    min_lng = int(min(lng_0_a, lng_0_b))  # step = 1

    d_ab = distance(lat_0_a, lng_0_a, lat_0_b, lng_0_b)
    print("d_ab: " + str(d_ab) + " km")

    number_of_points = int(d_ab)  # количество точек на маршруте

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
    time_f = 0
    f_len = 0
    abs_if = 0

    time_22 = time.perf_counter() - time_20
    print("\ttime_2.2: " + str(time_22))

    for feature in data['features']:
        start_time_f = time.perf_counter()  # timer for benchmarking
        arr = feature['geometry']['coordinates'][0]  # ex. from .geojson - "ing", "coordinates": [ [ [ 24.418315, "
        elev = feature['properties']['ELEV']

        for poi in arr:
            start_time_i = time.perf_counter()  # timer for benchmarking
            lng = poi[0]
            lat = poi[1]
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
        time_f += time.perf_counter() - start_time_f
        f_len += 1

    # show timers (benchmark)
    print("\ttime_x: " + str(time_x / p_len) + " p_len: " + str(p_len) + " sum: " + str(time_x) +
          " abs_if: " + str(abs_if) +
          "\n\ttime_i: " + str(time_i / arr_len) + " arr_len: " + str(arr_len) + " sum: " + str(time_i) +
          "\n\ttime_f: " + str(time_f / f_len) + " f_len: " + str(f_len) + " sum: " + str(time_f))

    print("[" + str(len(latlng_min)) + "] latlng_min: " + str(latlng_min) +
          "\n[" + str(len(elev_min)) + "] elev_min: " + str(elev_min) +
          "\n[" + str(len(d_min)) + "] d_min: " + str(d_min))

    time_23 = time.perf_counter() - time_20
    print("\ttime_2.3: " + str(time_23))
    time_3 = time.perf_counter() - start_time_0
    print("\ttime_3: " + str(time_3))


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
    with open("/home/bequite//PycharmProjects/Horizon/html/test.json", "w") as write_file:  # TODO: 'user'
        json.dump(json_data, write_file)
        # write_file.close()

    time_4 = time.perf_counter() - start_time_0
    print("\ttime_4: " + str(time_4))


def plot_path():
    print("plot_path()")

    x = range(0, number_of_points)

    y1 = np.zeros(number_of_points)
    s = 0
    for q in range(0, number_of_points):
        y1[q] = elev_min[q] + math.sin(s)
        s += np.pi / number_of_points

    y2 = range(0, len(d_min))
    y3 = [1, 3, 5, 7, 9]

    labels = ["elev_min_5m ", "d_min", "Odds"]
    fig, ax = plt.subplots()
    ax.stackplot(x, y1, labels=labels)  # ax.stackplot(x, y1, y2, labels=labels)
    ax.legend(loc='upper left')
    fig.set_size_inches(15, 5)

    time_5 = time.perf_counter() - start_time_0
    print("\ttime_5: " + str(time_5))

    plt.show()


# ------------------------------------- main ---------------------------------------------
if test_json:

    test_geojson()

    time_all = time.perf_counter() - start_time_0
    print("\ttime_all: " + str(time_all) + "\n")

elif run_geojson:

    lat0a = 53.822975  # Вертники, h = 292
    lng0a = 27.087467
    lat0b = 52.911044  # Слуцк, h = 146
    lng0b = 27.691194

    open_geojson_5m()
    # open_geojson_1m()

    find_points(lat0a, lng0a, lat0b, lng0b)

    create_json(lat0a, lng0a, lat0b, lng0b)

    plot_path()

    time_all = time.perf_counter() - start_time_0
    print("\ttime_all: " + str(time_all) + "\n")
