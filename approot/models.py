from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=64, verbose_name='书名')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    def __str__(self):
        return self.name

