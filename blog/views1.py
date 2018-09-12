# -*- coding:utf-8 -*-
import json
import re
import sys 
import os
from math import sqrt
import jieba
import jieba.analyse
import jieba.posseg as psg
from collections import Counter
import datetime
import time
from django.db.models import Q
from collections import OrderedDict
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import get_user_model

from django.views.generic import View, DetailView, ListView
from django.db.models import Count
from zer0Blog.settings import PERNUM
from tagging.models import TaggedItem

from blog.pagination import paginator_tool
from .models import Post, Carousel, Comment, Repository, Catalogue, User,UReport,Maincategory, Collection,Secret, RecommendList
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from email.header import Header
from django import forms
from django.shortcuts import render,redirect
from blog.templatetags.blog_tags import get_tags


class report_view(View):
     def post(self, request, *args, **kwargs):
         user = self.request.user
         if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
         cbox_list = request.POST.getlist('s') 
         print (cbox_list)
         pkey = self.kwargs.get("pk", "")
         print (user)
         se = Post.objects.filter(id = pkey)
         sv = se[0]
         string  = sv.title
         report = UReport.objects.create(
             ruser = user,
             post = string,
             reason = cbox_list,
             pname = user,
            )
         ur = User.objects.filter(name = user)
         urr = ur[0]
         _user = settings.EMAIL_HOST_USER1
         _pwd  = settings.EMAIL_HOST_PASSWORD1
         _to   =  urr.email
         msg = MIMEText('您举报的博文《'+string+'》已被举报成功，感谢你为净化网络环境所做的贡献','plain','utf-8')
         subject = '技术之心处理结果'
         msg['Subject'] = Header(subject, 'utf-8')
         msg['From']    =  _user
         msg['To']      =  _to
         s = smtplib.SMTP_SSL('smtp.qq.com',465)
         s.login(_user,_pwd) 
         s.sendmail(_user,_to,msg.as_string())
         s.quit()
         return HttpResponseRedirect('/post/'+pkey)
class BaseMixin(object):

    def get_context_data(self, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        try:
            context['hot_article_list'] = Post.objects.filter(status=1,stype=0).order_by("-view_count")[0:10]
            # context['man_list'] = get_user_model().objects.annotate(Count("post"))
            context['hot_news_list'] = Post.objects.filter(status=1,stype=1).order_by("-view_count")[0:10]
            context['suser_list']= get_user_model().objects.raw('select *, COUNT(post.id) as counts from blog_user as user LEFT JOIN blog_post post ON post.stype=1 and post.status=1 and post.author_id=user.id GROUP BY user.id');
            context['man_list'] = get_user_model().objects.raw('select *, COUNT(post.id) as counts from blog_user as user LEFT JOIN blog_post post ON post.status=1 and post.author_id=user.id GROUP BY user.id');
            mlist = Maincategory.objects.all()
            context['maincate_list'] = mlist
            context['catalogue'] = Catalogue.objects.all()
            context['tag_list'] = get_tags()
            d = {}
            for cata in Catalogue.objects.all():
                d[cata] = 0
            for p in Post.objects.filter(status=1,stype =0):
                d[p.catalogue] += 1

            d2 = {}
            for cate in Maincategory.objects.all():
                d2[cate.id] = 0
            for cata in Catalogue.objects.all():
                d2[cata.catename.id] += d[cata]
            # print(d2)
            context['cata_d'] = d
            context['cate_d'] = d2
            # print(len(mlist))
            pxlist = []
            for i in range(len(mlist)):
                top = -(len(mlist)-i)*47-20


                pxlist.append(top)
            context['px_list'] = pxlist
            context['zip'] = zip(mlist,pxlist)
        except Exception as e:
            pass

        return context
def change_view(request):
    return HttpResponseRedirect('admin/change_sc.html')

def emtest_view(request):
    _user = '1970971368@qq.com'
    _pwd  = 'nixplgueixqmcbif'
    _to   =  '1375082244@qq.com'
    msg = MIMEText("Test")
    msg['Subject'] = '这是一个email测试'
    msg['From']    =  _user
    msg['To']      =  _to

    # try:
    s = smtplib.SMTP_SSL('smtp.qq.com',465)
    s.login(_user,_pwd)
    s.sendmail(_user,_to,msg.as_string())
    s.quit()
    return HttpResponse('发送邮件成功')
    # except smtplib.SMTPException,e:
    #     return HttpResponse('发送邮件失败')
          
class IndexView(BaseMixin, ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    queryset = Post.objects.filter(status=1,stype=0,ban =0)  # 只取出状态为“已发布”的文章

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.queryset, display_amount=PERNUM)
        context = super(IndexView, self).get_context_data(**kwargs)
        #************#
        user = self.request.user
        if user.is_authenticated():
            MyRecommend = RecommendList.objects.filter(referee=self.request.user)
            for obj in MyRecommend:
                print(obj.recommend_post, obj.referee)
            context['recommend_list'] = MyRecommend
        #************#
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects

        return context

class NewsView(BaseMixin, ListView):
    template_name = 'blog/news.html'
    context_object_name = 'post_list'
    queryset = Post.objects.filter(status=1,stype=1)  # 只取出状态为“已发布”的文章

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.queryset, display_amount=PERNUM)
        context = super(NewsView, self).get_context_data(**kwargs)
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects

        return context

