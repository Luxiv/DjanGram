from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from main.views import about, RegistrationUser, Profile, Timeline, like_view, tagged,\
    ViewArticle, new_article, LoginUser, logout_user, friends, recommendations, EmailVerify, FullProfileInfo

urlpatterns = [
    path('', Timeline.as_view(), name='timeline'),
    path('profile/<slug:usr_slug>/', Profile.as_view(), name='profile'),
    path('post/<slug:post_slug>/', ViewArticle.as_view(), name='post_view'),
    path('tag/<slug:slug>/', tagged, name="tagged"),
    path('new-post/', new_article, name='new-post'),
    path('about-us/', about, name='about'),
    path('registration/', RegistrationUser.as_view(), name='registration'),
    path('confirm_email/', TemplateView.as_view(template_name='main/confirm_email.html'), name='confirm_email'),
    path('verify_email/<uidb64>/<token>/', EmailVerify.as_view(), name='verify_email'),
    path('invalid_verify/', TemplateView.as_view(template_name='invalid_verify.html'), name='invalid_verify'),
    path('profile_info/<slug:usr_slug>/', FullProfileInfo.as_view(), name='profile_info'),
    path('add_info/', TemplateView.as_view(template_name='main/add_info.html'), name='add_info'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('friends/', friends, name='friends'),
    path('recommendations/', recommendations, name='recommendations'),
    path('like/<slug:slug>/', like_view, name='like_post'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



