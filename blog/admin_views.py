# -*- coding:utf-8 -*-
from __future__ import division
import datetime
import json
import os
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.template.response import TemplateResponse
from django.views.generic import View, ListView, CreateView, UpdateView
from django.http import HttpResponse, HttpResponseRedirect
from heartoftech.settings import MEDIA_ROOT, MEDIA_URL, image_type

from heartoftech.settings import PERNUM
from blog.pagination import paginator_tool
from .models import Post, Catalogue, Carousel, User, EDITOR,Secret,UReport,Maincategory, Collection,Comment
from django.shortcuts import render
from django.db.models import Q
from PIL import Image 
import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from email.header import Header
import random
from django.contrib.auth.hashers import make_password, check_password
@csrf_exempt
# def change_view(request):
#    return render(request,'admin/change_sc.html',locals())
def markdown_image_upload_handler(request):
    # 要返回的数据字典，组装好后，序列化为json格式
    if request.method == "POST":
        result = {}
        try:
            file_img = request.FILES['editormd-image-file']
            file_suffix = os.path.splitext(file_img.name)[len(os.path.splitext(file_img.name)) - 1]
            filename = uuid.uuid1().__str__() + file_suffix

            # 检查图片格式
            if file_suffix not in image_type:
                result['success'] = 0
                result['message'] = "上传失败，图片格式不正确"
            else:
                path = MEDIA_ROOT + "/post/"
                if not os.path.exists(path):
                    os.makedirs(path)

                # 图片宽大于825的时候，将其压缩到824px，刚好适合13吋pc的大小
                img = Image.open(file_img)
                width, height = img.size
                
                file_name = path + filename
                img.save(file_name)

                file_img_url = "http://" + request.META['HTTP_HOST'] + MEDIA_URL + "post/" + filename

                result['success'] = 1
                result['message'] = "上传成功"
                result['url'] = file_img_url

        except Exception:
            result['success'] = 0
            result['message'] = "gfhfgh"

        return HttpResponse(json.dumps(result))


@csrf_exempt
def tinymce_image_upload_handler(request):
    if request.method == "POST":
        try:
            file_img = request.FILES['tinymce-image-file']
            file_suffix = os.path.splitext(file_img.name)[len(os.path.splitext(file_img.name)) - 1]
            # 检查图片格式
            if file_suffix not in image_type:
                return HttpResponse("请上传正确格式的图片文件")
            filename = uuid.uuid1().__str__() + file_suffix

            # 图片宽大于824的时候，将其压缩到824px，刚好适合13吋pc的大小
            img = Image.open(file_img)
            width, height = img.size
            
            path = MEDIA_ROOT + "/post/"
            if not os.path.exists(path):
                os.makedirs(path)

            file_name = path + filename
            img.save(file_name)

            file_img_url = "http://" + request.META['HTTP_HOST'] + MEDIA_URL + "post/" + filename

            context = {
                'result': "file_uploaded",
                'resultcode': "ok",
                'file_name': file_img_url
            }

        except Exception:
            context = {
                'result': "fhghgfh",
                'resultcode': "failed",
            }

        return TemplateResponse(request, "admin/plugin/ajax_upload_result.html", context)


def avatar_image_upload_handler(request):
    if request.method == "POST":
        try:
            file_img = request.FILES['avatar']
            file_suffix = os.path.splitext(file_img.name)[len(os.path.splitext(file_img.name)) - 1]
            # 检查图片格式
            if file_suffix not in image_type:
                return HttpResponse("请上传正确格式的图片文件")
            filename = uuid.uuid1().__str__() + file_suffix

            # 把头像压缩成90大小
            img = Image.open(file_img)
            
            path = MEDIA_ROOT + "/avatar/"
            if not os.path.exists(path):
                os.makedirs(path)

            file_name = path + filename
            img.save(file_name)

            file_img_url = "http://" + request.META['HTTP_HOST'] + MEDIA_URL + "avatar/" + filename
            user = request.user
            user.avatar_path = file_img_url
            user.save()

        except Exception:
            pass

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', "/"))


class PostView(ListView):
    template_name = 'admin/blog_admin.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        user = self.request.user
        post_list = Post.objects.filter(author_id=user.id,stype=0,ban=0).exclude(status=2)
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = objects
        context['editor_list'] = EDITOR
        return context