# 新增

def title_keyword(onvisiting_posts, other_posts_list):
    similar_post_list = {}
    onvisiting_top_words = jieba.analyse.extract_tags(onvisiting_posts.title, topK=4, withWeight=False, allowPOS=('n', 'nr', 'ns', 'nz', 'v'))
    
    # 将文章内容分词，长度大于等于2且对分词结果进行词性统计
    cut = jieba.lcut(onvisiting_posts.title)

    text = ','.join(cut)
    text1 = [(x.word,x.flag) for x in psg.cut(text) if (x.flag.startswith('n') or x.flag.startswith('v'))]
    s1 = len(text1)
    
    begin = time.time()
    postList = other_posts_list.exclude(title=onvisiting_posts.title)
    for post in postList:
        
        cut = jieba.lcut(post.title)

        text = ','.join(cut)

        top_words = jieba.analyse.extract_tags(text, topK=4, withWeight=False, allowPOS=('n', 'nr', 'ns', 'nz', 'v'))
        merged_words = list(set(onvisiting_top_words + top_words))
        text2 = [(x.word,x.flag) for x in psg.cut(text) if x.flag.startswith('n') or x.flag.startswith('v')]
        
        tf_dic1 = {}
        tf_dic2 = {}
        for word in merged_words:
            tf_dic1[word] = 0
            tf_dic2[word] = 0
        # 求出两个词频向量
        s2 = len(text2)
        for i in range(s1):
            if text1[i][0] in merged_words:
                tf_dic1[text1[i][0]] += 1
        for i in range(s2):
            if text2[i][0] in merged_words:
                tf_dic2[text2[i][0]] += 1
        
        dot_product = 0
        tf_dic1_mod = 0
        tf_dic2_mod = 0

        for word in merged_words:
            dot_product += tf_dic1[word] * tf_dic2[word]
            tf_dic1_mod += tf_dic1[word]**2
            tf_dic2_mod += tf_dic2[word]**2
        mod = sqrt(tf_dic1_mod)*sqrt(tf_dic2_mod)
        similar_post_list[post] = dot_product/(mod+1)
    end = time.time()
    print('用时：', end-begin)
    List = sorted(similar_post_list.items(),key = lambda items:items[1],reverse = True)[0:5]
    print(List)
    final_list = []
    s = len(List)
    for i in range(s):
        if List[i][1] > 0.3:
            final_list.append(List[i][0])

    return final_list

# 全局变量，用以存储搜索的关键字
# 后面有这种注释‘#///////////’的为新增内容
global_keyword = ''
global_bolg_title = ''

