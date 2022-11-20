import sqlite3
import csv


class DB:
    def __init__(self,db_path):
        self.connect = conn = sqlite3.connect(db_path,detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = cur = self.connect.cursor()

    def CreateUpdatedAtTrigger(self,table):
        self.cursor.execute(f"""CREATE TRIGGER IF NOT EXISTS trigger_{table}_updated_at AFTER UPDATE ON {table}
        BEGIN
            UPDATE {table} SET updated_at = DATETIME('now', 'localtime') WHERE rowid == NEW.rowid;
        END;""")

    def SQLToColumn(self,table_name):
        return [row[1] for row in self.cursor.execute(f"PRAGMA table_info('{table_name}')").fetchall()]

    """ALL"""
    def GetRecords(self,table='',col=['*'],terms={},option={'sql_str':''}):
        if '*' in col:
            col = self.col_dic[table]
        terms_SQL = self.GenerateWhereAndTerms(terms) if len(terms.keys()) > 0 else ""
        col_str = self.GenerateColumnStr(col)
        SQL = f"SELECT {col_str} FROM {table} {terms_SQL} {option['sql_str']}"
        records = self.cursor.execute(SQL).fetchall()
        return self.GenerateRecordsInDict(col,records)

    def InsertRecords(self,table,values):
        col = "".join([f"{k}," for k in values.keys()])[:-1]
        val = "".join(["?," for v in values.values()])[:-1]
        insert_data = [v for v in values.values()]
        SQL = f"INSERT INTO {table}({col}) VALUES({val})"
        # print(SQL)
        self.cursor.execute(SQL,insert_data)
        self.connect.commit()
    
    def BulkInsertRecords(self,table,values_list):
        values = values_list[0]
        col = "".join([f"{k}," for k in values.keys()])[:-1]
        val = "".join(["?," for v in values.values()])[:-1]
        insert_data = []
        for values in values_list:
            insert_data.append([v for v in values.values()])
        SQL = f"INSERT INTO {table}({col}) VALUES({val})"
        # print(SQL)
        self.cursor.executemany(SQL,insert_data)
        self.connect.commit()

    def UpdateRecords(self,table,terms,values):
        cur = self.cursor
        terms_SQL = self.GenerateWhereAndTerms(terms) if len(terms.keys()) > 0 else ""
        id = cur.execute(f"SELECT id FROM {table} {terms_SQL}").fetchone()
        if id:
            # for k in values.keys():
            #     if isinstance(values[k], str):
            #         s = values[k]#.replace("'",'').replace('"','')
            #         values[k] = f"'{s}'"
            #     if values[k] is None:
            #         values[k] = 'NULL'
            set_str = ''.join([f' {k} = ?,' for k in values.keys()])[:-1]
            SQL = f"UPDATE {table} SET{set_str} WHERE id = {id[0]}"
            insert_data = [v for v in values.values()]
            # print(SQL)
            cur.execute(SQL,insert_data)
            self.connect.commit()
        else:
            self.InsertRecords(table,values)

    def DeleteRecords(self,table,terms):
        cur = self.cursor
        terms_SQL = self.GenerateWhereAndTerms(terms) if len(terms.keys()) > 0 else ""
        SQL = f"DELETE FROM {table} {terms_SQL}"
        self.cursor.execute(SQL)
        # self.connect.commit()

    def Commit(self):
        self.connect.commit()

    """Other"""
    # face_idが一致するFaceSubjectsを取得
    def GetSubjectIdentify(self,face_id):
        face_subject_records = self.GetFaceSubjects(['id','face_id','subject_id'],{'face_id':face_id})
        print(face_subject_records)
        if len(face_subject_records) > 0:
            subject_id = face_subject_records[0]['subject_id']
            subject_records = self.GetSubjects({'id':subject_id})
            if len(subject_records) > 0:
                subject_record = subject_records[0]
                movie_records = self.GetMovies(['name'],{'id':subject_record['movie_id']})
                #print('movie_records',movie_records)
                movie_name = movie_records[0]['name']

                return f"{movie_name}_{subject_record['order_number']}"
            else:
                return 0

    def GenerateRecordsInDict(self,col,records):
        output_records = []
        for record in records:
            record_dic = {}
            for i in range(len(col)):
                record_dic[col[i]] = record[i]
            output_records.append(record_dic)
        return output_records

    def GenerateWhereAndTerms(self,terms):
        if not isinstance(terms, dict):
            print('terms is not dict.')
            return 0
        terms_SQL = ""
        flag = True
        for k in terms.keys():
            if isinstance(terms[k], str):
                s = terms[k]#.replace("'",'').replace('"','')
                terms[k] = f"'{s}'"
            if flag:
                terms_SQL += f"WHERE {k} = {terms[k]} "
                flag = False
            else:
                terms_SQL += f"AND {k} = {terms[k]} "
        return terms_SQL

    def GenerateColumnStr(self,col):
        col_str = col[0]
        for c in col[1:]:
            col_str += f",{c}"
        return col_str

class AnnotationDB(DB):
    def __init__(self,db_path):
        self.connect = conn = sqlite3.connect(db_path)
        # sqliteを操作するカーソルオブジェクトを作成
        self.cursor = cur = self.connect.cursor()

        # create Labels table
        cur.execute("""CREATE TABLE IF NOT EXISTS Labels(
                        id INTEGER,
                        name varcher(32),
                        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
                        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
                        )""")

        # create Movies table
        cur.execute("""CREATE TABLE IF NOT EXISTS Movies(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name varcher(32) unique,
                        fps NUMERIC(4,2),
                        frame int,
                        path text,
                        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
                        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
                        )""")

        # create Subjects table
        cur.execute("""CREATE TABLE IF NOT EXISTS Subjects(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name varcher(32) unique,
                        movie_id int,
                        order_number int,
                        sex varcher(6),
                        glasses bit,
                        fps NUMERIC(4,2),
                        frame int,
                        path text,
                        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
                        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
                        )""")

        # create Annotations table
        cur.execute("""CREATE TABLE IF NOT EXISTS Annotations(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subject_id int,
                        right_label_id int,
                        left_label_id int,
                        frame int,
                        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
                        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
                        )""")

        # create Logs tables
        cur.execute("""CREATE TABLE IF NOT EXISTS Logs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subject_id int,
                        frame int,
                        flag boolean,
                        created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
                        updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
                        )""")

        # 外部キーを有効化
        cur.execute('PRAGMA foreign_keys=true')
        
        table_names =  cur.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()
        table_names = [r[0] for r in table_names if r[0] != 'sqlite_sequence'] if len(table_names) > 0 else []
        print(table_names)

        self.col_dic = {}
        for table in table_names:
            # updated_atのトリガーを追加
            self.CreateUpdatedAtTrigger(table)
            # カラム名をリスト化
            self.col_dic[table] = self.SQLToColumn(table)
        print(self.col_dic)
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
            ids = []
            for row in csvreader:
                # if len(self.cursor.execute(f"select * from Labels where name = '{row[1]}'").fetchall()) == 0:
                #     SQL = f"insert into Labels(name) values('{row[1]}')"
                #     self.cursor.execute(SQL)
                id = int(row[0])
                self.UpdateRecords('Labels',{'id':id},{'id':row[0],'name':row[1]})
                ids.append(id)
            lr_ids = [lr['id'] for lr in self.GetRecords('Labels',['id'])]
            if len(lr_ids) > len(ids):
                for lr_id in lr_ids:
                    if not lr_id in ids:
                        self.DeleteRecords('Labels',{'id':lr_id})

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

    