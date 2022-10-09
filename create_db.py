import sqlite3
import sql_func
import movie_func
import csv
import glob
import os

dbname = 'db/ANNOTATION.db'
sql = sql_func.AnnotationDB(dbname)

for path in glob.glob('db/source/*.mp4'):
    movie = movie_func.Movie(path)
    source_name = os.path.basename(movie.path).replace('.mp4','')
    sql.UpdateMovies(source_name,movie.fps,movie.frame_count,movie.path)

for path in glob.glob('db/Subjects/*.mp4'):
    movie = movie_func.Movie(path)
    filename = os.path.basename(movie.path).replace('.mp4','')
    [source_name, order_number] = filename.split('_')
    sql.UpdateSubjects(sql.GetMoviesID(source_name),order_number,'',False,movie.path)



# source = movie_func.Movie()
# テストデータのインサート
# sql.UpdateMovies('627OBH2cUgM',30,1000)


# filename = "db/csv/labels.csv"
# with open(filename, encoding='utf8', newline='') as f:
#     header = next(f)
#     csvreader = csv.reader(f)
#     for row in csvreader:
#         print(row)

sql.Close()
