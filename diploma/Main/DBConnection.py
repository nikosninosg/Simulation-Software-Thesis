import mysql.connector
import pandas as pd

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='nikosninos7',
    database='diplomadb')

c = db.cursor(buffered=True)

c.execute("select database();")
record = c.fetchone()
print("You're connected to database: ", record)

# sql_drop = "DROP TABLE IF EXISTS `output_data`;"
# res_d = c.execute(sql_drop)
'''

c.execute("""create table output_data
(
    env_now        int          not null,
    machine        char(20)     null,
    description    varchar(30)  null,
    current_cans   int          null,
    init_level     int          null,
    capacity       int          null,
    status         char(20)     null,
    brakeTF        tinyint(1)   null,
    brake_duration float(20, 0) null,
    cause          char(20)     null
);
""")
'''


def insert_csv_to_db():
    c.execute("""DELETE FROM output_data;""")

    # (env_now, machine, description, current_cans, init_level, capacity, status, brakeTF, brake_duration, cause)
    sql = """INSERT INTO diplomadb.output_data VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ?);"""
    row = (13, 'Depall', 'Processing', 39912, 100, 10000, 'GREEN', True, 13, 'Blocked door')
    c.execute(sql, tuple(row))
    print("Record inserted")

    # the connection is not auto committed by default, so we must commit to save our changes
    db.commit()

    data = pd.read_csv(r'output/output.csv')
    df = pd.DataFrame(data=data)
    print(data)
    print(df.iloc[0])

    for i, rows in df.iterrows():
        sql1 = """INSERT INTO diplomadb.output_data 
        (env_now, machine, description, current_cans, init_level, capacity, status, brakeTF, brake_duration, cause)
         VALUES (%d, %s, %s, %d, %d, %d, ?, ?, %d, ?);"""

        c.execute(sql1, tuple(rows))

        db.commit()


print("1 record inserted, ID:", c.lastrowid)
# db.close()


insert_csv_to_db()
