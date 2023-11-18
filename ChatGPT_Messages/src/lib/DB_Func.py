import pandas as pd
import sqlite3
from sqlite3 import Error
import pymysql
from sqlalchemy import exc, create_engine, text as sql_text


##############################################################################
def Execute_Query(conn, query=None):
    """
    """
    cur = conn.cursor()
    cur.execute(query)
    #cur.execute("SELECT * FROM employee limit 5")

    rows = cur.fetchall()

    for row in rows:
        print(row)
##############################################################################
def Run_Query(Conn=None, Credentials=None, DB=None, DBFile = None, Query=None, Verbose=False):
    """
    """
    # initialize empty dataframe
    df = pd.DataFrame()
    status = 0

    if Conn:
        try:
            return(pd.DataFrame(pd.read_sql(Query, Conn)))
        except Error as e:
            print(e)  
            return -20  
    else:
        if DB == 'sqlite':
            try:
                Conn = sqlite3.connect(DBFile)
            except Error as e:
                print(e)
                return -20
            try:
                return(pd.DataFrame(pd.read_sql(Query, Conn)))
            except Error as e:
                print('read_sql_query error - sqlite')
                return -1
                
        elif DB == 'mysql':
            #Unpack DB Credentials 
            MYSQL_User = Credentials['User']
            MYSQL_PWD = Credentials['PWD']
            try:
                Conn = create_engine(f'mysql+pymysql://{MYSQL_User}:{MYSQL_PWD}@localhost/fakebank')
            except exc.SQLAlchemyError:
                print('failed to connect to mysql DB')
                return -1
            try:
                df = pd.read_sql_query(con=Conn.connect(),sql=sql_text(Query))
                return status, df
            except exc.SQLAlchemyError:
                if Verbose:
                    print('read_sql_query error - MySQL')
                    print(f'Query Error sql_text {sql_text(Query)}' )
                    print(f'returned message {df}')
                status = -5
                return df, status
        else:
            print('DB is unsupported')
            status = -10
            return status, df
