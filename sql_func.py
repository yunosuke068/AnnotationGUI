import sqlite3
import csv

class AnnotationDB:
    def __init__(self,db_path):
        self.connect = conn = sqlite3.connect(db_path)
        # sqliteを操作するカーソルオブジェクトを作成
        self.cursor = cur = self.connect.cursor()

        # create Labels table
        cur.execute("""CREATE TABLE IF NOT EXISTS Labels(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name varcher(32),
        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
        )""")

        # create Movies table
        cur.execute("""CREATE TABLE IF NOT EXISTS Movies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name varcher(32) unique,
        fps numeric(4,2),
        frame int,
        path text,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
        )""")

        # create Subjects table
        cur.execute("""CREATE TABLE IF NOT EXISTS Subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id int,
        order_number int,
        sex varcher(6),
        glasses bit,
        path text,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),

        FOREIGN KEY (movie_id) REFERENCES Movies(id)
        )""")

        # create Annotations table
        cur.execute("""CREATE TABLE IF NOT EXISTS Annotations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id int,
        right_label_id int,
        left_label_id int,
        frame int,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),

        FOREIGN KEY (subject_id) REFERENCES Subjects(id),
        FOREIGN KEY (right_label_id) REFERENCES Labels(id),
        FOREIGN KEY (left_label_id) REFERENCES Labels(id)
        )""")

        # create Logs tables
        cur.execute("""CREATE TABLE IF NOT EXISTS Logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id int,
        frame int,
        flag boolean,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),

        FOREIGN KEY (subject_id) REFERENCES Subjects(id)
        )""")

        # 外部キーを有効化
        cur.execute('PRAGMA foreign_keys=true')

        # updated_atのトリガーを追加
        for table in ['Labels','Movies','Subjects','Annotations']:
            self.CreateUpdatedAtTrigger(table)

        self.InitLabels()

        # データベースへコミット。これで変更を反映される
        conn.commit()

    def Close(self):
        self.cursor.close()
        self.connect.close()

    # すべてのテーブルを削除
    def DeleteTable(self):
        cur = self.cursor
        cur.execute('drop table Logs')
        cur.execute('drop table Annotations')
        cur.execute('drop table Subjects')
        cur.execute('drop table Movies')
        cur.execute('drop table Labels')

    def InitLabels(self):
        filename = "db/csv/labels.csv"
        with open(filename, encoding='utf8', newline='') as f:
            header = next(f)
            csvreader = csv.reader(f)
            for row in csvreader:
                if len(self.cursor.execute(f"select * from Labels where name = '{row[1]}'").fetchall()) == 0:
                    SQL = f"insert into Labels(name) values('{row[1]}')"
                    self.cursor.execute(SQL)

    def CreateUpdatedAtTrigger(self,table):
        self.cursor.execute(f"""CREATE TRIGGER IF NOT EXISTS trigger_{table}_updated_at AFTER UPDATE ON {table}
        BEGIN
            UPDATE {table} SET updated_at = DATETIME('now', 'localtime') WHERE rowid == NEW.rowid;
        END;""")

    def GetTables(self):
        cur = self.cursor
        SQL = "select name from sqlite_master where type='table'"
        tables_list = cur.execute(SQL).fetchall()
        if len(tables_list) > 1:
            tables = [table[0] for table in tables_list if not table[0] in 'sqlite_sequence']
        return tables

    def GetValueByID(self,table,id,column):
        SQL = f"select {column} from {table} where id = {id}"
        return self.cursor.execute(SQL).fetchone()

    def GetRecordsByValue(self,table,column,value):
        SQL = f"select * from {table} where {column} = '{value}'"
        return self.cursor.execute(SQL).fetchall()

    def GetAllValuesByTable(self,table):
        cur = self.cursor
        SQL = f"select * from {table}"
        return cur.execute(SQL).fetchall()

    """Movies"""
    # Movies Table
    # Moviesのレコードの追加
    def InsertMovies(self,name,fps,frame,path):
        cur = self.cursor
        SQL = f"select * from Movies where name = '{name}'"
        if len(cur.execute(SQL).fetchall()) == 0:
            SQL = f"insert into Movies(name,fps,frame,path) values('{name}',{fps},{frame},'{path}') on conflict (name) do nothing"
            cur.execute(SQL)
            self.connect.commit()
        else:
            print(f'Error:Record with the name "{name}" exists in the Movies table.')

    # Movies Table
    # Moviesのレコードの追加または、fps,frameの更新
    def UpdateMovies(self,name,fps,frame,path):
        cur = self.cursor
        id = cur.execute(f"select id from Movies where name = '{name}'").fetchone()
        if id:
            SQLs = [f"update Movies set fps = {fps} where id = {id[0]}",
                    f"update Movies set frame = {frame} where id = {id[0]}",
                    f"update Movies set path = '{path}' where id = {id[0]}"]
            for SQL in SQLs:
                cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertMovies(name,fps,frame,path)

    # Movies Table
    # nameからデータベースにおけるidを取得
    def GetMoviesID(self,name):
        SQL = f"select id from Movies where name = '{name}'"
        id = self.cursor.execute(SQL).fetchone()[0]
        return id

    def GetMoviesValuesForTable(self):
        cur = self.cursor
        SQL = f"select id, name, frame from Movies"
        return cur.execute(SQL).fetchall()

    """Subjects"""
    # Subjects Table
    # Subjectsのレコードの追加
    def InsertSubjects(self,movie_id,order_number,sex,glasses,path):
        cur = self.cursor
        SQL = f"select * from Subjects where movie_id = {movie_id} and order_number = {order_number}"
        if len(cur.execute(SQL).fetchall()) == 0:
            SQL = f"insert into Subjects(movie_id,order_number,sex,glasses,path) values({movie_id},{order_number},'{sex}',{glasses},'{path}')"
            cur.execute(SQL)
            self.connect.commit()
        else:
            print(f'Error:Record with the movie_id "{movie_id}" and order_number "{order_number}" exists in the Movies table.')

    # Subjects Table
    # Subjectsの追加、sex, glasses,pathの更新
    def UpdateSubjects(self,movie_id,order_number,sex,glasses,path):
        cur = self.cursor
        id = cur.execute(f"select id from Subjects where movie_id = '{movie_id}' and order_number =  '{order_number}'").fetchone()
        if id:
            SQLs = [f"update Subjects set sex = '{sex}' where id = {id[0]}",
                    f"update Subjects set glasses = {glasses} where id = {id[0]}",
                    f"update Subjects set path = '{path}' where id = {id[0]}"]
            for SQL in SQLs:
                cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertSubjects(movie_id,order_number,sex,glasses,path)

    # self.GetSubjectValuesForTable()
    # return: list in tuple. tuple in (id, movie_id, order_number)
    # example:  [(1, 1, 1), (2, 1, 2)]
    def GetSubjectsValuesForTable(self):
        cur = self.cursor
        SQL = f"select id, movie_id, order_number from Subjects"
        return cur.execute(SQL).fetchall()

    """Annotations"""
    # Annotations Table
    # Annotationsのレコードの追加
    def InsertAnnotationsAll(self,subject_id,right_label_id,left_label_id,frame):
        SQL = f"insert into Annotations(subject_id,right_label_id,left_label_id,frame) values({subject_id},{right_label_id},{left_label_id},{frame})"
        self.cursor.execute(SQL)
        self.connect.commit()

    def InsertAnnotationsRight(self,subject_id,right_label_id,frame):
        SQL = f"insert into Annotations(subject_id,right_label_id,frame) values({subject_id},{right_label_id},{frame})"
        self.cursor.execute(SQL)
        self.connect.commit()

    def InsertAnnotationsLeft(self,subject_id,left_label_id,frame):
        SQL = f"insert into Annotations(subject_id,left_label_id,frame) values({subject_id},{left_label_id},{frame})"
        self.cursor.execute(SQL)
        self.connect.commit()

    # Annotations Table
    # Annotationsのレコードの追加または、label_idの更新
    def UpdateAnnotationsAll(self,subject_id,right_label_id,left_label_id,frame):
        cur = self.cursor
        id = cur.execute(f"select id from Annotations where subject_id = {subject_id} and frame = {frame}").fetchone()
        if id:
            SQL = f"update Annotations set right_label_id = {right_label_id}, left_label_id = {left_label_id} where id = {id[0]}"
            cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertAnnotationsAll(subject_id,right_label_id,left_label_id,frame)

    def UpdateAnnotationsRight(self,subject_id,right_label_id,frame):
        cur = self.cursor
        id = cur.execute(f"select id from Annotations where subject_id = {subject_id} and frame = {frame}").fetchone()
        if id:
            SQL = f"update Annotations set right_label_id = {right_label_id} where id = {id[0]}"
            cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertAnnotationsRight(subject_id,right_label_id,frame)

    def UpdateAnnotationsLeft(self,subject_id,left_label_id,frame):
        cur = self.cursor
        id = cur.execute(f"select id from Annotations where subject_id = {subject_id} and frame = {frame}").fetchone()
        if id:
            SQL = f"update Annotations set left_label_id = {left_label_id} where id = {id[0]}"
            cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertAnnotationsLeft(subject_id,left_label_id,frame)

    def GetAnnotationsBySubjectID(self,subject_id):
        cur = self.cursor
        SQL = f"select * from Annotations where subject_id = {subject_id} order by frame"
        records = cur.execute(SQL).fetchall()
        if len(records) > 0:
            return records, True
        else:
            return [], False

    def GetAnnotationsRecord(self,subject_id,frame):
        cur = self.cursor
        SQL = f"select right_label_id, left_label_id from Annotations where subject_id = {subject_id} and frame = {frame}"
        labels = cur.execute(SQL).fetchone()
        if labels:
            return labels
        else:
            return ('-','-')

    """Logs"""
    # Logs Table
    # Logsのレコードの追加
    def InsertLogs(self,subject_id,frame):
        SQL = f"insert into Logs(subject_id,frame) values({subject_id},{frame})"
        self.cursor.execute(SQL)
        self.connect.commit()

    # Logs Table
    # Logsのレコードの追加または、label_idの更新
    def UpdateLogs(self,subject_id,frame):
        cur = self.cursor
        id = cur.execute(f"select id from Logs where subject_id = {subject_id}").fetchone()
        if id:
            SQL = f"update Logs set frame = {frame} where subject_id = {subject_id}"
            cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertLogs(subject_id,frame)

    def UpdateLogsFlag(self,subject_id):
        cur = self.cursor

        SQL = f"select id from Logs"
        for i in [r[0] for r in cur.execute(SQL).fetchall()]:
            SQL = f"update Logs set flag = 0 where subject_id = {i}"
            cur.execute(SQL)
        SQL = f"update Logs set flag = 1 where subject_id = {subject_id}"
        cur.execute(SQL)
        self.connect.commit()

    def GetFlagSubjectIDLogs(self):
        cur = self.cursor
        SQL = f"select * from Logs where flag = 1"
        if len(cur.execute(SQL).fetchall()) == 0:
            return 0
        else:
            return cur.execute(SQL).fetchone()[1]