class CPost(ListView):
    template_name = 'admin/cblog_admin.html'
    user_list = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        post_list = Post.objects.filter(stype=0).exclude(status=2)
        return post_list
    # def get_context_data(self, **kwargs):
    #     user_list = User.objects.all()
    #     user = self.request.user
    #     post_list = Post.objects.filter(stype=0).exclude(status=2)
    #     context = post_list.get_context_data(**kwargs)
    #     # context = super(CPost, self).get_context_data(**kwargs)
    #     page = self.kwargs.get('page') or self.request.GET.get('page') or 1
    #     objects, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
    #     context['page_range'] = page_range
    #     context['objects'] = objects
    #     context['editor_list'] = EDITOR
    #     return context
def CPost_view(request):   
    scna = request.GET.get('s')
    post_list = Post.objects.filter(stype=0).exclude(status=2)
    if scna == None:
      user_list = User.objects.all()
    else:
        user_list = User.objects.filter(Q(name__contains = scna)|Q( username = scna) )
    return render(request,'admin/cblog_admin.html',locals())
class NewsView(ListView):
    template_name = 'admin/news_admin.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        user = self.request.user
        post_list = Post.objects.filter(author_id=user.id,stype=1).exclude(status=2)
        return post_list

    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = objects
        context['editor_list'] = EDITOR
        return context

