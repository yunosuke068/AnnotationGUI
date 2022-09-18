# import sqlite3
#
# dbname = 'db/ANNOTATION.db'
# conn = sqlite3.connect(dbname)
#
# # sqliteを操作するカーソルオブジェクトを作成
# cur = conn.cursor()
#
# cur.execute('drop table Annotations')
# cur.execute('drop table Movies')
# cur.execute('drop table Subjects')
# cur.execute('drop table Labels')
#
# cur.close()
# conn.close()

import sqlite3
import sql_func

dbname = 'db/ANNOTATION.db'

sql = sql_func.AnnotationDB(dbname)

sql.DeleteTable()

sql.Close()
