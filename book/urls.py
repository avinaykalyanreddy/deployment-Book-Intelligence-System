from django.urls import path
from .views import  *

urlpatterns = [

    path("books/",get_books,name="get_books"),
    path("upload/",upload_book,name="upload_book"),
    path("ask/",ask_question,name='ask_question'),
    path('recommend/<int:book_id>/', recommend_books),
]