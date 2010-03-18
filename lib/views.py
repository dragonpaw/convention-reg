# Create your views here.
import settings
#from django.contrib.auth.views

@render('login.html')
def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user)
            log.info('Logged in: %s', form.user)
            return HttpResponseRedirect(form.cleaned_data['next'])
    else:
        try:
            next = request.REQUEST['next']
        except KeyError:
            next = settings.LOGIN_REDIRECT_URL
        form = UserLoginForm(initial={'next': next})

    return {'form': form }
