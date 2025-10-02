# ---------------------------------------------------------------------------------------------------
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
# from django.conf.urls import url
from django.urls import re_path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import re
from datetime import datetime, timedelta, time
from django.db.models import Sum
from datetime import date
from collections import OrderedDict
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordChangeView
# from . views import PasswordsChangeView
# ---------------------------------------------------------------------------------------------------


# **********************************************************************************************
urlpatterns = [
    path('sign_me_up', views.sign_me_up, name='sign_me_up'),
    path('sign_me_in', views.sign_me_in, name='sign_me_in'),
    path('sign_me_out', views.sign_me_out, name='sign_me_out'),
    path('user_dashboard', views.user_dashboard, name='user_dashboard'),
    path('change_my_photo', views.change_my_photo, name='change_my_photo'),
    path('change_my_password', views.change_my_password, name='change_my_password'),
    path('change_working_mode/<str:dev_sl>/', views.change_working_mode, name='change_working_mode'),

    path('manually_activate_deactivate/<str:dev_sl>/<int:act_deact>/', views.manually_activate_deactivate, name='manually_activate_deactivate'),

    path('capture_image', views.capture_image, name='capture_image'),
    path('alarm_light_on', views.alarm_light_on, name='alarm_light_on'),
    path('alarm_light_off', views.alarm_light_off, name='alarm_light_off'),





    path('single_meter_log/<str:meter_id>/', views.single_meter_log, name='single_meter_log'),
    path('activate_account/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('forgot_password_validate/<uidb64>/<token>/', views.forgot_password_validate, name='forgot_password_validate'),
    path('image_capture_command', views.image_capture_command, name='image_capture_command'),
]
# **********************************************************************************************
