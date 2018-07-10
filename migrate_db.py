import pandas as pd
import db_manager
import os
import sys

path = sys.argv[1]
table_name = sys.argv[2]

def insert(path, table_name):
    for file_name in os.listdir(path):
        df = pd.read_pickle(path + file_name)
        db_manager.insert_df(table_name, df)

insert(path, table_name)
