from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from be.model import error
from be.model import db_conn
import json


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        print("check add_book", book_id, book_json_str)
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            #book_json_str = json.loads(book_json_str)
            #book_find = self.mongodb['book'].find_one({'id':book_id})
            book_info_json = json.loads(book_json_str)
            print("book_info_json", book_info_json)
            price = book_info_json.get("price")
            print("price", price)
            book_info_json.pop("price")
            author = book_info_json.get("author")
            print("author", author)
            title = book_info_json.get("title")
            add_book = text("INSERT into store(store_id, book_id, author, title, price, stock_level) VALUES (:store_id, :book_id, :author, :title, :price, :stock_level)")
            params = {"store_id": store_id, "book_id": book_id, "author":author, "title": title, "price": price, "stock_level": stock_level}
            self.conn.execute(add_book, params)
            self.conn.commit()
            """
            self.conn.execute(
                "INSERT into store(store_id, book_id, book_info, stock_level)"
                "VALUES (?, ?, ?, ?)",
                (store_id, book_id, book_json_str, stock_level),
            )
            """
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            add_st = text("UPDATE store SET stock_level = stock_level + :add_stock_level WHERE store_id = :store_id AND book_id = :book_id")
            params = {"add_stock_level": add_stock_level, "store_id": store_id, "book_id": book_id}
            self.conn.execute(add_st, params)
            """
            self.conn.execute(
                "UPDATE store SET stock_level = stock_level + ? "
                "WHERE store_id = ? AND book_id = ?",
                (add_stock_level, store_id, book_id),
            )
            """
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        print("into creat_store")
        try:
            if not self.user_id_exist(user_id):
                print("user exist")
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                print("store_exist")
                return error.error_exist_store_id(store_id)
            """
            self.conn.execute(
                "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
                (store_id, user_id),
            )
            """
            creatst = text("INSERT into user_store(store_id, user_id) VALUES (:store_id, :user_id)")
            params = {"store_id": store_id, "user_id": user_id}
            self.conn.execute(creatst, params)
            self.conn.commit()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def deliver(self, store_id : str, order_id : str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            print("hi come deliver")

            check_order = text("SELECT status FROM new_order_detail WHERE order_id = :order_id")
            params = {"order_id": order_id}
            result = self.conn.execute(check_order, params)
            print("can check", result)
            row = result.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            status = row[0]
            if status != 1:
                return error.error_invalid_order_status(order_id)

            update_op = text("UPDATE new_order_detail SET status = :new_status WHERE order_id = :order_id")
            params = {"order_id": order_id, "new_status": "2"}
            self.conn.execute(update_op, params)

            self.conn.commit()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

