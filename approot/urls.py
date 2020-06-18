from django.urls import path

from approot import views

urlpatterns = [
    path('book/list/', views.BookListView.as_view(), name='book_list'),
    path('book/create/', views.BookCreateView.as_view(), name='book_create'),
]