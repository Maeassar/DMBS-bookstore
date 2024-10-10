from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from pymongo import MongoClient
import datetime
import time

time_limit = 30#订单存活时间


# 连接到MongoDB
client_mongodb = MongoClient('mongodb://127.0.0.1:27017/')
db_mongodb = client_mongodb['bookstore']
hismongodb = db_mongodb['history_order']

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            print("begin creat orders")
            for book_id, count in id_and_count:
                """
                cursor = self.conn.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = ? AND book_id = ?;",
                    (store_id, book_id),
                )
                """
                count = int(count)
                query_book = text("SELECT book_id, stock_level, price FROM store WHERE store_id = :store_id AND book_id = :book_id")
                params = {"store_id":store_id, "book_id":book_id}
                result = self.conn.execute(query_book, params)
                row = result.fetchone()

                print("get result")
                if row is None:
                    print("no book")
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                print("check_new_order:what in book", row[0], row[1], row[2], count)

                book_id = row[0]
                stock_level = row[1]
                price = row[2]

                stock_level = int(stock_level)
                if stock_level < count:
                    print("low stock")
                    return error.error_stock_level_low(book_id) + (order_id,)
                """
                cursor = self.conn.execute(
                    "UPDATE store set stock_level = stock_level - ? "
                    "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                    (count, store_id, book_id, count),
                )
                """
                update = text("UPDATE store SET stock_level = stock_level - :count WHERE store_id = :store_id AND book_id = :book_id AND stock_level >= :count")
                print("update stock")
                params = {"count":count, "store_id":store_id, "book_id":book_id}
                cursor = self.conn.execute(update, params)
                print("update stock final")
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)
                """
                self.conn.execute(
                    "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                    "VALUES(?, ?, ?, ?);",
                    (uid, book_id, count, price),
                )
                """
                status_create_order = 0 #表示已下单未支付
                order_time = time.time()
                print(order_time)

                insert_od = text("INSERT INTO new_order_detail(order_id, book_id, count, price, status, order_time) VALUES(:order_id, :book_id, :count, :price, :status_create_order, :order_time)")
                print("new_order_detail")
                params = {"order_id":uid, "book_id":book_id, "count":count, "price":price, "status_create_order":status_create_order, "order_time":order_time}
                self.conn.execute(insert_od, params)
            """
            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id) "
                "VALUES(?, ?, ?);",
                (uid, store_id, user_id),
            )
            """
            insert_o = text("INSERT INTO new_order(order_id, store_id, user_id) VALUES(:order_id, :store_id, :user_id)")
            params = {"order_id":uid, "store_id":store_id, "user_id":user_id}
            self.conn.execute(insert_o, params)

            self.conn.commit()
            order_id = uid
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            """
            cursor = conn.execute(
                "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
                (order_id,),
            )
            """
            query_o = text("SELECT order_id, user_id, store_id FROM new_order WHERE order_id = :order_id")
            params = {"order_id":order_id}
            result = conn.execute(query_o, params)
            row = result.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)


            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            """
            cursor = conn.execute(
                "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            )
            """
            query_ba = text("SELECT balance, password FROM users WHERE user_id = :buyer_id")
            params = {"buyer_id":buyer_id}
            cursor = conn.execute(query_ba, params)
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            """
            cursor = conn.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
                (store_id,),
            )
            """
            query_st = text("SELECT store_id, user_id FROM user_store WHERE store_id = :store_id")
            params = {"store_id":store_id}
            cursor = conn.execute(query_st, params)
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            """
            cursor = conn.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
                (order_id,),
            )
            """
            query_de = text("SELECT book_id, count, price, status, order_time FROM new_order_detail WHERE order_id = :order_id")
            params = {"order_id":order_id}
            cursor = conn.execute(query_de, params)

            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count
                status = row[3]
                order_time = row[4]
                print(order_time)

            cur_time = time.time()
            print(cur_time)
            time_diff = cur_time - order_time
            print(time_diff)
            if time_diff > time_limit:
                update_op = text("UPDATE new_order_detail SET status = :new_status WHERE order_id = :order_id")
                params = {"order_id": order_id, "new_status": "4"}
                cursor = conn.execute(update_op, params)
                conn.commit()

                order = {
                    "order_id": order_id,
                    "user_id": buyer_id,
                    "store_id": store_id,
                    "status": "已取消",
                    "count": count,
                    "price": price
                }  # 构造历史订单

                hismongodb.insert_one(order)  # 插入历史订单
                print(order)
                status = 4



            print("total_price", total_price)
            print("balance", balance)
            print("status", status)

            balance = int(balance)
            total_price = int(total_price)

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            """
            cursor = conn.execute(
                "UPDATE user set balance = balance - ?"
                "WHERE user_id = ? AND balance >= ?",
                (total_price, buyer_id, total_price),
            )
            """
            update_ba = text("UPDATE users SET balance = balance - :total_price "
             "WHERE user_id = :buyer_id AND balance >= :total_price")
            params = {"total_price":total_price, "buyer_id":buyer_id}
            cursor = conn.execute(update_ba, params)
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            """
            cursor = conn.execute(
                "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
                (total_price, buyer_id),
            )
            """
            update_ba = text("UPDATE users SET balance = balance + :total_price WHERE user_id = :buyer_id")
            params = {"total_price":total_price, "buyer_id":buyer_id}
            cursor = conn.execute(update_ba, params)
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            """
            cursor = conn.execute(
                "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            )
            """

            #下面的有可能影响test，先保留着

            """
            delete_no = text("DELETE FROM new_order WHERE order_id = :order_id")
            params = {"order_id":order_id}
            cursor = conn.execute(delete_no, params)

            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)
            """

            """
            cursor = conn.execute(
                "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            )
            
            delete_nod = text("DELETE FROM new_order_detail WHERE order_id = :order_id")
            params = {"order_id":order_id}
            cursor = conn.execute(delete_nod, params)
            """
            if status != 0:
                return error.error_invalid_order_id(order_id)

            # 已支付
            update_op = text("UPDATE new_order_detail SET status = :new_status WHERE order_id = :order_id")
            params = {"order_id": order_id, "new_status": "1"}
            cursor = self.conn.execute(update_op, params)
            print("改完了")
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            conn.commit()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive(self, user_id, order_id) -> (int, str):#手动收货
        try:
            print("starting receive")
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            check_order = text("SELECT order_id, status, count, price FROM new_order_detail WHERE order_id = :order_id")
            params = {"order_id": order_id}
            result = self.conn.execute(check_order, params)
            print("can check", result)
            row = result.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            order_id = row[0]
            print(order_id)
            status = row[1]
            print(status)
            count = row[2]
            print(count)
            price = row[3]
            print(price)


            check_user = text("SELECT user_id, store_id FROM new_order WHERE order_id = :order_id")
            params = {"order_id": order_id}
            result = self.conn.execute(check_user, params)
            print("can check", result)

            row_u = result.fetchone()
            buyer_id = row_u[0]
            store_id = row_u[1]
            print(store_id)

            order = {
                "order_id": order_id,
                "user_id": buyer_id,
                "store_id": store_id,
                "status": "已收到",
                "count": count,
                "price": price
            }#构造历史订单

            if buyer_id != user_id:
                return error.error_authorization_fail()

            if status != 2:#要已发货才可以确认收获
                return error.error_invalid_order_status(order_id)

            #已收到
            print("已收到")
            update_op = text("UPDATE new_order_detail SET status = :new_status WHERE order_id = :order_id")
            params = {"order_id": order_id, "new_status": "3"}
            self.conn.execute(update_op, params)

            self.conn.commit()


            hismongodb.insert_one(order)#插入历史订单


        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def cancel_order(self, user_id, order_id) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            check_order = text("SELECT status, count, price, order_id FROM new_order_detail WHERE order_id = :order_id")
            params = {"order_id": order_id}
            result = self.conn.execute(check_order, params)
            print("can check", result)
            row = result.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            status = row[0]
            if status != 0:
                return error.error_invalid_order_status(order_id)
            count = row[1]
            price = row[2]
            order_id = row[3]

            check_user = text("SELECT user_id, store_id FROM new_order WHERE order_id = :order_id")
            params = {"order_id": order_id}
            result = self.conn.execute(check_user, params)
            print("can check", result)

            row_u = result.fetchone()
            buyer_id = row_u[0]
            store_id = row_u[1]

            delete_no = text("DELETE FROM new_order WHERE order_id = :order_id")
            params = {"order_id": order_id}
            cursor = self.conn.execute(delete_no, params)

            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)


            delete_nod = text("DELETE FROM new_order_detail WHERE order_id = :order_id")
            params = {"order_id": order_id}
            cursor = self.conn.execute(delete_nod, params)

            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            self.conn.commit()

            order = {
                "order_id": order_id,
                "user_id": buyer_id,
                "store_id": store_id,
                "status": "已取消",
                "count": count,
                "price": price
            }  # 构造历史订单

            hismongodb.insert_one(order)  # 插入历史订单


        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            print("add fund now")
            """
            cursor = self.conn.execute(
                "SELECT password  from user where user_id=?", (user_id,)
            )
            """
            check = text("SELECT password FROM users WHERE user_id = :user_id")
            params = {"user_id":user_id}
            result = self.conn.execute(check, params)
            print("can check", result)
            row = result.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()
            """
            cursor = self.conn.execute(
                "UPDATE user SET balance = balance + ? WHERE user_id = ?",
                (add_value, user_id),
            )
            """
            addf = text("UPDATE users SET balance = balance + :add_value WHERE user_id = :user_id")
            params = {"add_value":add_value, "user_id":user_id}
            cursor = self.conn.execute(addf, params)
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def history_order(self, user_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ("",)

            history = hismongodb.find({"user_id": user_id})
            history_order_list = []
            for each in history:
                order_Id = each["order_id"]
                order = hismongodb.find_one({"order_id": order_Id})
                # print(order["order_id"])
                order_data = {
                    "order_id": order["order_id"],
                    "store_id": order["store_id"],
                    "count": order["count"],
                    "price": order["price"],
                    "status": order["status"]
                }
                history_order_list.append(order_data)

            if len(history_order_list) == 0:
                return error.error_non_history_order() + ("",)

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok", history_order_list
