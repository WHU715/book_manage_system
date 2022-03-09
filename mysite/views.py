import datetime
import json

import psycopg2
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, HttpResponse, redirect, reverse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout  # 查数据库验证， 登录， 退出登录
from django.contrib.auth.decorators import login_required  # 路由保护装饰器
# from mysite.models import user  # 用户表
from mysite.forms import Form  # 表单验证类（自定义的）
from mysite.models import get_user_list, get_profile, get_borrow_list, admin_statu, get_ranked_book, \
    get_ranked_paper, get_book_num, delete_oldest_book


def hello(request):
    request.encoding = 'utf-8'
    message = {}
    next_url = request.get_full_path()
    login_statu = False
    if request.POST:
        message = request.POST['q']

    if request.get_signed_cookie("login", salt="SSS", default=None) == 'yes':
        login_statu = True
    return render(request, "hello.html", {"test_message": message, 'login_statu': login_statu, 'next_url': next_url})


def show_papers(request):

    next_url = request.get_full_path()

    # conn = psycopg2.connect(database="postgres", user="dbuser", password="123@li", host="localhost", port="5432")
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")

    cur = conn.cursor()

    cur.execute("select * from paper join document on paper.documentid=document.documentid")  # 这里最后换成实际数据库papers
    # cur.execute("select * from book")  # 这里最后换成实际数据库papers
    papers_list_raw = cur.fetchall()

    print(papers_list_raw[0])
    request.encoding = 'utf-8'
    if request.POST and (
            'q_title' in request.POST or 'q_author' in request.POST or 'q_source' in request.POST):  # 搜索事件

        content_query_title = str(request.POST['q_title'])
        content_query_author = str(request.POST['q_author'])
        content_query_source = str(request.POST['q_source'])
        flag1 = 0
        flag2 = 0
        flag3 = 0
        if request.POST['q_title']:
            flag1 = 1

            papers_list_title=[]
            for item in content_query_title.split(' '):
                cur.execute("select * from paper join document on paper.documentid=document.documentid where document.title LIKE \'%" + str(item) + "%\'")  # 这里最后换成实际数据库papers
                papers_list_title_tmp = cur.fetchall()  # 根据标题搜索到的结果
                papers_list_title.extend(papers_list_title_tmp)
            # print(papers_list_title[0][9],content_query_title)
            papers_list_title = get_ranked_paper(papers_list_title,content_query_title)
            # print(papers_list_title[0][9])

        if request.POST['q_author']:
            flag2 = 1
            cur.execute(
                "select * from paper join document on paper.documentid=document.documentid where author =\'" + content_query_author + "\'")  # 这里最后换成实际数据库papers
            papers_list_author = cur.fetchall()  # 根据作者搜索到的结果
        if request.POST['q_source']:
            flag3 = 1
            cur.execute(
                "select * from paper join document on paper.documentid=document.documentid where journalname =\'" + content_query_source + "\'")  # 这里最后换成实际数据库papers
            papers_list_source = cur.fetchall()  # 根据关键字(keyword in paper)搜索到的结果

        if flag1 == 1 and flag2 == 1 and flag3 == 1:
            list_title_author = [i for i in papers_list_title if i in papers_list_author]
            list_title_author_source = [i for i in list_title_author if i in papers_list_source]  # 三者交集
            papers_list_raw = list_title_author_source  # 取三者交集
        elif flag1 == 1 and flag2 == 1 and flag3 == 0:
            list_title_author = [i for i in papers_list_title if i in papers_list_author]  # 以下是三种两两交集
            papers_list_raw = list_title_author
        elif flag1 == 1 and flag2 == 0 and flag3 == 1:
            list_title_source = [i for i in papers_list_title if i in papers_list_source]
            papers_list_raw = list_title_source
        elif flag1 == 0 and flag2 == 1 and flag3 == 1:
            list_author_source = [i for i in papers_list_author if i in papers_list_source]
            papers_list_raw = list_author_source
        elif flag1 == 1 and flag2 == 0 and flag3 == 0:
            papers_list_raw = papers_list_title
        elif flag1 == 0 and flag2 == 1 and flag3 == 0:
            papers_list_raw = papers_list_author
        elif flag1 == 0 and flag2 == 0 and flag3 == 1:
            papers_list_raw = papers_list_source

    papers_list = []
    for paper in papers_list_raw:
        paper_dict = {"id": paper[5], "title": paper[9], "author": paper[1], "source": paper[2],
                      # "year": str(paper[10]).split('-')[0], "link": paper[7]
                      "year": str(paper[10]), "link": paper[7]}

        papers_list.append(paper_dict)

    paginator = Paginator(papers_list, 80)  # 实例化一个分页对象, 每页显示10个
    page = request.GET.get('page')  # 从URL通过get页码，如?page=3
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)  # 如果传入page参数不是整数，默认第一页
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    is_paginated = True if paginator.num_pages > 1 else False  # 如果页数小于1不使用分页
    context = {'page_obj': page_obj, 'is_paginated': is_paginated}

    login_statu = False
    if request.get_signed_cookie("login", salt="SSS", default=None) == 'yes':
        login_statu = True

    admin_=(admin_statu(request)=="True")
    return render(request, "papers.html", {"context": context, 'login_statu': login_statu, 'next_url': next_url
        ,"admin_statu":admin_})


