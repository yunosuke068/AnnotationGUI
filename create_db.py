import sqlite3
import sql_func
import csv

dbname = 'db/ANNOTATION.db'

sql = sql_func.AnnotationDB(dbname)

# テストデータのインサート
sql.InsertMovies('test',30,1000)
sql.InsertMovies('test1',20,100)
sql.InsertMovies('test2',10,10000)
sql.InsertMovies('test3',40,10)
sql.InsertMovies('test4',50,10)
sql.InsertMovies('test5',40,10)
sql.InsertMovies('test6',70,10)

sql.InsertSubjects(sql.GetMoviesID('test'),1,'male',True)
sql.InsertSubjects(sql.GetMoviesID('test'),2,'female',False)
sql.InsertSubjects(sql.GetMoviesID('test3'),1,'male',True)
sql.InsertSubjects(sql.GetMoviesID('test3'),2,'male',False)
sql.InsertSubjects(sql.GetMoviesID('test3'),3,'male',True)

SQL="select id from Annotations where subject_id = 1 and frame = 5"
if sql.cursor.execute(SQL).fetchone():
    print(sql.cursor.execute(SQL).fetchone())

SQL="select id from Annotations where subject_id = 1 and frame = 3"
if sql.cursor.execute(SQL).fetchone():
    print(sql.cursor.execute(SQL).fetchone())
# filename = "db/csv/labels.csv"
# with open(filename, encoding='utf8', newline='') as f:
#     header = next(f)
#     csvreader = csv.reader(f)
#     for row in csvreader:
#         print(row)

sql.Close()
