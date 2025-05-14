from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
#from home.views import home
from django.contrib.auth import views as auth_views
from cuoora.views import topic_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', include('cuoora.urls')),
    path('topics/', topic_list, name='topic_list'),
    #path('', home, name='home'),
    path('users/', include('users.urls'), name='users'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    