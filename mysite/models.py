import Levenshtein
import psycopg2


def get_user_list():
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    cur.execute("select * from users")  # 这里最后换成实际数据库books
    user_list = cur.fetchall()
    user_list = [{"username": user[1], "userid": user[0], "type": user[5]} for user in user_list]
    return user_list


def get_profile(userid):
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    cur.execute("select * from users where userid=\'" + userid + "\'")  # 这里最后换成实际数据库books
    profile = cur.fetchall()
    profile = {"username": profile[0][1], "userid": profile[0][0], "type": profile[0][5]}
    return profile


def get_borrow_list(userid):
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()

    cur.execute(
        "select * from (borrowlist join document on document.documentid=borrowlist.documentid) join book on book.documentid=document.documentid where userid=\'" + userid + "\'")  # 这里最后换成实际数据库books

    borrow_list = cur.fetchall()
    borrow_list = [{"id": book[0], "name": book[5], "author": book[15], "type": book[16], "year": book[6]} for book in
                   borrow_list]
    return borrow_list


def admin_statu(request):
    admin = request.get_signed_cookie("admin", salt="SSS", default=None)  # 0表示用户，1表示管理员
    return admin


def get_ranked_paper(list_all, title_query):
    distances = list(map(lambda x: Levenshtein.distance(x[9], title_query), list_all))
    _, list_all = zip(*sorted(zip(distances, list_all), reverse=False))
    len_half = int(len(list_all) / 2)
    return list_all[:len_half]


def get_ranked_book(list_all, title_query):
    distances = list(map(lambda x: Levenshtein.distance(x[8], title_query), list_all))
    _, list_all = zip(*sorted(zip(distances, list_all), reverse=False))
    len_half = int(len(list_all) / 2)
    return list_all[:len_half]


def get_book_num():
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM book")
    book_count = cur.fetchall()
    return book_count[0][0]


def delete_oldest_book():
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    cur.execute(
        "select * from book join borrowstatu on book.documentid=borrowstatu.documentid order by addtime limit 20")
    delete_book_info = cur.fetchall()
    print(delete_book_info)
    delete_id=delete_book_info[0][1]
    borrowtimes=delete_book_info[0][9]
    for item in delete_book_info:
        if item[9]<borrowtimes:
            delete_id=item[1]
            borrowtimes=item[9]
    cur.execute("select * from book join document on book.documentid=document.documentid where book.documentid=\'" + str(delete_id) + "\'")
    delete_book_info = cur.fetchall()
    cur.execute("delete from book where documentid=\'" + str(delete_id) + "\'")
    cur.execute("delete from document where documentid=\'" + str(delete_id) + "\'")
    conn.commit()
    delete_book = {"id": delete_book_info[0][1], "title": delete_book_info[0][9]}
    return delete_book