class PostView(BaseMixin, DetailView):
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    queryset = Post.objects.filter(status=1)

    # 用于记录文章的阅读量，每次请求添加一次阅读量
    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get("pk")
        posts = self.queryset.get(pk=pkey)

        global global_bolg_title#/////////
        global_bolg_title = posts.title#//////
        
        posts.view_count += 1
        posts.save()
        return super(PostView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        pkey = self.kwargs.get("pk")
        user = self.request.user
        #************#
        onvisiting_posts = self.queryset.get(pk=pkey)#///////
        
        other_posts_list = Post.objects.filter(status=1)#///////
        
        similarity_list = title_keyword(onvisiting_posts, other_posts_list)#///////
        #************#
        comment_queryset = self.queryset.get(pk=pkey).comment_set.all().order_by('publish_Time')
        comment_dict = self.handle_comment(comment_queryset)

        if Collection.objects.filter(collect_user=user.id,collect_post=Post.objects.get(id=pkey)):
            iscollected = True
        else:
            iscollected = False
        context['comment_list'] = comment_dict
        context['similarity_list'] = similarity_list#///////
        context['iscollected'] = iscollected
        return context


    def handle_comment(self, queryset):
        comment_dict = OrderedDict()
        root_list = []
        child_list = []
        every_child_list = []
        # 将有根节点的评论和无根节点的评论分开
        for comment in queryset:
            if comment.root_id == 0:
                root_list.append(comment)
            else:
                child_list.append(comment)
        # 将根评论作为键，子评论列表作为值，组合成dict
        for root_comment in root_list:
            for child_comment in child_list:
                if child_comment.root_id == root_comment.id:
                    every_child_list.append(child_comment)
                    # every_child_list.reverse()
            comment_dict[root_comment] = every_child_list
            every_child_list = []
        return comment_dict


class News1View(BaseMixin, DetailView):
    template_name = 'blog/news_detail.html'
    context_object_name = 'post'
    queryset = Post.objects.filter(status=1)

    # 用于记录文章的阅读量，每次请求添加一次阅读量
    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get("pk")
        posts = self.queryset.get(pk=pkey)

    
        
        posts.view_count += 1
        posts.save()
        return super(News1View, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(News1View, self).get_context_data(**kwargs)
        pkey = self.kwargs.get("pk")
        user = self.request.user
        #************#
        onvisiting_posts = self.queryset.get(pk=pkey)#///////
        
        other_posts_list = Post.objects.filter(status=1)#///////
        
        
        comment_queryset = self.queryset.get(pk=pkey).comment_set.all().order_by('publish_Time')
        comment_dict = self.handle_comment(comment_queryset)

        if Collection.objects.filter(collect_user=user.id,collect_post=Post.objects.get(id=pkey)):
            iscollected = True
        else:
            iscollected = False
        context['comment_list'] = comment_dict
   
        context['iscollected'] = iscollected
        return context


    def handle_comment(self, queryset):
        comment_dict = OrderedDict()
        root_list = []
        child_list = []
        every_child_list = []
        # 将有根节点的评论和无根节点的评论分开
        for comment in queryset:
            if comment.root_id == 0:
                root_list.append(comment)
            else:
                child_list.append(comment)
        # 将根评论作为键，子评论列表作为值，组合成dict
        for root_comment in root_list:
            for child_comment in child_list:
                if child_comment.root_id == root_comment.id:
                    every_child_list.append(child_comment)
                    # every_child_list.reverse()
            comment_dict[root_comment] = every_child_list
            every_child_list = []
        return comment_dict
#******
class RecommendView(View):

    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get('pk')
        post = Post.objects.get(id=pkey)
        ur = self.request.user
        if ur.is_authenticated():
            obj = RecommendList.objects.filter(referee=ur,recommend_post=post)
            if obj: 
                return HttpResponseRedirect('/')
            else:
                post.recommend_count += 1
                RecommendList.objects.create(referee=ur,recommend_post=post)
                print(post.recommend_count)
                post.save()
                return HttpResponseRedirect('/')
        else:
            return redirect('/admin/login')
#*********

class CommentView(View):
    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        # 获取评论
        comment = self.request.POST.get("comment", "")
        root_id = self.request.POST.get("root_id", 0)
        parent_id = self.request.POST.get("parent_id", 0)

        # 判断当前用户是否是活动的用户
        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
        if not comment:
            return HttpResponse(u"请输入评论", status=403)
        if len(comment) > 200:
            return HttpResponse(u"评论过长，请重新输入", status=403)

        # 获取用户IP地址
        if "HTTP_X_FORWARDED_FOR" in request.META.keys():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        # 处理comment中的@事件
        comment = self.handle_at_str(comment)
        # 处理comment中的emoji表情，只有root_id为0的评论才会有表情
        if root_id == 0:
            comment = self.handle_emoji_str(comment)

        pkey = self.kwargs.get("pk", "")
        post_foreignkey = Post.objects.get(pk=pkey)

        comment = Comment.objects.create(
            post=post_foreignkey,
            author=user,
            content=comment,
            ip_address=ip,
            root_id=root_id,
            parent_id=parent_id,
        )

        result_dict = {'post_id': post_foreignkey.id,
                       'csrf_token': request.COOKIES["csrftoken"],
                       'user_avatar': str(user.avatar_path),
                       'user_id': user.id,
                       'author_id': comment.author.id,
                       'comment_id': comment.id,
                       'comment_author': comment.author.name,
                       'comment_publish_time': comment.publish_Time.strftime("%Y年%m月%d日 %H:%M"),
                       'comment_content': comment.content}

        return HttpResponse(json.dumps(result_dict))

    def handle_at_str(self, str):
        pattern = re.compile('@\S+ ')
        result = pattern.findall(str)
        for string in result:
            handler_str = '<a>' + string + '</a>'
            str = re.sub(string, handler_str, str)
        return str

    def handle_emoji_str(self, str):
        keys = ':(add1|-1|airplane|alarm_clock|alien|angel|angry|anguished|art|astonished|basketball|beers|bicyclist|birthday|blush|broken_heart|cat|chicken|clap|confounded|confused|cow|cry|disappointed|dizzy_face|dog|expressionless|fearful|flushed|frowning|full_moon_with_face|ghost|grimacing|grin|grinning|heart_eyes|high_brightness|hushed|innocent|joy|kissing_heart|laughing|mask|neutral_face|new_moon_with_face|pencil2|persevere|person_frowning|person_with_blond_hair|relaxed|relieved|satisfied|scream|sleeping|smile|smirk|sob|stuck_out_tongue_winking_eye|sunglasses|sweat|tired_face|triumph|tulip|u7981|unamused|unlock|v|weary|wink|worried|yum|zzz):'
        pattern = re.compile(keys)
        result = pattern.findall(str)
        for string in result:
            key = string
            # key = result[1:-1]
            url = '/static/jquery-emojiarea/packs/basic/emojis'
            extension = '.png'
            src = url + '/' + key + extension
            handler_str = '<img class="emoji" width="20" height="20" align="absmiddle" src="' + src + '"/>'
            str = re.sub(':'+string+':', handler_str, str)
        return str


class CommentDeleteView(View):
    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        # 判断当前用户是否是活动的用户
        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)

        pkey = self.kwargs.get("pk", "")
        comment = Comment.objects.filter(author_id=user.id).get(pk=pkey)

        # 如果root_id为0，代表为父评论，获取父评论的所有子评论
        if comment.root_id == 0:
            children_comment_set = Comment.objects.filter(root_id=comment.id)
            children_comment_set.delete()

        # 返回当前评论
        result = {'comment_id': comment.id}
        comment.delete()

        return HttpResponse(json.dumps(result))


class RepositoryView(BaseMixin, ListView):
    template_name = 'blog/repository.html'
    context_object_name = 'repository_list'
    queryset = Repository.objects.all()

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.queryset, display_amount=PERNUM)
        context = super(RepositoryView, self).get_context_data(**kwargs)
        context['page_range'] = page_range
        context['objects'] = objects
        return context