def show_books(request):
    next_url = request.get_full_path()

    # conn = psycopg2.connect(database="postgres", user="dbuser", password="123@li", host="localhost", port="5432")
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")

    cur = conn.cursor()

    cur.execute("select * from book join document on book.documentid=document.documentid")  # 这里最后换成实际数据库books
    books_list_raw = cur.fetchall()

    request.encoding = 'utf-8'

    if request.POST and (
            'q_book_title' in request.POST or 'q_book_id' in request.POST or 'q_book_author' in request.POST
            or 'q_book_press' in request.POST or 'q_book_type' in request.POST
    ):  # 搜索事件
        content_query_title = str(request.POST['q_book_title'])
        content_query_id = str(request.POST['q_book_id'])
        content_query_author = str(request.POST['q_book_author'])
        content_query_press = str(request.POST['q_book_press'])
        content_query_type = str(request.POST['q_book_type'])

        if request.POST['q_book_title']:
            books_list_title=[]
            for item in content_query_title.split(' '):
                cur.execute("select * from book join document on book.documentid=document.documentid where document.title LIKE \'%" + str(item) + "%\'")  # 这里最后换成实际数据库papers
                books_list_title_tmp = cur.fetchall()  # 根据标题搜索到的结果
                books_list_title.extend(books_list_title_tmp)
            books_list_title=get_ranked_book(books_list_title,content_query_title)
        else:
            cur.execute("select * from book join document on book.documentid=document.documentid")
            books_list_title = cur.fetchall()  # 根据标题搜索到的结果
        # print(books_list_title)

        if request.POST['q_book_id']:
            cur.execute(
                "select * from book join document on book.documentid=document.documentid where isbn =\'" + content_query_id + "\'")  # 这里最后换成实际数据库papers
            books_list_id = cur.fetchall()  # 根据isbn搜索到的结果
        else:
            cur.execute("select * from book join document on book.documentid=document.documentid")
            books_list_id = cur.fetchall()  # 根据标题搜索到的结果

        if request.POST['q_book_author']:
            cur.execute(
                "select * from book join document on book.documentid=document.documentid where author =\'" + content_query_author + "\'")  # 这里最后换成实际数据库papers
            books_list_author = cur.fetchall()  # 根据关键字(keyword in paper)搜索到的结果
        else:
            cur.execute("select * from book join document on book.documentid=document.documentid")
            books_list_author = cur.fetchall()  # 根据标题搜索到的结果

        if request.POST['q_book_press']:
            cur.execute(
                "select * from book join document on book.documentid=document.documentid where publisher =\'" + content_query_press + "\'")  # 这里最后换成实际数据库papers
            books_list_press = cur.fetchall()  # 根据关键字(keyword in paper)搜索到的结果
        else:
            cur.execute("select * from book join document on book.documentid=document.documentid")
            books_list_press = cur.fetchall()  # 根据标题搜索到的结果

        if request.POST['q_book_type']:
            cur.execute(
                "select * from book join document on book.documentid=document.documentid where type =\'" + content_query_type + "\'")  # 这里最后换成实际数据库papers
            books_list_type = cur.fetchall()  # 根据关键字(keyword in paper)搜索到的结果
        else:
            cur.execute("select * from book join document on book.documentid=document.documentid")
            books_list_type = cur.fetchall()  # 根据标题搜索到的结果
        title_id = [i for i in books_list_title if i in books_list_id]
        title_id_author = [i for i in title_id if i in books_list_author]
        title_id_author_press = [i for i in title_id_author if i in books_list_press]
        title_id_author_press_type = [i for i in title_id_author_press if i in books_list_type]
        books_list_raw = title_id_author_press_type

    books_list = []
    # print(books_list_raw[0])
    for book in books_list_raw:
        book_dict = {"id": book[1], "title": book[8],
                     # "author": book[5], "press": book[2], "year": str(book[9]).split('-')[0],
                     "author": book[5], "press": book[2], "year": str(book[9]),
                     "type": book[6]}
        books_list.append(book_dict)

    login_statu = False
    if request.get_signed_cookie("login", salt="SSS", default=None) == 'yes':
        login_statu = True
    admin_=(admin_statu(request)=="True")

    return render(request, "books.html",
                  {"books_list": books_list, 'login_statu': login_statu, 'next_url': next_url,"admin_statu":admin_})


