## 一、背景

`Django` 作为后端框架，提供 `api` 接口，`Vue.js` 作为前端框架，代替 `Django` 薄弱的模板引擎，使得前后端完全分离，也适合单页应用的开发构建。

本项目为一个单页项目，实现功能：

- 运行 `Django` 项目，可查询所有书籍
- 可添加书籍，并实时刷新

**项目整体目录结构**

```python
├── django_vue/	
    ├── approot/		# django app
    ├── django_vue		# 项目主配置
    |    ├── settings.py	
    ├── frontend/		# 前端文件
    |    ├── build/	
    |    ├── config/	
    |    ├── dist/	# 打包后前端文件放的位置
    |    ├── node_modules/	# 依赖、库
    |    ├── src/	
    |    ├── static/	# 纯静态资源
    ├── db.sqlite3		
    ├── manage.py
```

## 二、环境准备

- 后端：
  - `Django 2.1.1`：可用 `DRF`
  - `Python3.6.9`
  - `django-cors-headers`：解决跨域问题
- 前端：
  - `Vue.js`
  - `Element-UI`：饿了么推出的前台 `UI` 框架，有许多精美的 `UI` 文件
  - `vue-resource`：提供 `ajax` 请求服务
  - `vue-cli` 脚手架：快速搭建 `Vue` 项目

## 三、构建 Django 项目

1、创建项目和 `app`：

```python
python manage.py startproject django_vue
python manage.py startapp approot
```

2、新增模型类 `approot/models.py`：

```python
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=64, verbose_name='书名')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    def __str__(self):
        return self.name
```

迁移数据库文件：

```python
python manage.py makemigrations
python manage.py migrate
```

3、配置路由：

项目根目录，`django_vue/urls.py`：

```python
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('approot.urls')),	# 提供 api 接口，连接 app：approot
    
    # Vue 前端页面，后面会用到
    re_path(r'^$', TemplateView.as_view(template_name='index.html')),
]
```

新增 `approot/urls.py`：

```python
from django.urls import path

from approot import views

urlpatterns = [
    path('book/list/', views.BookListView.as_view(), name='book_list'),
    path('book/create/', views.BookCreateView.as_view(), name='book_create'),
]
```

新增两个 `api` 接口（路由），分别用于查询所有书籍和添加书籍。

4、视图函数 `approot/views.py`：

```python
import json

from django.core import serializers
from django.http import JsonResponse
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
```

这里采用的是 `Django CBV`，当然也可以使用 `DRF`。

5、配置文件：`django_vue/settings.py`：

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'approot',
    'corsheaders',	# 跨域访问设置
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # 跨域访问设置
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True  # 新增的跨域访问设置

# 模板文件
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [os.path.join(BASE_DIR, 'templates')]
        'DIRS': ['frontend/dist'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

STATIC_URL = '/static/'

# 静态文件
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/dist/static"),
]
```

这里需要提前安装 `pip install django-cors-headers`，用于解决 `Vue` 模板向 `Django` 后端请求跨域问题。

至此后端基本已配置完毕，可用 `postman` 测试下接口是否能够正常返回。

> 注意：模板文件和静态文件中的  `dist` 目录，会在 `Vue` 打包时生成

## 四、构建 Vue.js 前端项目

前端总共可以分为以下几个步骤：

- 安装 `node.js、nrm`，更换源为淘宝源

- 安装 `vue-cli`，并 使用 `vue-cli` 脚手架快速生成 `Vue.js` 模板文件
- 安装 `Element-UI、vue-resource` 等依赖
- 运行测试：`npm run dev`
- 打包：`npm run build`

### 安装 node.js

`node.js` 安装没什么好说的，一路安装即可，记得要勾选 `Add PATH`，添加到环境变量。

[官网地址](https://nodejs.org/zh-cn/)

安装成功后，测试：

```python
C:\Users\hj>node --version
v12.18.0

C:\Users\hj>npm --version
6.14.4
```

**nrm 安装**

`nrm` 用于提供一些常用 `NPM` 包镜像地址，包括 `cnpm`、淘宝镜像等

```python
npm i nrm -g	# 全局安装
nrm ls	# 查看当前可用镜像源地址
nrm use taobao	# 切换镜像源为 淘宝，速度会快很多

C:\Users\hj>nrm ls

  npm -------- https://registry.npmjs.org/
  yarn ------- https://registry.yarnpkg.com/
  cnpm ------- http://r.cnpmjs.org/
* taobao ----- https://registry.npm.taobao.org/
  nj --------- https://registry.nodejitsu.com/
  npmMirror -- https://skimdb.npmjs.com/registry/
  edunpm ----- http://registry.enpmjs.org/
```

### vue-cli 快速生成项目

1、安装

```vue
npm install -g vue-cli		// 全局安装
```

2、创建工程项目

```vue
cd django_vue	// 切换到后端项目根目录
vue init webpack frontend	// 初始化项目，需要手动配置一系列配置，如：项目描述、作者、打包方式，是否使用 ESLint 规范代码等
```

**目录结构**

```python
├── frontend/	
    ├── build/		# webpack 编译任务配置文明：开发环境与生产环境
    ├── config
    |    ├── index.js	# 项目核心配置
    ├── src/
    |    ├── main.js	# 程序入口文件
    |    ├── App.vue	# 程序入口 vue 组件
    |    ├── components/	# 组件
    |    ├── assets/	# 资源文件夹，一般放图片之类的
    |    ├── router/	# 路由
    ├── static/		# 纯静态资源
    ├── index.html
    └── node_modules/	# 项目中的依赖模块
    └── .babelrc	# bael 配置文件
    └── .editorconfig	# 编辑配置文件
    └── .gitignore	# 忽略文件
    └── package.json	# 项目文件，记载一些命令和依赖还有简要项目描述信息
    └── README.md	
    └── index.html	# 入口模板文件
