from django.conf.urls import url

from blog.views import HistoryView, News1View,AuthorNewsListView, report_view,IndexView, PostView, CommentView, RepositoryView, RepositoryDetailView, TagListView, \
    CategoryListView, AuthorPostListView, CommentDeleteView,NewsView,emtest_view,change_view, CollectView,CatalogueListView,register_views, \
    ceshi, show_Agreement, show_aboutUs, contact_us, SearchView, RecommendView, TagsView


urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^news/$',NewsView.as_view()),
    url(r'^post/(?P<pk>[0-9]+)$', PostView.as_view()),
    url(r'^news/(?P<pk>[0-9]+)$', News1View.as_view()),
    url(r'^comment/add/(?P<pk>[0-9]+)$', CommentView.as_view()),
    url(r'^comment/delete/(?P<pk>[0-9]+)$', CommentDeleteView.as_view()),
    url(r'^repository$', RepositoryView.as_view()),
    url(r'^repository/(?P<pk>[0-9]+)$', RepositoryDetailView.as_view()),
    url(r'^tag/(?P<slug>[\w\u4e00-\u9fa5]+)$', TagListView.as_view()),
    url(r'^catalogue/(?P<slug>[0-9]+)$', CatalogueListView.as_view()),
    url(r'^author/(?P<pk>[0-9]+)$', AuthorPostListView.as_view()),
    url(r'^test/$',emtest_view,name='sp'),
    url(r'^change_sc/$',change_view,name='ch'),
    url(r'^blog/report/(?P<pk>[0-9]+)$',report_view.as_view()),
    url(r'^author1/(?P<pk>[0-9]+)$', AuthorNewsListView.as_view()),#新闻归档
    url(r'^category/(?P<pk>[0-9]+)$', CategoryListView.as_view()),
    url(r'^add/collect/(?P<pk>[0-9]+)$',CollectView.as_view()),
# 123456
    url(r'^register/$',register_views),
    # url(r'captcha/$', verifycode),
    url(r'ceshi/$',register_views),
    url(r'tiaozhuan/$',ceshi),
    url(r'agreement/$',show_Agreement),
    url(r'aboutus/$',show_aboutUs),
    url(r'contact/$',contact_us),
    # url(r'^change_sc_done/$',change_view_done,name='chd'),
    #####
    url(r'^recommend/(?P<pk>[0-9]+)$', RecommendView.as_view()),
    url(r'^search/(?P<pk>.+)$', SearchView.as_view(), name='search'),# 新增
    url(r'^history/(?P<pk>[0-9]+)$',HistoryView.as_view()),#查看历史文章
	url(r'^tags/$', TagsView.as_view()),
]