def user_login(request):
    # conn = psycopg2.connect(database="postgres", user="dbuser", password="123@li", host="localhost",port="5432")

    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    if request.method == 'POST':
        form = Form(request.POST)
        # 验证
        if form.is_valid:
            data = request.POST.dict()
            username = data.get('username')
            password = data.get('password')
            next_url = data.get('next_url')

            cur.execute("select * from users where username=\'" + username + "\'")  # 这里最后换成实际数据库books
            user_info = cur.fetchall()
            if(len(user_info)==0):
                # 弹出密码错误的提示并继续回到login界面
                return render(request, "login.html", {'next_url': next_url, 'psw_false': True})

            print(user_info)

            userid = user_info[0][0]
            pass_user = (user_info[0][3] == password)
            admin = user_info[0][2]
            # 通过user name向数据库检索密码与用户id，密码通过进行下面
            #
            # userid = '11'  # 暂时用这个代替,用户id为11
            # admin = 1  # 暂时用这个代替，0表示用户，1表示管理员
            # pass_user = True  # 暂时用这个，表示验证成功

            if pass_user == True:
                if next_url and next_url != "/logout/" and next_url!='None':
                    response = redirect(next_url)
                    response.set_signed_cookie("login", 'yes', salt="SSS", max_age=60 * 60 * 12)
                    response.set_signed_cookie("userid", userid, salt="SSS", max_age=60 * 60 * 12)
                    response.set_signed_cookie("admin", admin, salt="SSS",
                                               max_age=60 * 60 * 12)  # 如果是管理员则cookie中admin为true
                    return response
                else:
                    response = redirect("/home/")
                    response.set_signed_cookie("login", 'yes', salt="SSS", max_age=60 * 60 * 12)
                    response.set_signed_cookie("userid", userid, salt="SSS", max_age=60 * 60 * 12)
                    response.set_signed_cookie("admin", admin, salt="SSS",
                                               max_age=60 * 60 * 12)  # 如果是管理员则cookie中admin为true
                    return response
            else:
                # 弹出密码错误的提示并继续回到login界面
                return render(request, "login.html", {
                    'next_url': next_url, 'psw_false': True
                })

    # 用户刚进入本login页面先把传进来的next_url传到渲染出来的页面中
    next_url = request.GET.get("next_url")
    return render(request, "login.html", {
        'next_url': next_url
    })


def user_logout(request):
    if request.method == 'POST':
        rep = redirect("/hello/")
        # 删除用户浏览器上之前设置的cookie
        rep.delete_cookie('login')
        return rep


def show_home(request):
    if request.get_signed_cookie("login", salt="SSS", default=None) != 'yes':
        return render(request, "login.html")

    admin = request.get_signed_cookie("admin", salt="SSS", default=None)  # 0表示用户，1表示管理员

    if admin=="True":
        response = redirect("/home_admin/")
        return response
    else:
        response = redirect("/home_user/")
        return response


