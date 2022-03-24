import psycopg2
import csv
db_user = "postgres"
db_password = "hello"
db_host = 'localhost'
db_port = "5432"
db_database = "test"
conn = None


def get_query(query):
    con = psycopg2.connect(user=db_user, password=db_password,
                           host=db_host, port=db_port,
                           database=db_database)
    rlist = []
    try:
        if (con):
            curr = con.cursor()
            curr.execute(query)
            rows = curr.fetchall()
            colnames = [desc[0] for desc in curr.description]
    except(Exception, psycopg2.DatabaseError) as error:
        print(query, error)
    finally:
        if (con):
            curr.close()
            con.close()

    column_counts = len(colnames)
    for i in rows:
        data = {}
        for g in range(column_counts):
            data[colnames[g]] = i[g]
        rlist.append(data)
    return rlist


def create_con():
    global conn
    conn = psycopg2.connect(user=db_user, password=db_password,
                            host=db_host, port=db_port,
                            database=db_database)
    conn.autocommit = True


def close_conn():
    global conn
    if (conn):
        conn.close()


def set_query(query, data_list):
    global conn
    curr = conn.cursor()
    curr.execute(query, data_list)


def set_query2(query):
    global conn
    curr = conn.cursor()
    curr.execute(query)


def load_csv():
    with open('test_addresses.csv') as csvfile:
        csv_reader = csv.reader(csvfile)
        rows = list(csv_reader)
    rows2 = []
    for i in rows:
        if i[7] == 'true':
            rows2.append(i)
    create_con()
    for i in rows2:
        rowid = i[0]
        country_code = str(i[1])
        address1 = str(i[2])
        address2 = str(i[3])
        postcode = str(i[4])
        geom = "ST_SetSRID(ST_MakePoint({},{}),4326)".format(i[5], i[6])
        number_value = str(i[8])
        address3 = str(i[9])
        address4 = str(i[10])
        query = "insert into public.ukdata (rowid, country_code, address1, "
        query += " address2, postcode, geom,  number_value, address3,"
        query += " address4)"
        " values (%s,%s,%s,%s,%s, {},%s,%s,%s)".format(geom)
        data_list = [
                    rowid, country_code, address1,
                    address2, postcode, number_value,
                    address3, address4
                    ]
        set_query(query=query, data_list=data_list)
    close_conn()


def check_db():
    query = "SELECT count(*) FROM pg_database where datname='test';"
    ls = get_query(query=query)
    if ls[0]["count"] == 0:
        query = "CREATE DATABASE test WITH OWNER = postgres ENCODING = 'UTF8'"
        query += " LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8' "
        query += " TABLESPACE = pg_default CONNECTION LIMIT = -1;"
        query += " CREATE EXTENSION postgis; "
        set_query2(query)
    query = "SELECT count(*) FROM pg_catalog.pg_tables WHERE "
    query += "schemaname != 'pg_catalog' AND schemaname "
    query += " != 'information_schema' and tablename='ukdata';"
    ls = get_query(query=query)
    if ls[0]["count"] == 0:
        query = """CREATE TABLE IF NOT EXISTS public.ukdata
            (
            rowid integer NOT NULL,
            country_code character varying(3) COLLATE pg_catalog."default",
            address1 character varying(255) COLLATE pg_catalog."default",
            address2 character varying(255) COLLATE pg_catalog."default",
            postcode character varying(20) COLLATE pg_catalog."default",
            bool_value boolean,
            address3 character varying(255) COLLATE pg_catalog."default",
            address4 character varying(255) COLLATE pg_catalog."default",
            number_value character varying(10) COLLATE pg_catalog."default",
            geom geometry(Point,4326),
            CONSTRAINT ukdata_pkey PRIMARY KEY (rowid)
            )
            WITH (
                OIDS = FALSE
            )
            TABLESPACE pg_default;

            ALTER TABLE IF EXISTS public.ukdata
                OWNER to postgres;
                CREATE INDEX IF NOT EXISTS ukdatageomindx
                ON public.ukdata USING gist
                (geom)
                TABLESPACE pg_default;
                        """
        set_query2(query)
    query = "SELECT count(*) FROM public.ukdata;"
    ls = get_query(query=query)
    if ls[0]["count"] == 0:
        load_csv()


def point2longlat(point):
    point = str(point)
    point = point.replace("POINT(", "")
    point = point.replace(")", "")
    points = point.split(" ")
    lat = points[1]
    lon = points[0]
    return lat, lon


def get_data(sw, en, zoom):
    envelope = str(sw)+","+str(en)
    query = """SELECT row_number() over () AS id,
    ST_NumGeometries(gc) as countpoint,
    ST_AsText (ST_Transform (ST_Centroid(gc), 4326)) as loca
    FROM (select unnest(ST_ClusterWithin(gc2,""" + str(zoom) + """)) gc
    from (SELECT geom as gc2
    FROM public.ukdata where geom
    && ST_MakeEnvelope(""" + envelope + """,4326) ) as a
                ) as f;"""
    df = get_query(query=query)
    rslt = []
    for i in df:
        stg = {}
        lat, lon = point2longlat(i["loca"])
        stg["latitude"] = lat
        stg["longitude"] = lon
        stg["count"] = i["countpoint"]

        rslt.append(stg)

    return rslt
