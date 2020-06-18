import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View

from approot.models import Book


class BookListView(View):
    """书籍列表"""

    def get(self, request):
        res = {'code': 0, 'msg': '查询成功', 'data': []}
        try:
            book_list = Book.objects.all()
            book_list = json.loads(serializers.serialize("json", book_list))
            res['data'] = book_list
        except Exception as e:
            res['code'] = -1
            res['msg'] = '查询失败'

        return JsonResponse(res)


class BookCreateView(View):
    """添加书籍"""

    def get(self, request):
        res = {'code': 0, 'msg': '添加成功', 'data': []}
        try:
            name = request.GET.get('name')
            Book.objects.create(name=name)
        except Exception as e:
            res['code'] = -1
            res['msg'] = '添加失败'

        return JsonResponse(res)
