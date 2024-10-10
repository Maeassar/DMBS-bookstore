import jwt
import time
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text
from be.model import error
from be.model import db_conn

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    #return encoded.decode("utf-8")
    return encoded


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            insert_user = text("INSERT INTO users (user_id, password, balance, token, terminal) VALUES (:uid, :pw, 0, :tok, :ter)")
            params = {"uid": user_id, "pw": password, "tok": token, "ter": terminal}
            self.conn.execute(insert_user, params)
            self.conn.commit()

        except IntegrityError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        pick_token = text("SELECT token from users where user_id= :uid")
        params = {"uid": user_id}
        result = self.conn.execute(pick_token, params)
        row = result.fetchone()
        print("finded", row)
        if row is None:
            return error.error_authorization_fail()
        db_token = row[0]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        #cursor = self.conn.execute(
            #"SELECT password from user where user_id=?", (user_id,)
        #)
        pick_pwd = text("SELECT password from users where user_id= :uid")
        params = {"uid": user_id}
        cursor= self.conn.execute(pick_pwd, params)

        row = cursor.fetchone()
        print("passwd_check")
        if row is None:
            return error.error_authorization_fail()
        if password != row[0]:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            print(token)
            update_query = text("UPDATE users SET token = :tok, terminal = :ter WHERE user_id = :uid")
            params = {"tok": token, "ter": terminal, "uid": user_id}
            cursor = self.conn.execute(update_query, params)
            self.conn.commit()

            if cursor.rowcount == 0:
                return error.error_authorization_fail() + ("",)
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        print("begin logout")
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message
            print("pass check_token")
            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            print("dummy", dummy_token)
            update_query = text("UPDATE users SET token = :tok, terminal = :ter WHERE user_id = :uid")
            params = {"tok": dummy_token, "ter": terminal, "uid": user_id}
            cursor = self.conn.execute(update_query, params)

            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            delete_query = text("DELETE FROM users WHERE user_id = :uid")
            params = {"uid": user_id}
            cursor = self.conn.execute(delete_query, params)
            self.conn.commit()

            if cursor.rowcount == 1:
                self.conn.commit()
            else:
                return error.error_authorization_fail()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            update_query = text("UPDATE users SET password = :pw, token = :tok, terminal = :ter WHERE user_id = :uid")
            params = {"pw": new_password, "tok": token, "ter": terminal, "uid": user_id}
            cursor = self.conn.execute(update_query, params)
            self.conn.commit()
            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
