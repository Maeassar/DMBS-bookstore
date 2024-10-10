import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
from fe.access.new_seller import register_new_seller
from fe.access import book
from fe import conf

import uuid

class TestOrder:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.seller = register_new_seller(self.seller_id, self.password)

        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 5)
        self.book_id_exist = []
        for bk in self.books:
            code = self.seller.add_book(self.store_id, 0, bk)
            assert code == 200
        for b in self.books:
            book_id = b.id
            code = self.seller.add_stock_level(self.seller_id, self.store_id, book_id, 100)
            assert code == 200
            self.book_id_exist.append(b)

        yield


    def test_deliver_ok(self):
        #ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        #assert ok
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(1000000)
        code = self.buyer.payment(order_id)
        code = self.seller.deliver(self.store_id, order_id)
        assert code == 200

    def test_non_exist_this_store(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.seller.deliver(self.store_id + "_x", order_id)
        assert code != 200

    def test_invalid_order(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.seller.deliver(self.store_id, order_id + "_x")
        assert code != 200


    def test_invalid_order_status(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.seller.deliver(self.store_id, order_id + "_x")
        assert code != 200


    def test_receive_ok(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(1000000)
        code = self.buyer.payment(order_id)
        code = self.seller.deliver(self.store_id, order_id)
        code = self.buyer.receive(order_id)
        assert code == 200

    def test_receive_non_order(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(1000000)
        code = self.buyer.payment(order_id)
        code = self.seller.deliver(self.store_id, order_id)
        code = self.buyer.receive(order_id + "_x")
        assert code != 200

    def test_receive_wuser_id(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(1000000)
        code = self.buyer.payment(order_id)
        code = self.seller.deliver(self.store_id, order_id)
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.receive(order_id)
        assert code != 200

    def test_receive_wstatus(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.receive(order_id)
        assert code != 200

    def test_cancel_ok(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel_order(order_id)
        assert code == 200

    def test_cancel_wuser_id(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.cancel_order(order_id)
        assert code != 200

    def test_cancel_worder_id(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel_order(order_id + "_x")
        assert code != 200

    def test_cancel_worder_status(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(1000000)
        code = self.buyer.payment(order_id)
        code = self.buyer.cancel_order(order_id)
        assert code != 200

    def test_cancel_repeat(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel_order(order_id)
        code = self.buyer.cancel_order(order_id)
        assert code != 200

    def test_find_history_cancel_ok(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.cancel_order(order_id)
        code = self.buyer.history_order()
        assert code == 200

    def test_find_history_receive_ok(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        code = self.buyer.add_funds(1000000)
        code = self.buyer.payment(order_id)
        code = self.seller.deliver(self.store_id, order_id)
        code = self.buyer.receive(order_id)
        code = self.buyer.history_order()
        assert code == 200

    def test_find_history_wuser_id(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))

        code0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.history_order()
        assert code != 200

    def test_find_non_history_order(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))
        code = self.buyer.history_order()
        assert code != 200