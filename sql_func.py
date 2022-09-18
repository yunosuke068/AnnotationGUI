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
        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),

        FOREIGN KEY (movie_id) REFERENCES Movies(id)
        )""")

        # create Annotations table
        cur.execute("""CREATE TABLE IF NOT EXISTS Annotations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id int,
        label_id int,
        frame int,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),

        FOREIGN KEY (subject_id) REFERENCES Subjects(id),
        FOREIGN KEY (label_id) REFERENCES Labels(id)
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

    # Movies Table
    # Moviesのレコードの追加
    def InsertMovies(self,name,fps,frame):
        cur = self.cursor
        SQL = f"select * from Movies where name = '{name}'"
        if len(cur.execute(SQL).fetchall()) == 0:
            SQL = f"insert into Movies(name,fps,frame) values('{name}',{fps},{frame}) on conflict (name) do nothing"
            cur.execute(SQL)
            self.connect.commit()
        else:
            print(f'Error:Record with the name "{name}" exists in the Movies table.')

    # Movies Table
    # Moviesのレコードの追加または、fps,frameの更新
    def UpdateMovies(self,name,fps,frame):
        cur = self.cursor
        id = cur.execute(f"select id from Movies where name = '{name}'").fetchone()
        if id:
            SQL = f"update Movies set fps = {fps} where id = {id[0]}"
            cur.execute(SQL)
            SQL = f"update Movies set frame = {frame} where id = {id[0]}"
            cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertMovies(name,fps,frame)

    # Movies Table
    # nameからデータベースにおけるidを取得
    def GetMoviesID(self,name):
        SQL = f"select id from Movies where name = '{name}'"
        id = self.cursor.execute(SQL).fetchone()[0]
        return id

    # Subjects Table
    # Subjectsのレコードの追加
    def InsertSubjects(self,movie_id,order_number,sex,glasses):
        cur = self.cursor
        SQL = f"select * from Subjects where movie_id = {movie_id} and order_number = {order_number}"
        if len(cur.execute(SQL).fetchall()) == 0:
            SQL = f"insert into Subjects(movie_id,order_number,sex,glasses) values({movie_id},{order_number},'{sex}',{glasses})"
            cur.execute(SQL)
            self.connect.commit()
        else:
            print(f'Error:Record with the movie_id "{movie_id}" and order_number "{order_number}" exists in the Movies table.')

    # Annotations Table
    # Annotationsのレコードの追加
    def InsertAnnotations(self,subject_id,label_id,frame):
        SQL = f"insert into Annotations(subject_id,label_id,frame) values({subject_id},{label_id},{frame})"
        self.cursor.execute(SQL)
        self.connect.commit()

    # Annotations Table
    # Annotationsのレコードの追加または、label_idの更新
    def UpdateAnnotations(self,subject_id,label_id,frame):
        cur = self.cursor
        id = cur.execute(f"select id from Annotations where subject_id = {subject_id} and frame = {frame}").fetchone()
        if id:
            SQL = f"update Annotations set label_id = {label_id} where id = {id[0]}"
            cur.execute(SQL)
            self.connect.commit()
        else:
            self.InsertAnnotations(subject_id,label_id,frame)

    # def GetOrderNumber(self):
        # order_numberの計算
        # SQL = f"select max(order_number) from (select * from Subjects where movie_id = '{movie_id}')"
        # order_max_tuple = cur.execute(SQL).fetchone()
        # if len(order_max_tuple) == 0:
        #     order_number = 1
        # else:
        #     order_number = order_max_tuple[0]+1
