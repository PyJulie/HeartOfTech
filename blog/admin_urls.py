from django.conf.urls import url,include

from blog.admin_views import  DeletePost2, DeletePost1,DeleteReport,Creport,backpwdone_view,backpwd_view, changedo_view, PostView,NewsView,AddNews,BanPost,CPost_view, DeletePost,CPost, NewPost, UpdatePostIndexView, AddPost, \
    UpdateDraft, UpdatePost, UpdateEditor,NewNews, LogoutView, CarouselIndexView, CarouselEditView, \
    AddCarousel, DeleteCarousel, CarouselUpdateView, UpdateCarousel, markdown_image_upload_handler, \
    tinymce_image_upload_handler, UserSetView, NewUserView, AddUser, avatar_image_upload_handler,BanUser,change_view,\
    TypeView, NewTypeView, AddTypeView, DelTypeView, CataView, NewCataView, DelCataView,CommentView,\
    DelCommentView, CollectView, DelCollectView, donate_view, qrcode_image_upload_handler

urlpatterns = [
    url(r'^admin/', include([
        url(r'^$', PostView.as_view(), name='index'),
        url(r'^delete/(?P<pk>[0-9]+)$', DeletePost.as_view()),
        url(r'^new$', NewPost.as_view()),
        url(r'^add$', AddPost.as_view()),
        url(r'^update/draft/(?P<pk>[0-9]+)$', UpdateDraft.as_view()),
        url(r'^update/post/(?P<pk>[0-9]+)$', UpdatePost.as_view()),
        url(r'^update/(?P<pk>[0-9]+)$', UpdatePostIndexView.as_view()),
        url(r'^upload/markdown/post$', markdown_image_upload_handler),
        url(r'^upload/tinymce/post$', tinymce_image_upload_handler),
        url(r'^update/editor$', UpdateEditor.as_view()),
        url(r'^carousel$', CarouselIndexView.as_view()),
        url(r'^new/carousel$', CarouselEditView.as_view()),
        url(r'^add/carousel$', AddCarousel.as_view()),
        url(r'^delete/carousel/(?P<pk>[0-9]+)$', DeleteCarousel.as_view()),
        url(r'^update/carousel/(?P<pk>[0-9]+)$', CarouselUpdateView.as_view()),
        url(r'^update/carousel/id/(?P<pk>[0-9]+)$', UpdateCarousel.as_view()),
        url(r'^repository$', PostView.as_view(), name='index'),
        url(r'^userset$', UserSetView.as_view()),
        url(r'^new/user$', NewUserView.as_view()),
        url(r'^add/user$', AddUser.as_view()),
        url(r'^set/upload/avatar$', avatar_image_upload_handler),
        url(r'^logout$', LogoutView.as_view()),
        url(r'^newsl$', NewsView.as_view()),#新闻管理
        url(r'^adnew$', NewNews.as_view()),#添加新闻
        url(r'^addn$', AddNews.as_view()),#确认添加新闻
        url(r'^cblog$',CPost_view,name='zc'),#博文管理界面
        url(r'^bpost/(?P<pk>[0-9]+)$',BanPost.as_view()),#封禁
        url(r'^buser/(?P<pk>[0-9]+)$',BanUser.as_view()),#封禁账户
        url(r'^search/*',CPost_view,name='pc'),#细致查找
        # url(r'^search1/*',UserSetView.as_view()),#细致查找用户
        # url(r'^change_sc/$',chang_view,name='ch'),
        # url(r'^change_sc_done/$',chang_view_done,name='chd'),
        url(r'^change_sc/$',change_view,name='ch'),#修改密保
        url(r'^change_done',changedo_view,name='sh'),#修改完成
        url(r'^bkpwd$', backpwd_view),#忘记密码
        url(r'^bkpwdone$', backpwdone_view),#忘记密码
        url(r'^creport$',Creport.as_view()),#举报信息管理界面
        url(r'^del/(?P<pk>[0-9]+)$', DeleteReport.as_view()),#删除举报信息
        url(r'^typemanage',TypeView.as_view()),
        url(r'^new/type$',NewTypeView.as_view()),
        url(r'^add/type$',AddTypeView.as_view()),
        url(r'^delete/maincategory/(?P<pk>[\s\S]+)$',DelTypeView.as_view()),
        url(r'^catalogue/(?P<pk>[0-9]+)$',CataView.as_view()),
        url(r'^new/catalogue/(?P<pk>[0-9]+)$',NewCataView.as_view()),
        url(r'^add/catalogue$',NewCataView.as_view()),
        url(r'^delete/catalogue/(?P<pk>[0-9]+)$',DelCataView.as_view()),
        url(r'^comments$',CommentView.as_view()),
        url(r'^comments/del/(?P<pk>[0-9]+)$',DelCommentView.as_view()),
        url(r'^collects$',CollectView.as_view()),
        url(r'^delete/collect/(?P<pk>[0-9]+)$',DelCollectView.as_view()),
        url(r'^delete1/(?P<pk>[0-9]+)$', DeletePost1.as_view()),
		url(r'^delete2/(?P<pk>[0-9]+)$', DeletePost2.as_view()),
        url(r'^donate$', donate_view),#打赏管理
        url(r'^set/upload/qrcode$', qrcode_image_upload_handler),
       ])),
]