def show_home_admin(request):
    if request.get_signed_cookie("login", salt="SSS", default=None) != 'yes':
        return render(request, "login.html")
    if admin_statu(request) != "True" :
        response = redirect("not_admin_error")
        return response
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()

    userid = request.get_signed_cookie("userid", salt="SSS", default=None)

    profile = get_profile(userid)
    user_list = get_user_list()

    # 如果管理员想要进行修改自己的密码
    if request.POST and ("new_psw14user" in request.POST or "new_psw24user" in request.POST
                         or "username4user" in request.POST) :
        data = request.POST.dict()
        userid4user = data.get('userid4user')
        new_psw1 = data.get('new_psw14user')
        new_psw2 = data.get('new_psw24user')
        if (new_psw1 == new_psw2):  # 也就是两遍确定的一致
            cur.execute("update users set password =\'" + str(new_psw1) + "\' where userid=\'" + userid4user + "\'")
            #             根据userid和new_psw1进行对应user表的修改
            if request.POST["username4user"]:
                cur.execute("update users set username =\'" + str(request.POST["username4user"]) + "\' where userid=\'" + userid4user + "\'")
            conn.commit()
            profile=get_profile(userid4user)
            return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile,"box_index": 0})
        else:#两边输入不一致或没有输入密码
            info="您刚才修改密码失败，可能因为输入的两边密码不一致或没有输入"
            print(info)
            if request.POST["username4user"]:
                cur.execute("update users set username =\'" + str(request.POST["username4user"]) + "\' where userid=\'" + userid4user + "\'")
            conn.commit()
            profile=get_profile(userid4user)

            return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile,"box_index": 0})


    # 在用户列表处的用户搜索
    if request.POST and ("userid4search" in request.POST or "user_name4search" in request.POST or "user_type4search" in request.POST):

        cur.execute("select * from users")
        user_list_raw = cur.fetchall()

        if (str(request.POST["userid4search"])!=''):
            cur.execute("select * from users where userid=\'" + request.POST["userid4search"] + "\'")
            search1_list = cur.fetchall()
        else:
            search1_list = user_list_raw
        if (str(request.POST["user_name4search"])!=''):
            cur.execute("select * from users where username=\'" + request.POST["user_name4search"] + "\'")
            search2_list = cur.fetchall()
        else:
            search2_list = user_list_raw
        if (str(request.POST["user_type4search"])!=''):
            cur.execute("select * from users where type=\'" + request.POST["user_type4search"] + "\'")
            search3_list = cur.fetchall()
        else:
            search3_list = user_list_raw

        # 三者取交集,将user_list更新为搜索结果并返回渲染
        search12_list = [i for i in search1_list if i in search2_list]
        user_list = [i for i in search12_list if i in search3_list]
        user_list = [{"username": user[1], "userid": user[0], "type": user[5]} for user in user_list]

        return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile, "box_index": 3})

    # 管理员点击用户列表中某一列最后的查看详情按钮时，要进行查询该用户的信息并返回管理员看到的用户信息界面
    if request.POST and ("userid4admin" in request.POST):
        userid4admin = request.POST["userid4admin"]
        profile=get_profile(userid)
        user_profile = get_profile(userid4admin)
        user_list=get_user_list()
        # print(user_profile)
        #box_index为1表示返回到管理员看到的用户信息
        return render(request, "home_admin.html", {'user_list': user_list, 'user_profile': user_profile, 'profile': profile, "box_index": 1})

    # 管理员在管理员修改用户界面，并且点击修改信息的按钮时；这里仅有修改密码的案例
    if request.POST and ("new_psw14admin_change" in request.POST or 'username4admin_change' in request.POST):
        data = request.POST.dict()
        username = data.get('username4admin_change')
        userid = data.get('userid4admin_change')
        new_psw1 = data.get('new_psw14admin_change')
        new_psw2 = data.get('new_psw24admin_change')

        profile = get_profile(userid)
        user_list = get_user_list()
        if new_psw1 == new_psw2 and str(new_psw1)!= '':  # 也就是两遍密码确定的一致且输入了密码
            cur.execute("update users set password =\'" + new_psw1 + "\' where userid=\'" + userid + "\'")
            #根据userid和new_psw1进行对应user表的修改
            if ("username4admin_change" in request.POST):
                cur.execute("update users set username =\'" + username + "\' where userid=\'" + userid + "\'")
            conn.commit()

            return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile,"box_index": 3})

        elif 'username4admin_change' in request.POST:#否则就是密码输入不一致或没有输入密码
            print(username)
            cur.execute("update users set username =\'" + username + "\' where userid=\'" + userid + "\'")
            conn.commit()

            user_list = get_user_list()
            return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile, "box_index": 3})
        else:#什么都没有做，直接返回用户列表
            return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile, "box_index": 3})

    # 管理员删除用户
    if request.POST and ("userid4admin_delete" in request.POST):
        cur.execute("delete from users where userid=\'" + request.POST["userid4admin_delete"] + "\'")
        conn.commit()
        user_list = get_user_list()
        #box_index为3表示返回到用户列表
        return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile,"box_index": 3})

    #管理员新增用户
    if request.POST and ("username4add" in request.POST):
        cur.execute("select max(userid) from users")
        re=cur.fetchall()
        print(request.POST["type4add"])
        cur.execute("insert into users  values(\'"+str(re[0][0]+1)
                    +"\',\'"+request.POST["username4add"]
                    + "\',\'" + "False"
                    + "\',\'" + request.POST["psw14add"]
                    + "\',\'" + "真实姓名"
                    + "\',\'" + request.POST["type4add"]
                    +"\')")
        conn.commit()

        user_list = get_user_list()
        #box_index为3表示返回到用户列表
        return render(request, "home_admin.html",{'user_list': user_list, 'profile': profile,"box_index": 3})

    return render(request, "home_admin.html",
                  {'user_list': user_list, 'profile': profile,"box_index": 0})


