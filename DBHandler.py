import json
import sqlite3

import shapely

from KBModel import HVDataModel
from shapely.geometry import Point


def create_connection():
    # create a connection
    conn = sqlite3.connect('hv.db')
    conn.enable_load_extension(True)
    # depending on your OS and sqlite/spatialite version you might need to add
    # '.so' (Linux) or '.dll' (Windows) to the extension name
    conn.execute('SELECT load_extension("mod_spatialite")')
    conn.execute('SELECT InitSpatialMetaData(1);')

    # cursor
    c = conn.cursor()

    # initial table creation
    c.execute("""CREATE TABLE IF NOT EXISTS HVReport (
                report TEXT,
                identifiers TEXT,
                dates TEXT,
                types TEXT,
                significance TEXT,
                summary TEXT,
                additional TEXT
        )""")
    c.execute('SELECT AddGeometryColumn("HVReport","geom" , 4326, "POINT", 2)')
    conn.commit()
    c.close()
    return conn


def insert_into_db(kbmodel, conn):
    query = kbmodel.toDBQuery()
    print(query)
    # cursor
    c = conn.cursor()
    # insert a KBModel into the database
    c.execute(query)
    conn.commit()
    c.close()


def fetch_from_db(query, conn):
    # cursor
    c = conn.cursor()
    # load from DB
    c.execute(query)
    tuples = c.fetchall()
    print(tuples)  # I should create kbmodels here
    c.close()
    return tuples


def get_all_raw_models():
    conn = create_connection()
    results = fetch_from_db("select *, ST_AsText(geom) from HVReport", conn)
    conn.close()
    return results


def get_all_models():
    conn = create_connection()
    models = []
    results = fetch_from_db("select *, ST_AsText(geom) from HVReport", conn)
    for res in results:
        report, identifiers, dates, types, significance, summary, additional, location_binary, location_wkt = res
        models.append(
            HVDataModel(
                identifiers=json.loads(identifiers),
                report=report,
                dates=json.loads(dates),
                types=json.loads(types),
                significance=significance,
                summary=summary,
                additional=json.loads(additional),
                location=shapely.from_wkt(location_wkt)
            )
        )
        conn.close()
        return models


if __name__ == "__main__":
    conn = create_connection()

    kbm1 = HVDataModel(identifiers={"HV_ID": 1, "R_ID": 100},
                       location=Point(-31.8, 144.9),
                       dates={"excavation": "2020-01-01",
                              "report": "2021-01-01"},
                       types=['building'],
                       significance="Locally significant",
                       summary="This is just a dummy summary of mock data 1",
                       additional={},
                       report="mock1.pdf")
    insert_into_db(kbm1, conn)
    kbm2 = HVDataModel(identifiers={"HV_ID": 2, "R_ID": 101},
                       location=Point(-31.7, 144.95),
                       dates={"excavation": "2021-01-01",
                              "report": "2021-05-01"},
                       types=['site'],
                       significance="State-level significant",
                       summary="This is just a dummy summary of mock data 2",
                       additional={"condition": "UNK"},
                       report="mock12.pdf")
    insert_into_db(kbm2, conn)
    models = []
    results = fetch_from_db("select *, ST_AsText(geom) from HVReport", conn)
    for res in results:
        report, identifiers, dates, types, significance, summary, additional, location_binary, location_wkt = res
        print(type(json.loads(identifiers)))
        print(type(json.loads(dates)))
        print(type(json.loads(types)))
        models.append(
            HVDataModel(
                identifiers=json.loads(identifiers),
                report=report,
                dates=json.loads(dates),
                types=json.loads(types),
                significance=significance,
                summary=summary,
                additional=json.loads(additional),
                location=shapely.from_wkt(location_wkt)
            )
        )
    for model in models:
        print(model.toHTML())