class RepositoryDetailView(BaseMixin, DetailView):
    template_name = 'blog/repository_detail.html'
    context_object_name = 'repository'
    queryset = Repository.objects.all()

    # 用于记录文章的阅读量，每次请求添加一次阅读量
    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get("pk")
        repositorys = self.queryset.get(pk=pkey)
        repositorys.view_count += 1
        repositorys.save()
        return super(RepositoryDetailView, self).get(request, *args, **kwargs)


class TagListView(BaseMixin, ListView):
    template_name = template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        slug_key = self.kwargs.get("slug")
        post_list = TaggedItem.objects.get_by_model(Post, slug_key)
        return post_list

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.get_queryset(), display_amount=PERNUM)
        context = super(TagListView, self).get_context_data(**kwargs)
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects
        return context


class CatalogueListView(BaseMixin, ListView):
    template_name = template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        slug_key = self.kwargs.get("slug")
        catalogue_key = Catalogue.objects.get(id=slug_key)
        post_list = Post.objects.filter(catalogue_id=catalogue_key, stype =0, status =1)
        return post_list

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.get_queryset(), display_amount=PERNUM)
        context = super(CatalogueListView, self).get_context_data(**kwargs)
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects
        return context


class AuthorPostListView(BaseMixin, ListView):
    template_name = template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        pkey = self.kwargs.get("pk")
        user = User.objects.get(pk=pkey)
        post_list = Post.objects.filter(author_id=user).filter(status=1)
        return post_list

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.get_queryset(), display_amount=PERNUM)
        context = super(AuthorPostListView, self).get_context_data(**kwargs)
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects
        return context
class AuthorNewsListView(BaseMixin, ListView):
    template_name = template_name = 'blog/news.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        pkey = self.kwargs.get("pk")
        user = User.objects.get(pk=pkey)
        post_list = Post.objects.filter(author_id=user).filter(status=1,stype=1)
        return post_list

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.get_queryset(), display_amount=PERNUM)
        context = super(AuthorNewsListView, self).get_context_data(**kwargs)
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects
        return context

