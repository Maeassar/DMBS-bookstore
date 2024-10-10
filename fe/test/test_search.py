import pytest
from fe.access.search import Search
from fe import conf
from fe.access.new_seller import register_new_seller
import uuid
from fe.access import book

class TestSearchBooks:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
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
        self.search = Search(conf.URL)
        self.page = 1
        self.limit = 5
        self.test_book_id = self.book_id_exist[0]

        yield

    def test_search_only_for_all(self):
        code, message, result = self.search.search_only_store("0", self.store_id, "撒哈拉的故事", self.page, self.limit)
        assert code == 200
    def test_search_only_for_title(self):
        code, message, result = self.search.search_only_store("2", self.store_id, "撒哈拉的故事", self.page, self.limit)
        assert code == 200
    def test_search_only_for_author(self):
        code, message, result = self.search.search_only_store("1", self.store_id, "三毛", self.page, self.limit)
        assert code == 200

    def test_search_all(self):
        code, message, result = self.search.search_all("0", "撒哈拉的故事", self.page, self.limit)
        assert code == 200

    def test_search_all_title(self):
        code, message, result = self.search.search_all("2", "撒哈拉的故事", self.page, self.limit)
        assert code == 200

    def test_search_all_author(self):
        code, message, result = self.search.search_all("1", "三毛", self.page, self.limit)
        assert code == 200

    def test_no_book_store(self):
        code, message, result = self.search.search_only_store("0", self.store_id, "倾城之恋", self.page, self.limit)
        assert code != 200
    def test_no_book_all(self):
        code, message, result = self.search.search_all("0", "xx撒哈拉-x唔x", self.page,self.limit)
        assert code != 200
    def test_no_store(self):
        self.store_id = self.store_id + "_x"
        code, message, result = self.search.search_only_store("0", self.store_id, "撒哈拉的故事", self.page, self.limit)
        assert code != 200

    def test_get_detail_info(self):
        buy_book_info_list = []
        buy_book_id_list = []
        buy_num = 1
        book_id_list = []
        buy_book_info_list.append((self.book_id_exist[0], buy_num))
        for item in buy_book_info_list:
            buy_book_id_list.append((item[0].id, item[1]))
            book_id_list.append(item[0].id)
        code, message, result = self.search.get_detail_info(book_id_list[0])
        assert code == 200

    def test_get_detail_info_fail(self):
        code, message, result = self.search.get_detail_info("123456")
        assert code != 200