```

### 安装其他依赖

**Element-UI**

提供 `UI` 组件

```python
npm install element-ui --save
npm install element-theme -g	# 全局安装
```

引入 `frontent/src/main.js`：

```python
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
Vue.use(ElementUi)
```

**vue-resource**

用于向后端发起请求

```python
 npm i vue-resource --save 
```

引入 `frontent/src/main.js`：

```python
import VueResource from 'vue-resource'
Vue.use(VueResource)
```

### 新增组件 Home

在 `frontend/src/components/` 下添加新的组件 `Home.vue`：

```vue
<template>
  <div class="home">
    <el-row display="margin-top: 10px">
      <el-input v-model="input" placeholder="请输入书名" style="display:inline-table; width: 30%; float:left"></el-input>
      <el-button type="primary" @click="addBook()" style="float:left; margin: 2px;">新增</el-button>
    </el-row>

    <el-row>
      <el-table :data="bookList" style="width: 100%" border>
        <el-table-column prop="id" label="编号" min-width="100">
          <template scope="scope"> {{ scope.row.pk }}</template>
        </el-table-column>
        <el-table-column prop="book_name" label="书名" min-width="100">
          <template scope="scope"> {{ scope.row.fields.name }}</template>
        </el-table-column>
        <el-table-column prop="add_time" label="添加时间" min-width="100">
          <template scope="scope"> {{ scope.row.fields.add_time }}</template>
        </el-table-column>
      </el-table>
    </el-row>
  </div>
</template>

<script>
  export default {
    name: "home",
    data () {
      return {
        input: '',
        bookList: [],
      }
    },
    mounted: function(){
      this.showBooks()
    },
    methods: {
      addBook() {
        this.$http.get('http://127.0.0.1:8000/api/book/create?name=' + this.input)
          .then((response) => {
            var res = JSON.parse(response.bodyText);
            if (res.code === 0) {
              this.showBooks()
            } else {
              this.$message.error('新增书籍失败，请重试');
              console.log(res['msg']);
            }
          })
      },
      showBooks() {
        this.$http.get('http://127.0.0.1:8000/api/book/list')
          .then((response) => {
            var res = JSON.parse(response.bodyText);
            console.log('查询书籍：', res);
            if (res.code === 0) {
              this.bookList = res['data']
            } else {
              this.$message.error("查询书籍失败！");
              console.log(res['msg']);
            }
          })
      }
    }
  }
</script>

<style scoped>
  h1, h2 {
    font-weight: normal;
  }

  ul {
    list-style-type: none;
    padding: 0;
  }

  li {
    display: inline-block;
    margin: 0 10px;
  }

  a {
    color: #42b983;
  }
</style>
```

其中 `el-row` 为 `Element-UI` 中所有，`$.http` 为 `vue-resource` 所有。该组件作用：

- `template`：展示一个表格（书籍信息）
- `script`：向后端发送请求，请求数据（查询、新增书籍）

> 注意：这里使用到 `Element-UI、vue-resource`，还需要在 `frontend/src/router/index.js` 进行引用

### 配置前端路由

`frontend/src/router/index.js` ：

```vue
import Vue from 'vue'
import Router from 'vue-router'
// import HelloWorld from '@/components/HelloWorld'
import Home from '@/components/Home'	// 一定要先引用 Home 组件，否则运行失败
import ElementUi from 'element-ui'
// import '@/theme-et/index.css'
Vue.use(ElementUi)

Vue.use(Router)

export default new Router({
  // routes: [
  //   {
  //     path: '/',
  //     name: 'HelloWorld',
  //     component: HelloWorld
  //   }
  // ]

  routes: [
    {
      path: '/',
      name: 'Home',		// Home 组件名称
      component: Home
    }
  ]
})
```

### 打包测试

在此之前我们已经用 `postman` 测试了后端 `api` 接口，这里将测试前端能够正常展示页面。

1、测试运行前端项目

```vue
cd frontend
npm run dev
```

访问：`http://localhost:8080/`，`F12` 诊断查看下是否报错。

2、打包

```vue
cnpm install  // 安装依赖，或 npm install

cd frontend
npm run build	// 打包，会在 frontend/ 下生成 dist 目录，其中有static/、index.html
```

打包成功的信息：

![](https://hubery624.oss-cn-shenzhen.aliyuncs.com/20200618091337.png)

关闭前端 `npm run dev`，运行后端 `python manage.py runserver`，访问 `http://127.0.0.1:8000/#/` 即可，若一切正常的话可以看到如下界面：

![](https://hubery624.oss-cn-shenzhen.aliyuncs.com/20200618090545.png)

## 参考文章

- [整合 Django + Vue.js 框架快速搭建 web 项目](https://segmentfault.com/p/1210000010550731/read#top)
- [源码](https://github.com/rogerlh/django_with_vue)
- [vue-cli 脚手架安装](https://www.jianshu.com/p/1ee1c410dc67)
- [Vue + Vue-router + Element-ui  搭建一个非常简单的dashboard demo](https://segmentfault.com/a/1190000012015667)
- [在vue项目中使用elementui](https://www.jianshu.com/p/e64004e7ca6a)
- [vue2.0项目引入element-ui](https://segmentfault.com/a/1190000011023102)
- [vue使用vue-resource插件请求数据](https://www.jianshu.com/p/fcbc904f9792)





