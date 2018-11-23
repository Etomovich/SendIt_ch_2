import psycopg2
from psycopg2 import connect
from instance.config import Config, TestConfiguration

def connection():
    try:
        print("Establishing connection to Postgres DB....")
        con = psycopg2.connect(Config.MAIN_URL)
        return con
    except (Exception, psycopg2.Error) as error :
        print ("Connection to Postgres Failed!! ", error)

def tests_connection():
    try:
        print("Establishing connection to Postgres DB....")
        con = psycopg2.connect(TestConfiguration.TEST_URL)
        return con
    except (Exception, psycopg2.Error) as error :
        print ("Connection to Postgres Failed!! ", error)

def create_test_relations():
    con = tests_connection()
    cur = con.cursor()
    queries = sendit_relations()
    for query in queries:
        cur.execute(query)
    con.commit()
    con.close()
    return True

def create_relations():
    con = connection()
    cur = con.cursor()
    queries = sendit_relations()
    for query in queries:
        cur.execute(query)
    con.commit()
    con.close()
    return True

def remove_all_tables():
    con = connection()
    cur = con.cursor()
    tab1 = """DROP TABLE IF EXIST sendit_users CASCADE;"""
    tab2 = """DROP TABLE IF EXIST sendit_orders CASCADE;"""
    tab3 = """DROP TABLE IF EXIST sendit_parcels CASCADE;"""
    cur.execute(tab1)
    cur.execute(tab2)
    cur.execute(tab3)
    con.commit()
    con.close()
    return True

def sendit_relations():
    '''Creates all the tables in the database.'''
    tab1="""
        CREATE TABLE IF NOT EXISTS sendit_users(
            user_id         SERIAL PRIMARY KEY,
            username        VARCHAR(50)  UNIQUE NOT NULL,
            email           VARCHAR(50)  UNIQUE NOT NULL,
            phone_number    VARCHAR(20)  UNIQUE NOT NULL,
            role            VARCHAR(10)  NOT NULL,
            password        VARCHAR(100)  NOT NULL);
    """
    tab2="""
        CREATE TABLE IF NOT EXISTS sendit_parcels(
            parcel_id           SERIAL PRIMARY KEY,
            parcel_name         VARCHAR(50)  NOT NULL,
            submission_station  VARCHAR(50)  NOT NULL,
            present_location    VARCHAR(50)  NOT NULL,
            weight              NUMERIC(20, 2) NOT NULL DEFAULT 0.0,
            expected_pay        NUMERIC(20, 2) NULL DEFAULT 0.0,
            order_id            INTEGER NULL,
            feedback            VARCHAR(300)  NULL,
            destination         VARCHAR(50)  NULL,
            submission_date     TIMESTAMP WITH TIME ZONE NOT NULL,
            status              VARCHAR(20)  DEFAULT 'not-started',
            approved            VARCHAR(20)  DEFAULT 'No',
            owner_id            INTEGER NULL
        );
    """

    tab3="""
        CREATE TABLE IF NOT EXISTS sendit_orders(
            order_id            SERIAL PRIMARY KEY,
            parcel_name         VARCHAR(50)  NULL,
            parcel_description  VARCHAR(300) NULL,
            pay_mode            VARCHAR(100) NULL,
            pay_proof           VARCHAR(50)  NULL,
            amount_paid         NUMERIC(20, 2) NULL DEFAULT 0.0,
            destination         VARCHAR(50)  NULL,
            submitted           VARCHAR(50)  DEFAULT 'False',
            order_status        VARCHAR(50)  DEFAULT 'unprocessed',
            feedback            VARCHAR(300)  NULL,
            owner_id            INTEGER REFERENCES sendit_users(user_id) ON DELETE CASCADE,
            parcel_id           INTEGER REFERENCES sendit_parcels(parcel_id) ON DELETE CASCADE
            );
    """
    
    return [tab1,tab2,tab3]