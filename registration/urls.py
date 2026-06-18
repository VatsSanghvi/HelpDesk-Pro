from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.urls import urlpatterns as auth_url_patterns

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # USER URLS
    path('user_list/', views.UserListView.as_view(), name='user_list'),
    path('user_list_role/<str:role>', views.UserRoleListView.as_view(), name='user_list_role'),
   
    path('user_detail/<int:pk>', views.UserDetailView.as_view(), name='user_detail'),
    path('user_create/', views.UserCreateView.as_view(), name='user_create'),
    path('user_update/<int:pk>', views.UserUpdateView.as_view(), name='user_update'),
    
    path('profile/<int:pk>', views.UserDetailView.as_view(), name='profile'),
    path('profile_update/<int:pk>', views.UserUpdateView.as_view(), name='profile_update'),
]

urlpatterns += auth_url_patterns[1:]


# DEFAULT DJANGO URLS AND FORMS

# path('', include('django.contrib.auth.urls'))

# login/                        auth_views.LoginView                        [name='login']                      auth_forms.AuthenticationForm
# logout/                       auth_views.LogoutView                       [name='logout']
# password_change/              auth_views.PasswordChangeView               [name='password_change']            auth_forms.PasswordChangeForm
# password_change/done/         auth_views.PasswordChangeDoneView           [name='password_change_done']
# password_reset/               auth_views.PasswordResetView                [name='password_reset']             auth_forms.PasswordResetForm
# password_reset/done/          auth_views.PasswordResetDoneView            [name='password_reset_done']
# reset/<uidb64>/<token>/       auth_views.PasswordResetConfirmView         [name='password_reset_confirm']     auth_forms.SetPasswordForm
# reset/done/                   auth_views.PasswordResetCompleteView        [name='password_reset_complete']


# from django.contrib.auth import forms as auth_forms
# from django.contrib.auth import views as auth_views

# path('login/'                   , auth_views.LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True)   , name='login')
# path('logout/'                  , auth_views.LogoutView.as_view(template_name='registration/logout.html')                                   , name='logout')
# path('password_change/'         , auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html')             , name='password_change')
# path('password_change/done/'    , auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html')         , name='password_change_done')
# path('password_reset/'          , auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html')               , name='password_reset')
# path('password_reset/done/'     , auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html')           , name='password_reset_done')
# path('reset/<uidb64>/<token>/'  , auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html')     , name='password_reset_confirm')
# path('reset/done/'              , auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html')   , name='password_reset_complete')