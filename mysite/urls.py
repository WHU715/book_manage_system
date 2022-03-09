"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('papers/', views.show_papers),
    path('hello/', views.hello),
    url(r'^$', views.show_books),
    path('books/', views.show_books),

    path('home/', views.show_home, name='home'),
    path('home_admin/', views.show_home_admin, name='home_admin'),
    path('home_user/', views.show_home_user, name='home_user'),

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('book_detail/', views.show_book_detail, name='book_detail'),
    path('paper_detail/', views.show_paper_detail, name='paper_detail'),

    path('paper_op/', views.paper_op, name='paper_op'),
    path('paper_add/', views.paper_add, name='paper_add'),
    path('book_op/', views.book_op, name='book_op'),
    path('book_add/', views.book_add, name='book_add'),

    path('not_admin_error/', views.not_admin_error, name='not_admin_error'),
    path('full_alert/', views.full_alert, name='full_alert'),

]