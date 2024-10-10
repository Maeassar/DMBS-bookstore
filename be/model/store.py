import logging
import os
from sqlalchemy import create_engine,text
import pymongo
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


class Store:
    database: str

    def __init__(self, db_path):
        self.engine = create_engine('postgresql://postgres:504020@127.0.0.1:5432/bookstore') #连接本地数据库
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            mongodb = self.get_db_mongo()
            print("user")
            sql = text(
                "CREATE TABLE IF NOT EXISTS users ("
                "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            )
            self.conn.execute(sql)
            print("us")
            sql = text(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id TEXT, store_id TEXT, "
                "PRIMARY KEY(user_id, store_id));"
            )
            print("store")
            #store有冗余信息，方便查询（支持id, 作者， 名字的简单查询）
            self.conn.execute(sql)
            sql = text(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id TEXT, book_id TEXT, author TEXT, title TEXT, price TEXT, stock_level INTEGER,"
                " PRIMARY KEY(store_id, book_id));"
            )
            self.conn.execute(sql)
            print("no")
            sql = text(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            )
            self.conn.execute(sql)
            print("nod")
            #添加status， 0表示已下单未付款，1表示已下单已付款， 2表示已发货， 3表示已收货，4表示已取消，（取消和收货都从sql里删掉，存到mongodb中
            # ）

            sql = text(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  status INTEGER, order_time INTEGER, "
                "PRIMARY KEY(order_id, book_id))"
            )
            self.conn.execute(sql)

            self.conn.commit()

        except SQLAlchemyError as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self):
        print("try starting")
        self.DBSession = sessionmaker(bind=self.engine)
        self.conn = self.DBSession()
        print("conn haven!!")
        return self.conn

    def get_db_mongo(self):
        self.mongodb = self.client["bookstore"]
        # mongodb目前需手动建立文档集
        return self.mongodb


database_instance: Store = None

def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()

def get_db_mongo():
    global database_instance
    return database_instance.get_db_mongo()