def show_home_user(request):

    if request.get_signed_cookie("login", salt="SSS", default=None) != 'yes':
        return render(request, "login.html")
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    userid = request.get_signed_cookie("userid", salt="SSS", default=None)

    profile = get_profile(userid)
    borrow_list = get_borrow_list(userid)

    if request.POST and ("new_psw14user" in request.POST or "new_psw24user" in request.POST
                         or "username4user" in request.POST) :
        data = request.POST.dict()
        userid4user = data.get('userid4user')
        new_psw1 = data.get('new_psw14user')
        new_psw2 = data.get('new_psw24user')
        if (new_psw1 == new_psw2):  # 也就是两遍确定的一致
            cur.execute("update users set password =\'" + str(new_psw1) + "\' where userid=\'" + userid4user + "\'")
            #             根据userid和new_psw1进行对应user表的修改
            if request.POST["username4user"]:
                cur.execute("update users set username =\'" + str(request.POST["username4user"]) + "\' where userid=\'" + userid4user + "\'")
            conn.commit()
            profile=get_profile(userid4user)

            return render(request, "home_admin.html",{'borrow_list': borrow_list, 'profile': profile,"box_index": 0})
        else:#两边输入不一致或没有输入密码
            info="您刚才修改密码失败，可能因为输入的两边密码不一致或没有输入"
            print(info)
            if request.POST["username4user"]:
                cur.execute("update users set username =\'" + str(request.POST["username4user"]) + "\' where userid=\'" + userid4user + "\'")
            conn.commit()
            profile=get_profile(userid4user)
            return render(request, "home_admin.html",{'borrow_list': borrow_list, 'profile': profile,"box_index": 0})

    # 如果用户点击了某个书籍的还书按钮
    if request.POST and ("book_id_return" in request.POST):
        # 最好后面再增加一个确认已经还了本书的页面，参数带上book_id和userid
        # 根据当前的book_id以及userid进行borrow_list的删除该借书记录的操作并
        cur.execute("delete from borrowlist where userid=\'" + request.POST["userid4user"] + "\'and documentid=\'" +
            request.POST["book_id_return"] + "\'")
        cur.execute("update book set CopyNum = CopyNum+1 where documentid=\'" + request.POST["book_id_return"] + "\'")
        conn.commit()

        borrow_list = get_borrow_list(userid)
        return render(request, "home_user.html",{'profile': profile, 'borrow_list': borrow_list,"box_index": 2})

    return render(request, "home_user.html",{'profile': profile, 'borrow_list': borrow_list,"box_index": 0})


