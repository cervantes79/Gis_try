import psycopg2
import csv
db_user = "postgres"
db_password = "hello"
db_host = 'localhost'
db_port = "5432"
db_database = "test"
db_connection = None


def get_query(query):
    """ get sql query as list of dictionaries """

    connection = psycopg2.connect(user=db_user,
                                  password=db_password,
                                  host=db_host, port=db_port,
                                  database=db_database)
    resultlist = []
    try:
        if (connection):
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
    except(psycopg2.DatabaseError) as error:
        print(query, error)
    finally:
        if (connection):
            cursor.close()
            connection.close()

    column_counts = len(colnames)
    for i in rows:
        data = {}
        for g in range(column_counts):
            data[colnames[g]] = i[g]
        resultlist.append(data)
    return resultlist


def create_db_connection():
    """ Create connection to database """
    global db_connection
    db_connection = psycopg2.connect(user=db_user, password=db_password,
                                     host=db_host, port=db_port,
                                     database=db_database)
    db_connection.autocommit = True


def close_db_connection():
    """ Close database connection """
    global db_connection
    if (db_connection):
        db_connection.close()


def set_query(query, data_list):
    """ run sql commands in database
        query: T-sql query
        data_list: list of parameters
        """
    global db_connection
    cursor = db_connection.cursor()
    cursor.execute(query, data_list)


def set_query2(query):
    """ run sql commands in database
        query: T-sql query
        Parameters already inserted to query string

    """
    global db_connection
    cursor = db_connection.cursor()
    cursor.execute(query)


def load_csv():
    """ Loads and inserts csv to the database
    also it filters non point rows """
    with open('test_addresses.csv') as csvfile:
        csv_reader = csv.reader(csvfile)
        csv_rows = list(csv_reader)
    filterted_rows = []
    for i in csv_rows:
        if i[7] == 'true':
            filterted_rows.append(i)
    create_db_connection()
    for i in filterted_rows:
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
    close_db_connection()


def check_db():
    """ This checks database. If any setting is missing it creates. """

    query = "SELECT count(*) FROM pg_database where datname='test';"
    data = get_query(query=query)
    if data[0]["count"] == 0:
        query = "CREATE DATABASE test WITH OWNER = postgres ENCODING = 'UTF8'"
        query += " LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8' "
        query += " TABLESPACE = pg_default CONNECTION LIMIT = -1;"
        query += " CREATE EXTENSION postgis; "
        set_query2(query)
    query = "SELECT count(*) FROM pg_catalog.pg_tables WHERE "
    query += "schemaname != 'pg_catalog' AND schemaname "
    query += " != 'information_schema' and tablename='ukdata';"
    data = get_query(query=query)
    if data[0]["count"] == 0:
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
    data = get_query(query=query)
    if data[0]["count"] == 0:
        load_csv()


def point2longlat(point):
    """ this split latitude and longtitude values from string value """
    point = str(point)
    point = point.replace("POINT(", "")
    point = point.replace(")", "")
    points = point.split(" ")
    lat = points[1]
    lon = points[0]
    return lat, lon


def get_data(sw, en, zoom):
    """ It takes 3 parameters:
        sw: south west point of bounding box,
            Example sw=-11.962067381231293,51.81965717678804
        en:  north east point of bounding box,
            Example ne=5.31906738123115,56.60417303370079
        zoom: Zoom level
        it returns list of dictionaries with keys below:
        [{'latitude':'','longitude':'','count':''}]
        """
    envelope = str(sw) + "," + str(en)
    query = """SELECT row_number() over () AS id,
    ST_NumGeometries(gc) as countpoint,
    ST_AsText (ST_Transform (ST_Centroid(gc), 4326)) as loca
    FROM (select unnest(ST_ClusterWithin(gc2,""" + str(zoom) + """)) gc
    from (SELECT geom as gc2
    FROM public.ukdata where geom
    && ST_MakeEnvelope(""" + envelope + """,4326) ) as a
                ) as f;"""
    data = get_query(query=query)
    result_list = []
    for i in data:
        stagingdict = {}
        lat, lon = point2longlat(i["loca"])
        stagingdict["latitude"] = lat
        stagingdict["longitude"] = lon
        stagingdict["count"] = i["countpoint"]

        result_list.append(stagingdict)

    return result_list
