from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import search
import json

bp_search = Blueprint("search", __name__, url_prefix="/search")

@bp_search.route("/index", methods=["POST"])
def hello_search():
    return 'Hello Search!'

@bp_search.route("/search_only_store", methods=["POST"])
def search_only_store():
    choose: int = request.json.get("choose")
    store_id: str = request.json.get("store_id")
    keyword: str = request.json.get("keyword")
    page: int = request.json.get("page")
    limit: int = request.json.get("limit")
    s = search.Search()
    print("Can u get result perfectly?")
    code, message, result = s.search_only_store(choose, store_id, keyword, page, limit)
    print("u did it")
    return jsonify({"message": message,  "result": result}), code

@bp_search.route("/search_all", methods=["POST"])
def search_all():
    choose: int = request.json.get("choose")
    keyword: str = request.json.get("keyword")
    page: int = request.json.get("page")
    limit: int = request.json.get("limit")
    s = search.Search()
    code, message, result = s.search_all(choose, keyword, page, limit)
    return jsonify({"message": message,  "result": result}), code

@bp_search.route("/get_detail_info", methods=["POST"])
def get_detail_info():
    book_id :str = request.json.get("book_id")
    s = search.Search()
    code, message, result = s.get_detail_info(book_id)
    return jsonify({"message": message,  "result": result}), code