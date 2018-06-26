import database as db
import db_info

db.set_up_connection(db.db, db_info.db_name, user=db_info.db_user, password=db_info.db_password)
#TODO add docstring and exceptions
def insert_df(table_name, df):
    db.insert_into_table(df, table_name, auto_id=True)

