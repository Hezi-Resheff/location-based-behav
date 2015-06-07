import pandas as pd 
import numpy as np
import sqlalchemy 

import settings as st

def from_gps(date_start, date_end, animals=None, limit=False):
   
    engine = sqlalchemy.create_engine(st.CONN_STR) # connect to server

    sql = "SELECT * from lab_data.storks_gps WHERE date_start_fix >= '{0}' AND date_start_fix <= '{1}' ".format(date_start, date_end)
    if animals:
        sql += "AND bird_id in ({0}) ".format(",".join([str(a) for a in animals]))
    else:
        sql += "AND bird_id is not null "
    if limit:
        sql += "LIMIT {0}".format(limit)
    
    data = pd.read_sql_query(sql, engine, "idx", True, None, parse_dates=["date_start_fix", "date_end_fix"])

    return data 


if __name__ == "__main__":
    print(from_gps("20120101", "20120101"))
    