# 新增paper
def paper_add(request):
    print(admin_statu(request))
    if admin_statu(request) != "True" :
        response = redirect("not_admin_error")
        return response

    # conn = psycopg2.connect(database="postgres", user="dbuser", password="123@li", host="localhost", port="5432")
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    # 	有form表单且合法：
    if request.POST and ("paper_title_add" in request.POST and "paper_source_add" in request.POST and
                         "paper_year_add" in request.POST and "paper_link_add" in request.POST and "paper_volnum_add" in request.POST
                         and "paper_pagen_add" in request.POST and "paper_pagenum_add" in request.POST):
        cur.execute("select max(documentid) from document")
        re = cur.fetchall()
        cur.execute("select max(paperid) from paper")
        re2 =cur.fetchall()

        cur.execute("insert into document values(\'"
                    + str(re[0][0] + 1) + "\',\'"
                    + request.POST["paper_title_add"] + "\',\'"
                    + request.POST["paper_year_add"] + "\',\'"
                    + "" + "\',\'"
                    + "" + "\',\'"
                    + request.POST["paper_pagenum_add"] + "\')")

        cur.execute("insert into paper values(\'"
                    + str(re2[0][0] + 1) + "\',\'"
                    +""+"\',\'"
                    +request.POST["paper_source_add"]+"\',\'"
                    +""+"\',\'"
                    +request.POST["paper_volnum_add"]+"\',\'"
                    +str(re[0][0] + 1)+"\',\'"
                    +request.POST["paper_pagen_add"]+"\',\'"
                    +request.POST["paper_link_add"]+"\')")


        conn.commit()
        response = redirect("/papers/")
        return response
    # 		返回到paper.html界面
    return render(request, "paper_add.html")


# 新增图书
def book_add(request):
    if admin_statu(request) != "True" :
        response = redirect("not_admin_error")
        return response

    # conn = psycopg2.connect(database="postgres", user="dbuser", password="123@li", host="localhost", port="5432")
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    # 	有form表单且合法：
    if request.POST and ("book_title_add" in request.POST and "book_isbn_add" in request.POST and
                         "book_type_add" in request.POST and "book_press_add" in request.POST and "book_year_add" in request.POST
                         and "book_pagenum_add" in request.POST and "book_picture_add" in request.POST):
        cur.execute("select max(documentid) from document")
        re = cur.fetchall()
        cur.execute("insert into document values(\'"
                    + str(re[0][0] + 1) + "\',\'"
                    + request.POST["book_title_add"] + "\',\'"
                    + request.POST["book_year_add"] + "\',\'"
                    + request.POST["book_picture_add"] + "\',\'"
                    + "" + "\',\'"
                    + request.POST["book_pagenum_add"] + "\')")

        cur.execute("insert into book values(\'"
                    + request.POST["book_isbn_add"] + "\',\'"
                    + str(re[0][0] + 1) + "\',\'"
                    + request.POST["book_press_add"] + "\',\'"
                    + "2" + "\',\'"
                    + "" + "\',\'"
                    + "" + "\',\'"
                    + request.POST["book_type_add"] + "\')")

        conn.commit()
        if(get_book_num()>100):
            book_delete = delete_oldest_book()
            return render(request, "full_alert.html",{"book":book_delete,"login_statu":login_statu})

        response = redirect("/books/")
        return response
    # 		返回到paper.html界面
    return render(request, "book_add.html")


def show_paper_detail(request):

    paper_id = request.get_full_path().split('?paper_id=')[1]

    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    cur.execute("select * from paper join document on paper.documentid=document.documentid where paper.documentid =\'" + str(paper_id) + "\'")  # 这里最后换成实际数据库papers
    paper_info = cur.fetchall()  # 根据isbn搜索到的结果
    print(paper_info)
    paper_info=paper_info[0]
    paper_info={"id":paper_info[5],"title":paper_info[9],"source":paper_info[2],"year":paper_info[10],"link":paper_info[7],
                "volnum":paper_info[4],"pagen":paper_info[6],"pagenum":paper_info[13],"abstract":paper_info[12]}
    login_statu = False
    if request.get_signed_cookie("login", salt="SSS", default=None) == 'yes':
        login_statu = True

    admin = request.get_signed_cookie("admin", salt="SSS", default=None)  # 0表示用户，1表示管理员
    if admin=="True":
        admin_statu=True
    else:
        admin_statu=False

    return render(request, "paper_detail.html", {"paper_info":paper_info,"login_statu":login_statu,"admin_statu":admin_statu,
                                                 "paper_id":paper_id})


