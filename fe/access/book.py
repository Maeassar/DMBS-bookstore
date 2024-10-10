import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
from pymongo import MongoClient

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "data/book.db")
        self.db_l = os.path.join(parent_path, "data/book_lx.db")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

    def get_book_count(self):
        client = MongoClient("mongodb://localhost:27017/")
        db = client["bookstore"]
        collection = db["book"]
        count = collection.count_documents({})
        return count

    def get_book_info(self, start, size):
        client = MongoClient("mongodb://localhost:27017/")
        db = client["bookstore"]
        collection = db["book"]
        books = collection.find().sort("_id").skip(start).limit(size)

        book_list = []
        for book in books:
            # 创建 Book 对象并设置属性
            book_obj = Book()
            book_obj.id = book["book_info"]["id"]
            book_obj.title = book["book_info"]["title"]
            book_obj.author = book["book_info"]["author"]
            book_obj.publisher = book["book_info"]["publisher"]
            book_obj.original_title = book["book_info"]["original_title"]
            book_obj.translator = book["book_info"]["translator"]
            book_obj.pub_year = book["book_info"]["pub_year"]
            book_obj.pages = book["book_info"]["pages"]
            book_obj.price = book["book_info"]["price"]
            book_obj.binding = book["book_info"]["binding"]
            book_obj.isbn = book["book_info"]["isbn"]
            book_obj.author_intro = book["book_info"]["author_intro"]
            book_obj.book_intro = book["book_info"]["book_intro"]
            book_obj.content = book["book_info"]["content"]
            book_obj.tags = book["book_info"]["tags"]

            # 处理图片
            """
            picture = book["book_info"]["picture"]
            print(picture)
            if picture:
                for i in range(0, random.randint(0, 9)):
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book_obj.pictures.append(encode_str)
            """


            book_list.append(book_obj)

        return book_list