class CategoryListView(BaseMixin, ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        pkey = self.kwargs.get("pk")
        catalogue_key = Catalogue.objects.filter(catename = Maincategory.objects.get(id=pkey))
        post_list = Post.objects.filter(catalogue=catalogue_key,stype = 0,status =1)
        return post_list

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.get_queryset(), display_amount=PERNUM)
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects
        return context

class CollectView(View):
    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        pkey = self.kwargs.get("pk")
        p = Post.objects.get(id=pkey)

        if Collection.objects.filter(collect_user=user,collect_post=p):
            Collection.objects.get(collect_user=user,collect_post=p).delete()
        else:
            Collection.objects.create(collect_user=user,collect_post=p)

        return HttpResponseRedirect('/post/'+str(pkey))

# 新增
pageviews = ''
date = ''

class SearchView(BaseMixin, ListView):

    template_name = 'blog/show_search.html'
    context_object_name = 'post_list'

    def get_queryset(self):
            # 搜索浏览量为default_view_count的文章，默认为0，表示全部文章
            default_view_count = 0
            
            new_k = self.kwargs.get('pk')
            if new_k in ['0','10','30','50']:
                global pageviews
                pageviews = new_k
            if new_k in ['all', 'oneweek', 'onemonth', 'oneyear']:
                global date
                date = new_k
            # 获取关键字
            keyword = self.request.GET.get("search_in_website")

            global global_keyword
            # 如果new_k不在所给的限制条件里，表示默认显示全部，否则将new_k赋值给default_k
            if keyword == None:
                if (pageviews in ['0','10','30','50']) and (date in ['all', 'oneweek', 'onemonth', 'oneyear']):
                    default_view_count = pageviews
                    if date == 'all':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=100000)
                    if date == 'oneweek':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=1)
                    if date == 'onemonth':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=3)
                    if date == 'oneyear':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=5)
                    post_list = Post.objects.filter(status=1, \
                    title__contains=global_keyword, view_count__gte=default_view_count, publish_time__gte=back_time).order_by('-publish_time')
                elif pageviews in ['0','10','30','50']:
                    default_view_count = pageviews
                    post_list = Post.objects.filter(status=1, \
                    title__contains=global_keyword, view_count__gte=default_view_count).order_by('-publish_time')
                elif date in ['all', 'oneweek', 'onemonth', 'oneyear']:
                    if date == 'all':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=100000)
                    if date == 'oneweek':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=1)
                    if date == 'onemonth':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=3)
                    if date == 'oneyear':
                        back_time = datetime.datetime.now() - datetime.timedelta(days=5)
                    post_list = Post.objects.filter(status=1, \
                    title__contains=global_keyword, publish_time__gte=back_time).order_by('-publish_time')
            else:
                global_keyword = keyword
                post_list = Post.objects.filter(status=1, \
                    title__contains=global_keyword, view_count__gte=default_view_count).order_by('-publish_time')
            return post_list

    def get_context_data(self, **kwargs):
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(
            pages=page, queryset=self.get_queryset(), display_amount=PERNUM)
        context = super(SearchView, self).get_context_data(**kwargs)
        context['carousel_page_list'] = Carousel.objects.all()
        context['page_range'] = page_range
        context['objects'] = objects
        return context

# 123456
class UserForm(forms.Form):
    username = forms.CharField(label='用户名',)
    password = forms.CharField(label='密码',widget=forms.PasswordInput())
    nickname = forms.CharField(label='昵称')
    email = forms.EmailField(label='邮箱')


class newForm(forms.Form):
    code = forms.CharField(label = '验证码')

global randCode
randCode = ""
global userData
userData = {}