def show_book_detail(request):
    userid = request.get_signed_cookie("userid", salt="SSS", default=None)

    book_id = request.get_full_path().split('?book_id=')[1]
    print('ceshi',book_id)
    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    cur.execute("select * from book join document on book.documentid=document.documentid where book.documentid =\'" + book_id + "\'")  # 这里最后换成实际数据库papers
    book_info = cur.fetchall()  # 根据isbn搜索到的结果
    book_info=book_info[0]
    book_info={"id":book_info[1],"title":book_info[8],"isbn":book_info[0],"type":book_info[6],"press":book_info[1],
               "year":book_info[9],"pagenum":book_info[12],"abstract":book_info[11]}
    login_statu = False
    if request.get_signed_cookie("login", salt="SSS", default=None) == 'yes':
        login_statu = True

    admin = request.get_signed_cookie("admin", salt="SSS", default=None)  # 0表示用户，1表示管理员
    if admin=="True":
        admin_statu=True
    else:
        admin_statu=False
    if request.POST and ("book_id_borrow" in request.POST):

        cur.execute("insert into borrowlist values(\'"
                    + request.POST["book_id_return"] + "\',\'"
                    + str(datetime.date.today()) + "\',\'"
                    + str(datetime.date.today() + datetime.timedelta(days=30)) + "\',\'"
                    + userid + "\')")

        cur.execute("update book set CopyNum = CopyNum-1 where documentid=\'" + request.POST["book_id_borrow"] + "\'")

        conn.commit()
        response = redirect("/home_user/")
        return response

    return render(request, "book_detail.html", {"book_info":book_info,"login_statu":login_statu,"admin_statu":admin_statu,
                                                "book_id":book_id})

# show_paper_detail:
# 	接受当前参数request.get("paper_id")#这是a herf传入的
# 	根据paper_id查paper详细信息
# 	返回渲染paper_detail.html
# show_book_detail:
# 	接受当前参数request.get("book_id")#这是a herf传入的
# 	根据book_id查paper详细信息
# 	返回渲染book_detail.html


def paper_op(request):
    # paper_id = request.get_full_path().split('?paper_id=')[1]
    if admin_statu(request) != "True" :
        response = redirect("not_admin_error")
        return response
    path_items=request.get_full_path().split('?paper_id=')
    if(len(path_items)>1):
        paper_id = path_items[1]

    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    #如有post请求则修改，并且完成修改后重新查询该paper信息并至paper_detail界面
    if(request.POST) and ("delete_signal" in request.POST):
        cur.execute("delete from paper where documentid=\'"+request.POST["paper_id4delete"]+"\'")
        cur.execute("delete from document where documentid=\'"+request.POST["paper_id4delete"]+"\'")

        conn.commit()
        response = redirect("/papers/")
        return response

    if(request.POST) and ("paper_title_op" in request.POST or "paper_source_op" in request.POST or "paper_year_op" in request.POST or
    "paper_link_op" in request.POST or "paper_volnum_op" in request.POST or "paper_pagen_op" in request.POST or
    "paper_pagenum_op" in request.POST):
        if request.POST["paper_title_op"]:
            cur.execute("update document set title =\'"+request.POST["paper_title_op"]+"\'where documentid =\'"+request.POST["paper_id4change"]+"\'")
        if request.POST["paper_source_op"]:
            cur.execute("update paper set journalname =\'"+request.POST["paper_source_op"]+"\'where documentid =\'"+request.POST["paper_id4change"]+"\'")
        if request.POST["paper_year_op"]:
            cur.execute("update document set publicationdate =\'"+request.POST["paper_year_op"]+"\'where documentid =\'"+request.POST["paper_id4change"]+"\'")
        if request.POST["paper_link_op"]:
            cur.execute("update paper set link =\'"+request.POST["paper_link_op"]+"\'where documentid =\'"+request.POST["paper_id4change"]+"\'")
        if request.POST["paper_volnum_op"]:
            cur.execute("update paper set volumenumber =\'"+request.POST["paper_volnum_op"]+"\'where documentid =\'"+request.POST["paper_id4change"]+"\'")
        if request.POST["paper_pagen_op"]:
            cur.execute("update paper set pagenumber =\'"+request.POST["paper_pagen_op"]+"\'where documentid =\'"+request.POST["paper_id4change"]+"\'")
        if request.POST["paper_pagenum_op"]:
            cur.execute("update document set pagecount =\'"+request.POST["paper_pagenum_op"]+"\'where documentid =\'"+request.POST["paper_id4change"]+"\'")
        conn.commit()
        response = redirect("/papers/")
        return response

    return render(request, "paper_op.html",{"paper_id":paper_id})

