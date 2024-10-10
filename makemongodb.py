import sqlite3
from pymongo import MongoClient

# 连接到SQLite数据库
conn_sqlite = sqlite3.connect('../../Database_pro1/bookstore/fe/data/book_lx.db')
cursor_sqlite = conn_sqlite.cursor()

# 连接到MongoDB
client_mongodb = MongoClient('mongodb://127.0.0.1:27017/')
db_mongodb = client_mongodb['bookstore']
collection_mongodb = db_mongodb['book']

# 查询SQLite数据库中的表格内容
cursor_sqlite.execute("SELECT * FROM book")
rows = cursor_sqlite.fetchall()

# 将数据转换为MongoDB文档格式，并插入到MongoDB集合中
for row in rows:
    book_data = {
        "book_info": {
            "tags": row[15].split(",") if row[15] else [],
            "pictures": [str(row[16])] if row[16] else [],
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "publisher": row[3],
            "original_title": row[4],
            "translator": row[5],
            "pub_year": row[6],
            "pages": row[7],
            "price": row[8],
            "binding": row[10],
            "isbn": row[11],
            "author_intro": row[12],
            "book_intro": row[13],
            "content": row[14]
        },
        "stock_level": 0
    }

    collection_mongodb["store"].create_index(
        [("book_info.book_intro", "text"), ("book_info.content", "text"), ("book_info.tags", "text"),
         ("book_info.title", "text")])
    collection_mongodb.insert_one(book_data)



# 关闭连接
conn_sqlite.close()
client_mongodb.close()
