from django.http import HttpResponseRedirect


class AdminAuthenticationMiddleware(object):
    def process_request(self, request):
        if (request.path != '/admin/login/' and request.path != '/admin/bkpwd' and request.path != '/admin/bkpwdone') and 'admin' in request.path:
            user = request.user
            if not user.is_authenticated():
                return HttpResponseRedirect('/admin/login')

