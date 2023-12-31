from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("api/register", views.register),
    path("api/verify/code", views.verify_verification_code),
    path("api/login", views.login),
    path("api/refresh/token", TokenRefreshView.as_view()),
    path("api/change/password", views.change_password),
    path("api/add/friend", views.add_friend),
    path("api/get/profile", views.get_profile),
    path("api/get/friends", views.get_friends),
    path("api/upload/profile/picture", views.upload),
    path("api/send/reset/code", views.send_reset_password_code),
    path("api/reset/password", views.reset_password),
    path("api/delete/account", views.delete_account),
    path("api/deactivate/account", views.deactivate_account)
]
