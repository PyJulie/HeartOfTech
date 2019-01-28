## 目录
* [说明](#1)
* [功能](#2)
* [如何使用](#3)

## <a name="1">说明</a>
这是一个Django多人博客系统，以整体的思路来说，一个个人博客系统，需要有个人的后台管理，不需要进行注册，游客由于没有站点账号，因此无法进行评论，或者提供注册界面，方便用户注册后对博文内容进行询问。用户只需要管理自己所发的博文，或者对非法的一些评论就行删除即可，至于美化界面并不需要特别地在后台进行前端接口的开放，只需要直接对页面进行美化编辑即可。
而对于一个公共的开放式博客系统来说，由于很多用户都要进行博文的发布，因此，除了博主的权限以外，还应加入超级管理员的角色，方便对所有博主用户进行管理，因此，对于没有任何编程经验的博主或者编辑来说，加入一个美观且操作便捷的后台系统因此就变得十分有必要。
再者，考虑到盈利的部分，也应加入广告管理与新闻部分，这部分同样由编辑来负责，另外在某些特色功能上，要与其他的博客系统进行区分，否则失去了造轮子的意义，如果本项目与市面上其他的博客系统雷同或者大同小异，那么也就没有必要进行重头式的开发。

## <a name="2">功能</a>

针对博主方面：
* 打赏是驱动博主写出优秀博文的动力，所以我们增加了打赏功能，博主可以上传自己微信或支付宝的收款码方便读者进行打赏。
* 可选择富文本模式和MarkDown模式之间的自由切换。从最早的富文本到后来的LaTEX，程序员们对写作工具的要求也变得越来越高，甚至有程序员提出没有MarkDown自己无法写出文字这样的说法，因此，我觉得加入MarkDown文本编辑器很有必要。另外，市面上很多的MarkDown写作工具是收费的，这样也变相为博主们提供了一个写作工具，即使他们不发布在我们的平台上。但对于用户的粘性来说，这是一个很好的解决方案。
* 草稿功能，博主有新鲜的思路但不愿意立即发布，或者文章内容还有待更改，就可使用草稿功能，这样可以随时进入编辑模式，然后确认无误后再发布。未来还可以加入自动保存功能，防止因网页崩溃、供电中断造成的数据丢失。
针对编辑方面：
* 编辑可以发布新闻，新闻可增加站点流量，还能成为潜在的获益渠道。
* 编辑可以对文章进行加精或推荐，好的文章会自动出现在首页列表，编辑还可以设置轮播功能，这样对于优秀的文章可以直接做推荐，而且用户也能看地更直观。
对于整个博客系统，我们提出：
特色功能：
* 可以添加广告，而且在后台可以直接对广告进行增删改查。
* 强大的搜索功能，在你想要的时候总能出现在你眼前，搜索覆盖到需要对文章内容进行检索的方方面面。
* 举报功能，感谢用户们为净化网络作出的贡献。
* 楼中楼回复，更方便用户之间的交流与互动。
* 自动推荐系统，使用机器学习方法，对文章之间的相似度进行检测，自动为你推荐相似文章
* 邮箱验证注册，避免机器人批量注册，而且找回密码也可以通过邮箱进行验证。
* Session记录，用户可以选择是否记住用户，避免在个人电脑上访问站点时，需要重复不断地登录。
* 细致的分类列表，可以帮助用户快速地寻找到自己感兴趣的文章分类，避免了漫无目的地浏览站点。
* 自动生成标签云，方便用户查找自己所感兴趣的内容，通常用户在浏览所有标签时，处于并无明确目标信息的“漫游”状态。为了更好地体现侧边栏的内容（包括后期扩充的内容），提供更多兴趣入口点。 
* 分享功能，将您喜爱的文章分享到微博、微信等比较常用的公共平台上。


## <a name="3">如何使用</a>

需要安装的包：
* django
* django-tagging
* pillow(该包为PIL的一个分支，由于停止维护，目前pip和easy_install好像都无法下载安装PIL了)
* MySQL-python（还有一个数据库驱动，我使用的是MySQL，你也可以使用其他驱动）

安装完成后，打开settings，修改其中的数据库配置。配置如下：

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'yourname',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': '127.0.0.1',
            'PORT': '3306'
        }
    }


* 在项目根目录下输入 `python manager.py makemigrations` \
* 再输入 `python manager.py migrate` 生成数据库表
* 然后使用 `python manager.py runserver` 启动数据库即可。
* 若要正式部署使用，建议使用 nginx+uwsgi 部署，可参考[Nginx+uWSGI安装与配置](http://mdba.cn/?p=109)
