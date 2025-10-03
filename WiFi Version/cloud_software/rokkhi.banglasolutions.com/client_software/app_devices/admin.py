from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from . models import *
# ------------------------------------------------------------------------------


# ***************************************************************************************************************
class DeviceInfoAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = [
        'dev_sl', 'dev_user', 'dev_name', 'dev_ver', 'esp_mac', 'active', 'dev_active_mode',
        'dev_active_hour_start', 'dev_active_hour_end', 'dev_alert_type', 'dev_alert_cause', 'change_pending',
        'alert_number', 'alert_email', 'snooze_delay', 'busy_status', 'remark',]

    list_display_links = ['dev_sl']

    list_editable = [
        'dev_active_mode', 'dev_active_hour_start', 'dev_active_hour_end',
        'dev_alert_type', 'dev_alert_cause', 'change_pending', 'alert_number', 'alert_email', 'snooze_delay', 'busy_status',]

    list_filter = ['dev_ver', 'active']
    search_fields = ['dev_sl']
    # readonly_fields = ['dev_sl']
    # ------------------------------------------------------------------------------
    list_per_page = 10
    list_max_show_all = 10
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['dev_sl', 'dev_name', 'dev_ver',]
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class DeviceHeartbeatAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'hb_time', 'no_of_reboot']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ManualCapturedImageAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'image_thumb', 'insert_date_time', 'image_size']
    list_display_links = ['device_info_id']
    # ------------------------------------------------------------------------------
    list_per_page = 50
    list_max_show_all = 50
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def image_thumb(self, obj):
        if obj.image_path:
            return mark_safe(
                f'<a href="{obj.image_path.url}" target="_blank">'
                f'<img src="{obj.image_path.url}" width="100" height="auto" style="border:1px solid #ccc;"/>'
                f'</a>'
            )
        return "-"

    image_thumb.short_description = 'Image Preview'

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['-insert_date_time']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class MotionVideoFromDeviceAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = [
        'device_info_id',
        'insert_date_time',
        'video_path',
        'video_size',
        'total_frame',
        'is_detection_applied',

        'is_person_found',
        'person_image_thumb',
        'person_found_frame_no',

        'is_motion_found',
        'motion_image_thumb',
        'motion_found_frame_no',

        # 'motion_found_frame_path',
        # 'person_found_frame_path',
        'is_alert_done',
        'is_alert_snooze']
    # ------------------------------------------------------------------------------
    readonly_fields = ['motion_image_thumb', 'person_image_thumb']  # Show thumbnail in the form view
    list_display_links = ['device_info_id']
    list_editable = ['is_detection_applied', 'is_alert_done', 'is_alert_snooze']
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    list_per_page = 10
    list_max_show_all = 10
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['-insert_date_time']
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def motion_image_thumb(self, obj):
        if obj.motion_found_frame_path:
            return mark_safe(
                f'<a href="{obj.motion_found_frame_path.url}" target="_blank">'
                f'<img src="{obj.motion_found_frame_path.url}" width="100" height="auto" style="border:1px solid #ccc;"/>'
                f'</a>'
            )
        return "-"

    motion_image_thumb.short_description = 'Motion Image'
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def person_image_thumb(self, obj):
        if obj.person_found_frame_path:
            return mark_safe(
                f'<a href="{obj.person_found_frame_path.url}" target="_blank">'
                f'<img src="{obj.person_found_frame_path.url}" width="100" height="auto" style="border:1px solid #ccc;"/>'
                f'</a>'
            )
        return "-"

    person_image_thumb.short_description = 'Person Image'
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # # Optional: Organize form layout. Set fields to be shown and Ordering
    # fieldsets = (
    #     (None, {'fields': ('motion_found_frame_path', 'motion_image_thumb'),}),
    # )
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ImageCaptureCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'resolution', 'flashlight', 'cmd_status', 'active']
    list_display_links = ['device_id']
    list_editable = ['resolution', 'flashlight', 'cmd_status', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class USSDCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'ussd_cmd', 'cmd_status', 'active']
    list_display_links = ['device_info_id']
    list_editable = ['ussd_cmd', 'cmd_status', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class USSDCommandResultAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'ussd_code', 'ussd_result', 'insert_date_time']
    list_display_links = ['device_info_id']
    # list_editable = ['ussd_code', 'ussd_result']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class MobileCallCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'mobile_no', 'call_duration', 'cmd_status', 'active']
    list_display_links = ['device_id']
    list_editable = ['mobile_no', 'call_duration', 'cmd_status', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class MobileCallResultAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'insert_date_time', 'called_to', 'call_duration', 'active']
    list_display_links = ['device_info_id']
    list_editable = ['active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class MobileSMSResultAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'sms_to', 'active']
    list_display_links = ['device_info_id']
    list_editable = ['active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOnCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOnLogAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'insert_date_time']
    list_display_links = ['device_info_id']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOffCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOffLogAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'insert_date_time']
    list_display_links = ['device_info_id']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class NoOfFrameToCaptureCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'cmd_name', 'number_of_frame', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'number_of_frame', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class HbDelayCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'cmd_name', 'hb_delay', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'hb_delay', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ControlMotionCaptureAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'enable_or_disable_motion_capture', 'enable_or_disable_flash_light',
                    'vdo_frame_size', 'no_of_frame_capture_limit', 'active']
    list_display_links = ['device_id']

    list_editable = ['cmd_status', 'enable_or_disable_motion_capture', 'enable_or_disable_flash_light',
                     'vdo_frame_size', 'no_of_frame_capture_limit', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class WiFiSSIDPassCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'cmd_name', 'ssid', 'password', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'ssid', 'password', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class CloudIPDomainPortCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'cmd_name', 'cloud_ip', 'cloud_domain', 'cloud_port', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'cloud_ip', 'cloud_domain', 'cloud_port', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class DeviceSerialCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'cmd_name', 'device_sl', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'device_sl', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class CameraInitSettingCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_status', 'cmd_name', 'cam_flip', 'cam_mirror', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'cam_flip', 'cam_mirror', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ImageResolutionListAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['cmd_visual', 'cmd', 'active']
    list_display_links = ['cmd_visual']
    list_editable = ['active']
    # ------------------------------------------------------------------------------
    list_per_page = 15
    list_max_show_all = 15
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['cmd']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ResetRebootCounterCommandAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_id', 'cmd_name', 'cmd_status', 'active']
    list_display_links = ['device_id']
    list_editable = ['cmd_status', 'active']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class DevTempLogAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------------------
    list_display = ['device_info_id', 'insert_date_time', 'dev_temp']
    list_display_links = ['device_info_id']
    # ------------------------------------------------------------------------------
    list_per_page = 100
    list_max_show_all = 100
    actions_on_top = True
    actions_on_bottom = True
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def get_ordering(self, request):
        return ['device_info_id']
    # ------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
admin.site.register(MotionVideoFromDevice, MotionVideoFromDeviceAdmin)
admin.site.register(ManualCapturedImage, ManualCapturedImageAdmin)
admin.site.register(DeviceInfo, DeviceInfoAdmin)
admin.site.register(DeviceHeartbeat, DeviceHeartbeatAdmin)
admin.site.register(ImageCaptureCommand, ImageCaptureCommandAdmin)
admin.site.register(LightAlarmOnCommand, LightAlarmOnCommandAdmin)
admin.site.register(LightAlarmOnLog, LightAlarmOnLogAdmin)
admin.site.register(LightAlarmOffCommand, LightAlarmOffCommandAdmin)
admin.site.register(LightAlarmOffLog, LightAlarmOffLogAdmin)
admin.site.register(HbDelayCommand, HbDelayCommandAdmin)
admin.site.register(ControlMotionCapture, ControlMotionCaptureAdmin)
admin.site.register(WiFiSSIDPassCommand, WiFiSSIDPassCommandAdmin)
admin.site.register(CloudIPDomainPortCommand, CloudIPDomainPortCommandAdmin)
admin.site.register(ResetRebootCounterCommand, ResetRebootCounterCommandAdmin)
admin.site.register(CameraInitSettingCommand, CameraInitSettingCommandAdmin)
admin.site.register(ImageResolutionList, ImageResolutionListAdmin)
admin.site.register(DevTempLog, DevTempLogAdmin)
# ------------------------------------------------------------------------------
admin.site.register(EspMacId)
admin.site.register(DeviceVersion)
# ***************************************************************************************************************
