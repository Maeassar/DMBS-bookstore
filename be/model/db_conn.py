from be.model import store
from sqlalchemy import text


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        """
        cursor = self.conn.execute(
            "SELECT user_id FROM user WHERE user_id = ?;", (user_id,)
        )
        """
        query = text("SELECT user_id FROM users WHERE user_id = :user_id")
        params = {"user_id":user_id}
        result = self.conn.execute(query, params)
        row = result.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        """
        cursor.execute(
            "SELECT book_id FROM store WHERE store_id = %s AND book_id = %s",
            (store_id, book_id),
        )
        """
        query = text("SELECT book_id FROM store WHERE store_id = :store_id AND book_id = :book_id")
        params = {"store_id":store_id, "book_id":book_id}
        result = self.conn.execute(query, params)
        row = result.fetchone()

        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        query = text("SELECT store_id FROM user_store WHERE store_id = :store_id")
        params = {"store_id":store_id}
        result = self.conn.execute(query, params)
        row = result.fetchone()
        """
        cursor = self.conn.execute(
            "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
        )
        """
        if row is None:
            return False
        else:
            return True
