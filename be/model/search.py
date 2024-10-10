"""
新增搜索功能，实现分项搜索，结合使用mongodb和sql数据库
"""
from be.model import error
from be.model import db_conn
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from pymongo import MongoClient

client_mongodb = MongoClient('mongodb://127.0.0.1:27017/')
db_mongodb = client_mongodb['bookstore']
mongodb = db_mongodb['book']

class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_only_store(self,
                          choose: int,
                          store_id: str,
                          keyword: str,
                          page: int,
                          limit: int):
        try:
            if not self.store_id_exist(store_id):
                print("hihi can u get, can u learn that u can't get store_id")
                return error.error_non_exist_store_id(store_id) + ("",)
            choose = int(choose)

            page = int(page)
            limit = int(limit)

            skip = (page - 1) * limit


            if choose == 0:  # book_intro
                id_in_mongo_list = []
                book_real_in_store = []


                print("print result")
                result = mongodb.find({"$text": {"$search": keyword}}, {"book_info.id":True})  # 全文索引,这时候先不用管store_id
                for r in result:
                    id_in_mongo_list.append(r["book_info"]["id"])

                print(id_in_mongo_list)

                count = mongodb.count_documents({"$text": {"$search": keyword}})
                if count == 0:
                    return error.error_non_this_book() + ("",)

                book_list = []

                for i in range(len(id_in_mongo_list)):
                    result_in_sql = text("SELECT book_id, price, title, author FROM store WHERE store_id = :store_id AND book_id = :book_id LIMIT 5 OFFSET 0")
                    params = {"store_id": store_id, "book_id": id_in_mongo_list[i], "limit": limit, "offset": skip}
                    result = self.conn.execute(result_in_sql, params)
                    row = result.fetchone()
                    print(id_in_mongo_list[i])
                    if not row is None:
                        book_list.append(id_in_mongo_list[i])
                        """
                        print(id_in_mongo_list[i])
                        price = row[1]
                        title = row[2]
                        author = row[3]
                        print(row[0], price, title, author)
                        print("开始构造")

                        temp = {
                            "book_id": book_real_in_store[i],
                            "price": price,
                            "title": title,
                            "author": author
                            }
                        """

                print("book_list")
                print(book_list)

            elif choose == 1:
                print("根据作者名字查询")
                book_list = []
                result_author = text("SELECT book_id, price, title, author FROM store WHERE store_id = :store_id AND author = :keyword LIMIT 5 OFFSET 0")
                params = {"store_id": store_id, "keyword": keyword, "limit": limit, "offset": skip}
                result = self.conn.execute(result_author, params)
                row = result.fetchall()
                for r in row:
                    book_id = r[0]
                    price = r[1]
                    title = r[2]
                    author = r[3]
                    print(row[0], price, title, author)
                    print("开始构造")

                    temp = {
                        "book_id":  book_id,
                        "price": price,
                        "title": title,
                        "author": author
                    }
                    book_list.append(temp)

            elif choose == 2:
                print("根据作品名字查询")
                book_list = []
                result_author = text("SELECT book_id, price, title, author FROM store WHERE store_id = :store_id AND title = :keyword LIMIT 5 OFFSET 0")
                params = {"store_id": store_id, "keyword": keyword, "limit": limit, "offset": skip}
                result = self.conn.execute(result_author, params)
                row = result.fetchall()
                for r in row:
                    book_id = r[0]
                    price = r[1]
                    title = r[2]
                    author = r[3]
                    print(row[0], price, title, author)
                    print("开始构造")

                    temp = {
                        "book_id":  book_id,
                        "price": price,
                        "title": title,
                        "author": author
                    }
                    book_list.append(temp)

            if len(book_list) == 0:
                print("no such book in store")
                return error.error_not_book_in_this_store(store_id) + ("",)


            print(book_list)

        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "OK", book_list

    def search_all(self,
                  choose: int,
                  keyword: str,
                  page: int,
                  limit: int):
        try:
            page = int(page)
            limit = int(limit)

            skip = (page - 1) * limit

            choose = int(choose)
            if choose == 0:  # book_intro
                book_list = []
                id_in_mongo_list = []
                book_real_in_store = []

                print("print result")
                result = mongodb.find({"$text": {"$search": keyword}}, {"book_info.id":True})  # 全文索引,这时候先不用管store_id
                for r in result:
                    id_in_mongo_list.append(r["book_info"]["id"])

                print(id_in_mongo_list)

                count = mongodb.count_documents({"$text": {"$search": keyword}})
                if count == 0:
                    return error.error_non_this_book() + ("",)

                for i in range(len(id_in_mongo_list)):
                    result_in_sql = text("SELECT book_id, title, author FROM store WHERE book_id = :book_id LIMIT 5 OFFSET 0")
                    params = {"book_id": id_in_mongo_list[i], "limit": limit, "offset": page}
                    result = self.conn.execute(result_in_sql, params)
                    row = result.fetchone()

                    if not row is None:
                        book_list.append(id_in_mongo_list[i])

                print(book_list)


            elif choose == 1:
                print("根据作者名字查询")
                book_list = []
                result_author = text("SELECT book_id, price, title, author FROM store WHERE author = :keyword LIMIT 5 OFFSET 0")
                params = {"keyword": keyword, "limit": limit, "offset": skip}
                result = self.conn.execute(result_author, params)
                row = result.fetchall()
                for r in row:
                    book_id = r[0]
                    price = r[1]
                    title = r[2]
                    author = r[3]
                    print(row[0], price, title, author)
                    print("开始构造")

                    temp = {
                        "book_id":  book_id,
                        "price": price,
                        "title": title,
                        "author": author
                    }
                    book_list.append(temp)

            elif choose == 2:
                print("根据作品名字查询")
                book_list = []
                result_author = text("SELECT book_id, price, title, author FROM store WHERE title = :keyword LIMIT 5 OFFSET 0")
                params = {"keyword": keyword, "limit": limit, "offset": skip}
                result = self.conn.execute(result_author, params)
                row = result.fetchall()
                for r in row:
                    book_id = r[0]
                    price = r[1]
                    title = r[2]
                    author = r[3]
                    print(row[0], price, title, author)
                    print("开始构造")

                    temp = {
                        "book_id":  book_id,
                        "price": price,
                        "title": title,
                        "author": author
                    }
                    book_list.append(temp)

            if len(book_list) == 0:
                print("no such book all store")
                return error.error_not_book_which_u_want + ("",)

            print(book_list)

        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "OK", book_list

    def get_detail_info(self, book_id):
        try:
            book = mongodb.find_one({'book_info.id': book_id}, {'_id': 0})
            print("book_finded", book)
            book_info = book["book_info"]
            book_data = {
                "id": book_info["id"],
                "title": book_info["title"],
                "author": book_info["author"],
                "tags": "\n".join(book_info["tags"]),
                "publisher": book_info["publisher"],
                "original_title": book_info["original_title"],
                "pub_year": book_info["pub_year"],
                "pages": book_info["pages"],
                "binding": book_info["binding"],
                "author_intro": book_info["author_intro"],
                "content": book_info["content"]
            }
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", book_data