def register_views(request):
    if request.method == "POST":
        userform = UserForm(request.POST)
        print(userform)
        # form = CustomUserCreationForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            nickname = userform.cleaned_data['nickname']
            email = userform.cleaned_data['email']
            error_context = {}
            if User.objects.filter(username=username):
                # request.session['error_message'] = '此帐号已经被注册!'
                error_context['name'] = "此帐号已经被注册!"
                return render(request, 'blog/register.html',error_context)
            if User.objects.filter(email=email):
                # request.session['error_message'] = '此帐号已经被注册!'
                error_context['email'] = "此邮箱已经被注册!"
                return render(request, 'blog/register.html',error_context)
            if User.objects.filter(name=nickname):
                # request.session['error_message'] = '此帐号已经被注册!'
                error_context['nickname'] = "此昵称已经被使用!"
                return render(request, 'blog/register.html',error_context)


            global userData
            userData['username'] = username
            userData['password'] = password
            userData['email'] = email
            userData['nickname'] = nickname
            # user = User.objects.create_user(
            #     username=username,
            #     password=password,
            #     email=email,)
            # user.name = username
            # mail_host = "smtp.163.com"      # SMTP服务器
            # mail_user = "m18821701190@163.com"                  # 用户名
            # mail_pass = "ldy654321"               # 授权密码，非登录密码
            _user = settings.EMAIL_HOST_USER1
            _pwd  = settings.EMAIL_HOST_PASSWORD1
            _to   =  email

            # sender = 'm18821701190@163.com'    # 发件人邮箱(最好写全, 不然会失败)
            # regemail = request.POST['email']
            # receivers = [regemail]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
            # uname= request.POST['username']

            from random import sample
            str = ''.join(sample('AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789', 6))
            # str2 = str
            # msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<img alt="" src="cid:image1" />good!', 'html', 'utf-8')
            # msg.attach(msgText)
            # file1 = "/home/tarena/www/zer0Blog/yemian.png"
            # image = MIMEImage(open(file1, 'rb').read())
            # image.add_header('Content-ID', '<image1>')
            # import mimetypes
            # message.attach(image)

            content = '<i>你好!</i>'+str
            global randCode
            uname = username
            randCode = str
            title = '欢迎注册技术之心博客用户'  # 邮件主题
            # message = MIMEText(content, 'html', 'utf-8')  # 内容, 格式, 编码
            # message['From'] = "{}".format(sender)
            # message['To'] = ",".join(receivers)
            # message['Subject'] = title
            
            msg = MIMEText('您好,欢迎注册技术之心博客用户，您的帐号为：'+uname+'您的验证码       '+str,'plain','utf-8')
            subject = '技术之心处理结果'
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From']    =  _user
            msg['To']      =  _to
       
        # s = smtplib.SMTP_SSL('smtp.163.com',465)
            s = smtplib.SMTP_SSL('smtp.qq.com',465)
            s.login(_user,_pwd) 
            s.sendmail(_user,_to,msg.as_string())
       
       
            s.quit()
            # try:
            #     smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
            #     print("1")
            #     smtpObj.login(mail_user, mail_pass)  # 登录验证
            #     print("2")
            #     smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
            #     print("3")
            #     print("mail has been send successfully.")
            # except smtplib.SMTPException as e:
            #     print(e)


            # email_client.quit()
            # if __name__ == '__main__':
            # sendEmail()
            # user.is_active = 1
            # user.is_staff = 1
            # user.save()
            
            return redirect('/tiaozhuan')
            

    else:
        userform = UserForm()
    return render(request, 'blog/register.html',{'userform':userform})

def ceshi(request):
    print(1)
    if request.method == "POST":
        print(2)
        userform = newForm(request.POST)
        print(userform)
        # form = CustomUserCreationForm(request.POST)
        if userform.is_valid():
            print(3)
            verycode = userform.cleaned_data['code']
            global randCode
            if randCode == verycode:
                global userData
                user = User.objects.create_user(
                    username=userData['username'],
                    password=userData['password'],
                    email=userData['email'],
                    name=userData['nickname']
                    )
                infor = "Success!"
                user.is_active = 1
                user.is_staff = 1
                user.save()
                sv = User.objects.get(username = userData['username'])
                se = Secret.objects.create(
                    s_user_id = sv.id                    
                    )
                se.save()
                return render(request,"blog/yzSuccess.html")
            else:
                infor = "Fail!"
                return HttpResponse("失败!")
        else:
            print(4)
    else:
        userform = newForm()
    return render(request, 'blog/tiaozhuan.html',{'userform':userform})
    # def new_views(request):
    # return render(request, 'blog/111.html')

def show_Agreement(request):
    return render(request,'blog/user_Agreement.html')
def show_aboutUs(request):
    return render(request,'blog/showUs.html')
def contact_us(request):
    return render(request,'blog/contact.html')
class HistoryView(BaseMixin, ListView):

    template_name = 'blog/history.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        pkey = self.kwargs.get('pk')
        post_list = Post.objects.filter(status=1,stype=0,author_id=pkey)
        return post_list


    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = objects
        return context