def book_op(request):
    if admin_statu(request) != "True" :
        response = redirect("not_admin_error")
        return response
    path_items=request.get_full_path().split('?book_id=')
    if(len(path_items)>1):
        book_id = path_items[1]
    # book_id=request.get_full_path().split('?book_id=')[1]

    conn = psycopg2.connect(database="postgres", user="liu1", password="Liu@200193", host="124.70.85.191", port="5432")
    cur = conn.cursor()
    #如有post请求则修改，并且完成修改后重新查询该book信息并跳转至book_detail界面
    if (request.POST) and ("delete_signal" in request.POST):
        cur.execute("delete from book where documentid=\'"+request.POST["book_id4delete"]+"\'")
        cur.execute("delete from document where documentid=\'"+request.POST["book_id4delete"]+"\'")
        conn.commit()
        response = redirect("/books/")
        return response

    if(request.POST) and ("book_title_op" in request.POST or "book_isbn_op" in request.POST or "book_year_op" in request.POST or
    "book_press_op" in request.POST or "book_picture_op" in request.POST or
    "book_pagenum_op" in request.POST):
        if("book_title_op" in request.POST):
            cur.execute("update document set title =\'"+request.POST["book_title_op"]+"\'where documentid =\'"+request.POST["book_id4change"]+"\'")
        if("book_isbn_op" in request.POST):
            cur.execute("update book set isbn =\'"+request.POST["book_isbn_op"]+"\'where documentid =\'"+request.POST["book_id4change"]+"\'")
        if("book_year_op" in request.POST):
            cur.execute("update document set publicationdate =\'"+request.POST["book_year_op"]+"\'where documentid =\'"+request.POST["book_id4change"]+"\'")
        if("book_press_op" in request.POST):
            cur.execute("update book set publisher =\'"+request.POST["book_press_op"]+"\'where documentid =\'"+request.POST["book_id4change"]+"\'")
        if("book_picture_op" in request.POST):
            cur.execute("update document set picture =\'"+request.POST["book_picture_op"]+"\'where documentid =\'"+request.POST["book_id4change"]+"\'")
        if("book_pagenum_op" in request.POST):
            cur.execute("update document set pagecount =\'"+request.POST["book_pagenum_op"]+"\'where documentid =\'"+request.POST["book_id4change"]+"\'")
        if ("book_type_op" in request.POST):
            cur.execute(
                "update book set type =\'" + request.POST["book_type_op"] + "\'where documentid =\'" +
                request.POST["book_id4change"] + "\'")

        conn.commit()
        response = redirect("/books/")
        return response

    return render(request, "book_op.html",{"book_id":book_id})


# paper_op函数
# 	接受当前参数request.get("paper_id")#这是paper_detail 的a herf传入的（paper_detail可以获取到{{paper_info.id}}）
# 	if有form的post请求：
# 		根据form表单内容与paper_id进行修改操作
# 	返回渲染paper_op.html
#
# book_op函数
# 	接受当前参数request.get("book_id")#这是book_detail 的a herf传入的（book_detail可以获取到{{book_info.id}}）
# 	if有form的post请求：
# 		根据form表单内容与book_id进行修改操作
# 	返回渲染book_op.html

def not_admin_error(request):
    return render(request, "not_admin_error.html")


def full_alert(request):
    return render(request, "full_alert.html")