# ***************************************************************************************************
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
# ***************************************************************************************************


# ***************************************************************************************************
admin.site.site_header = 'zOs'
admin.site.site_title = 'zOs Admin'
admin.site.index_title = 'zOs Administration'
# ***************************************************************************************************


# ***************************************************************************************************
urlpatterns = [
    # ---------------------------------------------------------------------------------------------------
    # Self URLs
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    path('get_motion_call_and_sms_nos', views.get_motion_call_and_sms_nos, name='get_motion_call_and_sms_nos'),
    path('reset_motion_call_pending_status', views.reset_motion_call_pending_status, name='reset_motion_call_pending_status'),
    
    


    # path('', views.gmap_tracking, name='gmap_tracking'),
    # path('ajax_new_values', views.ajax_new_values, name='ajax_new_values'),
    # path('insert_data_to_log_table', views.insert_data_to_log_table, name='insert_data_to_log_table'),
    # path('upload_and_save_photo', views.upload_and_save_photo, name='upload_and_save_photo'),
    # ---------------------------------------------------------------------------------------------------
    # Devices management service related URL
    # path('update_hb_table', views.update_hb_table, name='update_hb_table'),
    # path('update_bill_status_in_ticketing_log', views.update_bill_status_in_ticketing_log, name='update_bill_status_in_ticketing_log'),
    # ---------------------------------------------------------------------------------------------------
    # path('live_dashboard/', views.live_dashboard, name='live_dashboard'),
    # path('update_hb_table', views.update_hb_table, name='update_hb_table'),
    # path('reports_dashboard/<str:report_type>', views.reports_dashboard, name='reports_dashboard'),
    # ---------------------------------------------------------------------------------------------------
    # App URLs
    path('app_users', include('app_users.urls')),
    # path('app_devices', include('app_devices.urls')),
    # path('app_google_map_tracking', include('app_google_map_tracking.urls')),
    # path('app_user_management', include('app_user_management.urls')),
    # ---------------------------------------------------------------------------------------------------
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ***************************************************************************************************

