import sqlite3

dbname = 'TEST.db'
conn = sqlite3.connect(dbname)

# sqliteを操作するカーソルオブジェクトを作成
cur = conn.cursor()

# personsというtableを作成する
# cur.execute('CREATE TABLE persons(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING)')

# "name"に"Taro"を入れる
cur.execute('INSERT INTO persons(name) values("Taro")')
cur.execute('INSERT INTO persons(name) values("Hanako")')
cur.execute('INSERT INTO persons(name) values("Hiroki")')


# データベースへコミット。これで変更を反映される
conn.commit()

cur.close()
conn.close()