class DeletePost(View):
    def get(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        # 判断当前用户是否是活动的用户
        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
        # 获取删除的博客ID
        pkey = self.kwargs.get('pk')
        post1 = Post.objects.get(pk=pkey)
        col = Collection.objects.filter(collect_post_id=pkey)
        if col:
           col[0].delete()
        comm = Comment.objects.filter(post=post1)
        if comm:
           comm[0].delete()
        post1.status = 2
        post1.save()
        return HttpResponseRedirect('/admin/')
class DeletePost2(View):
    def get(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        # 判断当前用户是否是活动的用户
        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
        # 获取删除的博客ID
        pkey = self.kwargs.get('pk')
        post1 = Post.objects.get(pk=pkey)
        col = Collection.objects.filter(collect_post_id=pkey)
        if col:
           col[0].delete()
        comm = Comment.objects.filter(post=post1)
        if comm:
           comm[0].delete()
        post1.status = 2
        post1.save()
        return HttpResponseRedirect('/admin/newsl')
class DeletePost1(View):
    def get(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        # 判断当前用户是否是活动的用户
        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
        # 获取删除的博客ID
        pkey = self.kwargs.get('pk')
        post1 = Post.objects.get(pk=pkey)
        col = Collection.objects.filter(collect_post_id=pkey)
        if col:
           col[0].delete()
        comm = Comment.objects.filter(post=post1)
        if comm:
           comm[0].delete()
        post1.status = 2
        post1.save()
        return HttpResponseRedirect('/admin/cblog')
class DeleteReport(View):
    def get(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        # 判断当前用户是否是活动的用户
        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
        # 获取删除的博客ID
        pkey = self.kwargs.get('pk')
        report = UReport.objects.get(pk=pkey)
        report.delete()
        report.save()
        return HttpResponseRedirect('/admin/creport')


class BanPost(View):
    def get(self, request, *args, **kwargs):
        # 获取当前用户
        user = self.request.user
        # 判断当前用户是否是活动的用户
        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
        # 获取删除的博客ID
        pkey = self.kwargs.get('pk')
        post = Post.objects.get(pk=pkey)
        # _user = '1970971368@qq.com'
        # _pwd  = 'nixplgueixqmcbif'
        _user = settings.EMAIL_HOST_USER1
        _pwd  = settings.EMAIL_HOST_PASSWORD1
        _to   =  post.author.email
       
       
       
    
    # try:
       
    # return HttpResponse('发送邮件成功')
    # except smtplib.SMTPException,e:
        if post.ban == 1:
             post.ban = 0

             msg = MIMEText('您的博文《'+post.title+'》已被管理员解除封禁','plain','utf-8')
            
        else:
             post.ban = 1
             msg = MIMEText('您的博文《'+post.title+'》因为违反用户协议已被管理员解除封禁','plain','utf-8')
        post.save()
       
        subject = '技术之心处理结果'
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From']    =  _user
        msg['To']      =  _to
       
        # s = smtplib.SMTP_SSL('smtp.163.com',465)
        s = smtplib.SMTP_SSL('smtp.qq.com',465)
        s.login(_user,_pwd) 
        s.sendmail(_user,_to,msg.as_string())
       
       
        s.quit()
        return HttpResponseRedirect('/admin/cblog')
class BanUser(View):
    """docstring for BanUser"""
    def get(self,request,*args,**kwargs):
        user = self.request.user

        if not user.is_authenticated():
            return HttpResponse(u"请登录! ",status=403)
        pkey = self.kwargs.get('pk')
        users = User.objects.get(pk=pkey)
        _user = settings.EMAIL_HOST_USER1
        _pwd  = settings.EMAIL_HOST_PASSWORD1
        _to   =  users.email
        print (3)
        if users.is_active == 1 :
             users.is_active = 0
             msg = MIMEText('用户'+users.username+'因违反用户协议已被管理员封禁','plain', 'utf-8')
        else:
             users.is_active = 1
             msg = MIMEText('用户'+users.username+'解除封禁','plain', 'utf-8')
        users.save()
        print (2) 
        subject = '技术之心处理结果'
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From']    =  _user
        msg['To']      =  _to
        print (1)
        # s = smtplib.SMTP_SSL('smtp.163.com',465)
        s = smtplib.SMTP_SSL('smtp.qq.com',465)
        s.login(_user,_pwd)
        s.sendmail(_user,_to,msg.as_string())
        s.quit()
        return HttpResponseRedirect('/admin/userset')

        
class NewPost(CreateView):
    template_name = 'admin/post_new.html'
    model = Post
    fields = ['title']

    def get_context_data(self, **kwargs):
        context = super(NewPost, self).get_context_data(**kwargs)
        context['catalogue_list'] = Catalogue.objects.all()
        context['maincategeory_list']  = Maincategory.objects.all()
        return context
class NewNews(CreateView):
    template_name = 'admin/news_new.html'
    model = Post
    fields = ['title']

    def get_context_data(self, **kwargs):
        context = super(NewNews, self).get_context_data(**kwargs)
        context['catalogue_list'] = Catalogue.objects.all()
        context['maincategeory_list']  = Maincategory.objects.all()
        return context


class UpdatePostIndexView(UpdateView):
    template_name = 'admin/post_new.html'
    model = Post
    fields = ['title']

    def get_context_data(self, **kwargs):
        context = super(UpdatePostIndexView, self).get_context_data(**kwargs)
        context['catalogue_list'] = Catalogue.objects.all()
        context['maincategeory_list']  = Maincategory.objects.all()
        return context
# def change_view(request):
#    return render(request,'admin/change_sc.html',locals())
def backpwdone_view(request):
     uid = request.POST.get('uid')
     st = Secret.objects.filter(id = uid)
     sf =st[0]
     fre = request.POST.get('fre')
     sre = request.POST.get('sre')
     tre = request.POST.get('tre')
     if sf.f_result == fre and sf.s_result == sre and sf.t_result == tre :
        _user = settings.EMAIL_HOST_USER1
        _pwd  = settings.EMAIL_HOST_PASSWORD1
        swv = User.objects.filter(id = sf.s_user_id)
        su = swv[0]
        _to   = su.email   
        pw = ''.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a'], 8))
        sha_pwd = make_password(pw, None, 'pbkdf2_sha256')
        su.password= sha_pwd
        msg = MIMEText('您的账户密码《'+pw+'》','plain','utf-8')
        su.save()
        subject = '技术之心处理结果'
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From']    =  _user
        msg['To']      =  _to
        s = smtplib.SMTP_SSL('smtp.qq.com',465)
        s.login(_user,_pwd) 
        s.sendmail(_user,_to,msg.as_string())
        s.quit()
     else :
        return render(request,'admin/error.html',locals())
     return render(request,'admin/success.html',locals())

def backpwd_view(request):
    uid = request.POST.get('username')
    if not uid :
        sname = User.objects.all()
        return render(request,'admin/bkpwd.html',locals())
    else:    
        se = User.objects.filter(username = uid)
        if not se:
            sname = User.objects.all()
            # return HttpResponse('未设置密保无法通过此方法找回')
            return render(request,'admin/bkpwd.html',locals())
        sv = se[0]
        st = Secret.objects.filter(s_user=sv.id)
        sf = st[0]
        if not sf.f_question:
            return HttpResponse('未设置密保无法通过此方法找回')
        else:
            print(sf.f_question)
            return render(request,'admin/bkpwdone.html',locals())
def change_view(request):
        user = request.user
        print(user)
        se   = Secret.objects.filter(s_user=user)
        sv = se[0]
        # print (se[0].f_question)
        return render(request,'admin/change_sc.html',locals())
def changedo_view(request):  
        user = request.user
        question1 = request.POST.get('qv1')
        question2 = request.POST.get('qv2')
        question3 = request.POST.get('qv3')
        result1 = request.POST.get("uv1")
        result2 = request.POST.get("uv2")
        result3 = request.POST.get("uv3")   
        se   = Secret.objects.filter(s_user=user.id)
        sv = se[0]
        sv.f_result = result1
        sv.s_result = result2
        sv.t_result = result3
        sv.f_question = question1
        sv.s_question = question2
        sv.t_question = question3
        sv.save()
        return render(request,'admin/change_sc_done.html',locals())
class AddPost(View):
    def post(self, request):
        # 获取当前用户
        user = request.user
        # 获取评论
        title = request.POST.get("title", "")
        content = request.POST.get("content", "")
        catalogue = request.POST.get("catalogue", "")
        tags = request.POST.getlist("tag", "")
        action = request.POST.get("action", "0")

        maincate = Maincategory.objects.get(id=request.POST.get("maincate",""))
        catalogue_foreignkey = Catalogue.objects.get(name=catalogue,catename=maincate)
        editor_choice = user.editor_choice

        post_obj = Post.objects.create(
            title=title,
            author=user,
            content=content,
            catalogue=catalogue_foreignkey,
            status=action,
            editor_choice=editor_choice,
            stype = 0,
            ban = 0,
        )

        post_obj.update_tags(tags)

        return HttpResponseRedirect('/admin/')
class AddNews(View):
    def post(self, request):
        # 获取当前用户
        user = request.user
        # 获取评论
        title = request.POST.get("title", "")
        content = request.POST.get("content", "")
        catalogue = request.POST.get("catalogue", "")
        tags = request.POST.getlist("tag", "")
        action = request.POST.get("action", "0")

        maincate = Maincategory.objects.get(id=request.POST.get("maincate",""))
        catalogue_foreignkey = Catalogue.objects.get(name=catalogue,catename=maincate)
        editor_choice = user.editor_choice

        post_obj = Post.objects.create(
            title=title,
            author=user,
            content=content,
            catalogue=catalogue_foreignkey,
            status=action,
            editor_choice=editor_choice,
            stype = 1,
            ban = 0,
        )

        post_obj.update_tags(tags)

        return HttpResponseRedirect('/admin/newsl')



class UpdateDraft(View):
    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user = request.user
        # 获取要修改的博客
        pkey = self.kwargs.get('pk')
        post = Post.objects.filter(author_id=user.id).get(pk=pkey)
        # 获取评论
        title = request.POST.get("title", "")
        content = request.POST.get("content", "")
        catalogue = request.POST.get("catalogue", "")
        tags = request.POST.getlist("tag", "")
        action = request.POST.get("action", "0")

        maincate = Maincategory.objects.get(id=request.POST.get("maincate",""))
        catalogue_foreignkey = Catalogue.objects.get(name=catalogue,catename=maincate)

        post.title = title
        post.content = content
        post.catalogue = catalogue_foreignkey
        post.status = action
        post.modify_time = datetime.datetime.now()
        post.save()

        post.update_tags(tags)

        return HttpResponseRedirect('/admin/')


class UpdatePost(View):
    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user = request.user
        # 获取要修改的博客
        pkey = self.kwargs.get('pk')
        post = Post.objects.filter(author_id=user.id).get(pk=pkey)
        # 获取评论
        title = request.POST.get("title", "")
        content = request.POST.get("content", "")
        catalogue = request.POST.get("catalogue", "")
        tags = request.POST.getlist("tag", "")
        action = 1

        maincate = Maincategory.objects.get(id=request.POST.get("maincate",""))
        catalogue_foreignkey = Catalogue.objects.get(name=catalogue,catename=maincate)

        post.title = title
        post.content = content
        post.catalogue = catalogue_foreignkey
        post.status = action
        post.modify_time = datetime.datetime.now()
        post.save()

        post.update_tags(tags)

        return HttpResponseRedirect('/admin/')


class UpdateEditor(View):
    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user = request.user

        if not user.is_authenticated():
            return HttpResponse(u"请登陆！", status=403)
        # 获取编辑器
        editor = request.POST.get("editor", "")
        user.editor_choice = editor
        user.save()

        return HttpResponseRedirect('/admin/')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib.auth.views import logout
        return logout(request, next_page='/')


class CarouselIndexView(ListView):
    template_name = 'admin/carousel_admin.html'
    context_object_name = 'carousel_list'
    queryset = Carousel.objects.all()


class CarouselEditView(CreateView):
    template_name = 'admin/carousel_new.html'
    model = Carousel
    fields = ['title']

    def get_context_data(self, **kwargs):
        context = super(CarouselEditView, self).get_context_data(**kwargs)
        context['post_list'] = Post.objects.filter(status=1)
        return context


class AddCarousel(View):
    def post(self, request, *args, **kwargs):

        # 将文件路径和其余信息存入数据库
        title = request.POST.get("title", "")
        post = request.POST.get("post", "")
        post_foreignkey = Post.objects.get(pk=post)
        image_link = request.POST.get("image_link", "")

        if not image_link:
            filename = ""
            try:
                file_img = request.FILES['files']
                file_suffix = os.path.splitext(file_img.name)[len(os.path.splitext(file_img.name)) - 1]
                filename = uuid.uuid1().__str__() + file_suffix

                # 把过大的图像压缩成合适的轮播图大小
                img = Image.open(file_img)
               
                path = MEDIA_ROOT + "/carousel/"
                if not os.path.exists(path):
                    os.makedirs(path)

                file_name = path + filename
                img.save(file_name)
            except Exception:
                pass
            file_img_url = "http://" + request.META['HTTP_HOST'] + MEDIA_URL + "carousel/" + filename
            Carousel.objects.create(
                title=title,
                post=post_foreignkey,
                img=file_img_url,
            )
        else:
            Carousel.objects.create(
                title=title,
                post=post_foreignkey,
                img=image_link,
            )
        return HttpResponseRedirect('/admin/carousel')


class DeleteCarousel(View):
    def get(self, request, *args, **kwargs):
        # 获取删除的博客ID
        pkey = self.kwargs.get('pk')
        carousel = Carousel.objects.get(id=pkey)
        carousel.delete()
        return HttpResponseRedirect('/admin/carousel')


class CarouselUpdateView(UpdateView):
    template_name = 'admin/carousel_update.html'
    model = Carousel
    fields = ['title']

    def get_context_data(self, **kwargs):
        context = super(CarouselUpdateView, self).get_context_data(**kwargs)
        context['post_list'] = Post.objects.all()
        return context


class UpdateCarousel(View):
    def post(self, request, *args, **kwargs):

        # 将文件路径和其余信息存入数据库
        title = request.POST.get("title", "")
        post = request.POST.get("post", "")
        post_foreignkey = Post.objects.get(pk=post)
        image_link = request.POST.get("image_link", "")

        pkey = self.kwargs.get('pk')
        carousel = Carousel.objects.get(id=pkey)

        if not image_link:
            try:
                file_img = request.FILES['files']
                file_suffix = os.path.splitext(file_img.name)[len(os.path.splitext(file_img.name)) - 1]
                filename = uuid.uuid1().__str__() + file_suffix

                # 把过大的图像压缩成合适的轮播图大小
                img = Image.open(file_img)
                
                path = MEDIA_ROOT + "/carousel/"
                if not os.path.exists(path):
                    os.makedirs(path)

                file_name = path + filename
                img.save(file_name)
            except Exception:
                pass
            file_img_url = "http://" + request.META['HTTP_HOST'] + MEDIA_URL + "carousel/" + filename

            carousel.title = title
            carousel.post = post_foreignkey
            carousel.img = file_img_url
            carousel.save()

        else:
            carousel.title = title
            carousel.post = post_foreignkey
            carousel.img = image_link
            carousel.save()
        return HttpResponseRedirect('/admin/carousel')


class UserSetView(ListView):
    template_name = 'admin/userset_admin.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        user_list = User.objects.all()
        # sv = request.GET.get('s')
        return user_list

    def get_context_data(self, **kwargs):
        context = super(UserSetView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = objects
        return context


class NewUserView(CreateView):
    template_name = 'admin/userset_new.html'
    model = User
    fields = ['username']


class AddUser(View):
    def post(self, request):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        name = request.POST.get("name", "")
        email = request.POST.getlist("email", "")

        user_obj = User.objects.create_user(
            username="".join(username),
            password="".join(password),
            email="".join(email),
        )

        user_obj.name = name
        user_obj.is_superuser = 0
        user_obj.is_staff = 1

        user_obj.save()

        return HttpResponseRedirect('/admin/userset')
class Creport(ListView):     
    template_name = 'admin/creport_admin.html'
    context_object_name = 'report_list'

    def get_queryset(self):
        user = self.request.user
        report_list = UReport.objects.all().order_by("-report_time")
        return report_list

    def get_context_data(self, **kwargs):
        context = super(Creport, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = objects
        return context
#类型展示的视图
class TypeView(ListView):
    template_name = 'admin/typemanage.html'
    context_object_name = 'Maincategory_list'

    #获取需要展示的数据并且返回（必须）
    def get_queryset(self):
        Maincategory_list = Maincategory.objects.all()
        return Maincategory_list

    #传递额外的数据到模板
    def get_context_data(self, **kwargs):
        context = super(TypeView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        objects, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = objects
        return context
#接受表单
class NewTypeView(CreateView):
    template_name = 'admin/type_new.html'
    model = Maincategory
    fields = ['name']

#添加分类数据到数据库
class AddTypeView(View):
    def post(self,request):
        maincategoryname = request.POST.get("blogtype","")
        Maincategory.objects.create(name = maincategoryname)

        return HttpResponseRedirect('/admin/typemanage')

#删除分类
class DelTypeView(View):
    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get('pk')
        cate = Maincategory.objects.get(name=pkey)
        catalogueList = Catalogue.objects.filter(catename = cate.id)
        error=""
        if not Maincategory.objects.filter(name='其他'):
            err = '无法删除'
            return HttpResponseRedirect('/admin/typemanage')
        if pkey == '其他':
            err = '无法删除'
            return HttpResponseRedirect('/admin/typemanage')

        for cata in catalogueList:
            if cata.name=='其他':
                for po in Post.objects.filter(catalogue=cata):
                    po.catalogue = Catalogue.objects.get(catename=Maincategory.objects.get(name='其他'),name='其他')
                    po.save()
            cata.catename = Maincategory.objects.get(name='其他')
            if cata.name=='其他':
                cata.delete()
            else:
                cata.save()

        cate.delete()
        #context = "can't delete type"
        return HttpResponseRedirect('/admin/typemanage')
        # return render(request, 'admin/typemanage.html', {'error': error})

#展示分类目录的视图
class CataView(ListView):
    template_name = 'admin/catalogue_admin.html'
    context_object_name = 'catalogue_list'

    def get_queryset(self):
        pkey = self.kwargs.get('pk')
        catalogue_list = Catalogue.objects.filter(catename = pkey)
        return catalogue_list

    def get_context_data(self, **kwargs):
        context = super(CataView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        obj, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = obj
        mc = Maincategory.objects.get(id=self.kwargs.get('pk'))
        context['maincate'] = mc
        return context

#接受表单并数据到数据库
class NewCataView(CreateView):
    template_name = 'admin/catalogue_new.html'
    model = Catalogue
    fields = ['name']

    def get_context_data(self, **kwargs):
        context = super(NewCataView,self).get_context_data(**kwargs)
        mc = Maincategory.objects.get(id=self.kwargs.get('pk'))
        context['maincate'] = mc
        return context
#class AddCataView(View):
    def post(self,request):
        n = request.POST.get("blogcata","")
        cn = int(request.POST.get("cateid",""))
        mc = Maincategory.objects.get(id=cn)
        Catalogue.objects.create(name=n,catename=mc)
        return HttpResponseRedirect('/admin/catalogue/'+str(mc.id))

class DelCataView(View):
    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get('pk')
        cata = Catalogue.objects.get(id=pkey)
        mc = Maincategory.objects.get(name=cata.catename)
        postList = Post.objects.filter(catalogue=cata)

        if not Catalogue.objects.filter(name='其他',catename=cata.catename):
            err = 'error'
            return HttpResponseRedirect('/admin/catalogue/'+str(mc.id))
        if cata.name =='其他':
            err = 'error'
            return HttpResponseRedirect('/admin/catalogue/'+str(mc.id))

        for p in postList:
            p.catalogue = Catalogue.objects.filter(name='其他',catename=cata.catename)[0]
            p.save()
        cata.delete()
        return HttpResponseRedirect('/admin/catalogue/'+str(mc.id))

class CommentView(ListView):
    template_name = 'admin/comment_admin.html'
    context_object_name = 'comment_list'

    #获取需要展示的数据并且返回（必须）
    def get_queryset(self):
        user = self.request.user
        comment_list = Comment.objects.filter(author=user).order_by('-publish_Time')
        return comment_list

    #传递额外的数据到模板
    def get_context_data(self, **kwargs):
        context = super(CommentView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        page_in_post = self.kwargs.get('pagepost') or self.request.GET.get('pagepost') or 0
        page = int(page)
        page_in_post = int(page_in_post)
        user = self.request.user
        l = []
        cl = Comment.objects.filter(author=user)
        for comm in cl:
            l += [comm.post.id]
        l = list(set(l))
        postl = Post.objects.filter(id__in=l)
        # obj, page_range = paginator_tool(pages=page, queryset=cl, display_amount=PERNUM)
        # context['page_range'] = page_range
        # context['objects'] = obj

        obj = []
        page_range = []
        for p in postl:
            if page_in_post==p.id:

                obj_tmp, page_range_tmp = paginator_tool(pages=page, queryset=cl.filter(post=p),display_amount=PERNUM)
            else:
                obj_tmp, page_range_tmp = paginator_tool(pages=1, queryset=cl.filter(post=p),display_amount=PERNUM)
            obj.append(obj_tmp)
            page_range.append(page_range_tmp)

        # context['page_range_list'] = page_range
        # context['objects_list'] = obj

        # context['page_range'] = page_range_tmp
        # context['objects'] = obj_tmp
        context['comm_post'] = postl
        context['zip'] = zip(postl,obj,page_range)

        return context


class DelCommentView(View):

    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get('pk')
        comm = Comment.objects.get(id=pkey)
        comm.delete()
        return HttpResponseRedirect('/admin/comments')

class CollectView(ListView):
    template_name = 'admin/collect_admin.html'
    context_object_name = 'collect_list'

    def get_queryset(self):
        user = self.request.user
        collect_list = Collection.objects.filter(collect_user=user)
        return collect_list

    def get_context_data(self, **kwargs):
        context = super(CollectView, self).get_context_data(**kwargs)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        obj, page_range = paginator_tool(pages=page, queryset=self.object_list, display_amount=PERNUM)
        context['page_range'] = page_range
        context['objects'] = obj
        return context

class DelCollectView(View):
    def get(self, request, *args, **kwargs):
        pkey = self.kwargs.get('pk')
        col = Collection.objects.get(id=pkey)
        col.delete()
        return HttpResponseRedirect('/admin/collects')

def donate_view(request):
    return TemplateResponse(request, "admin/donate.html")


def qrcode_image_upload_handler(request):
    if request.method == "POST":
        try:
            if 'alipay' in request.FILES.keys():
                file_img = request.FILES['alipay']
                file_suffix = os.path.splitext(file_img.name)[len(os.path.splitext(file_img.name)) - 1]
                # 检查图片格式
                if file_suffix not in image_type:
                    return HttpResponse("请上传正确格式的图片文件")
                filename = uuid.uuid1().__str__() + file_suffix

                img = Image.open(file_img)

                path = MEDIA_ROOT + "/alipay_qrcode/"
                if not os.path.exists(path):
                    os.makedirs(path)

                file_name = path + filename
                img.save(file_name)

                file_img_url = "http://" + request.META['HTTP_HOST'] + MEDIA_URL + "alipay_qrcode/" + filename
                user = request.user
                user.alipay_qrcode_path = file_img_url
                user.save()

            # 微信部分，方便起见先这么写了，不管冗余
            if 'wechat' in request.FILES.keys():
                file_img = request.FILES['wechat']
                file_suffix = os.path.splitext(file_img.name)[len(os.path.splitext(file_img.name)) - 1]
                # 检查图片格式
                if file_suffix not in image_type:
                    return HttpResponse("请上传正确格式的图片文件")
                filename = uuid.uuid1().__str__() + file_suffix

                img = Image.open(file_img)

                path = MEDIA_ROOT + "/wechat_qrcode/"
                if not os.path.exists(path):
                    os.makedirs(path)

                file_name = path + filename
                img.save(file_name)

                file_img_url = "http://" + request.META['HTTP_HOST'] + MEDIA_URL + "wechat_qrcode/" + filename
                user = request.user
                user.wechat_qrcode_path = file_img_url
                user.save()

        except Exception:
            pass

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', "/"))
