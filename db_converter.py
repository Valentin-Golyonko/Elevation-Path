import sqlite3
import time

import geojson

print("Please wait! Running...")
start_time_0 = time.perf_counter()  # time.perf_counter, time.process_time


def open_geojson():
    print("opening .geojson")
    global data
    with open('data/xxx.geojson', encoding="utf8") as f:
        data = geojson.load(f)

    time_1 = time.perf_counter() - start_time_0
    print("\ttime_1: " + str(time_1))


def test_geojson():
    print("test_geojson()")
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
    print("\tlen_arr = " + str(len_arr) + "; count = " + str(count))


def convert_geojson_to_db():
    print("convert_geojson_to_db()")
    count = 0
    len_arr = 0
    db_row = 1
    purchases = []

    time_30 = time.perf_counter()

    i_db = sqlite3.connect('data/test.db')
    i_cursor = i_db.cursor()

    time_32 = time.perf_counter()
    for feature_t in data['features']:
        arr_t = feature_t['geometry']['coordinates']

        if len(arr_t) > 1:
            len_arr += 1

        for i in arr_t[0]:
            count += 1
            lng = i[0]
            lat = i[1]
            elev = feature_t['properties']['ELEV']

            purchase = (lat, lng, elev, count)
            purchases.append(purchase)

    # print(str(count) + ": " + str(lng) + " " + str(lat) + " " + str(elev))
    print("\tlen_arr = " + str(len_arr) + "; count = " + str(count))
    print("\ttime_3.3: " + str(time.perf_counter() - time_32))

    time_34 = time.perf_counter()
    try:
        i_cursor.executemany("INSERT INTO elevation (lat, lng, elev, id) VALUES (?, ?, ?, ?)", purchases)
        i_db.commit()

        if count == db_row * 100:
            print("db_row = " + str(count))
            db_row += 1
    except sqlite3.DatabaseError as err:
        print("\tError: ", err)
    else:
        i_db.commit()

    print("\ttime_3.5: " + str(time.perf_counter() - time_34))

    max_id = i_cursor.execute("SELECT MAX(id) FROM elevation").fetchone()
    print("\tMAX(id): " + str(max_id[0]))
    i_db.close()

    print("\ttime_3.1: " + str(time.perf_counter() - time_30))


def open_db():
    print("open_db()")
    time_60 = time.perf_counter()

    db = sqlite3.connect('data/xxx.db')
    cursor = db.cursor()

    try:
        max_id = cursor.execute("SELECT MAX(id) FROM elevation").fetchone()
        print("\tMAX(id): " + str(max_id[0]))

        for row in cursor.execute("SELECT * FROM elevation"):
            print("\t" + str(row)
                  + "; lat = " + str(-row[0])
                  + ", lng = " + str(-row[1])
                  + ", elev = " + str(-row[2])
                  + ", id = " + str(row[3]))

    except sqlite3.DatabaseError as err:
        print("\tError: ", err)
    else:
        db.commit()

    db.close()

    print("\ttime_6.1: " + str(time.perf_counter() - time_60))


# ------------------------------------- main ---------------------------------------------
open_geojson()

test_geojson()

convert_geojson_to_db()

# open_db()
