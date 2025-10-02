from datetime import datetime
import time
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator
# ---------------------------------------------------------------------------------------------------------------


# ***************************************************************************************************************
class EspMacId(models.Model):
    # ----------------------------------------------------------------------------------------------
    esp_mac = models.CharField(max_length=50, unique=True, verbose_name='Device MAC')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '01. Device MAC'
        verbose_name_plural = '01. Device MACs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.esp_mac}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class DeviceVersion(models.Model):
    # ----------------------------------------------------------------------------------------------
    version = models.CharField(max_length=20, unique=True, verbose_name='Device Version')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '02. Device Version'
        verbose_name_plural = '02. Device Versions'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.version}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class DeviceInfo(models.Model):
    # ----------------------------------------------------------------------------------------------
    dev_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='DeviceInfo_dev_user', verbose_name='Device User')
    dev_sl = models.CharField(max_length=50, unique=True, verbose_name='Device Serial')
    dev_name = models.CharField(max_length=50, verbose_name='Device Name')
    dev_ver = models.ForeignKey(DeviceVersion, on_delete=models.CASCADE, related_name='DeviceInfo_dev_ver', verbose_name='Device Version')
    esp_mac = models.ForeignKey(EspMacId, on_delete=models.CASCADE, related_name='DeviceInfo_esp_mac', verbose_name='ESP MAC')
    active = models.BooleanField(default=False, verbose_name='Is Device Active')
    # ----------------------------------------------------------------------------------------------
    ACTIVE_MODE = (('always_on', 'Always ON'), ('always_off', 'Always OFF'), ('schedule', 'Schedule ON-OFF'), ('a_on_m_off', 'Manual OFF - Auto ON'))
    dev_active_mode = models.CharField(max_length=30, choices=ACTIVE_MODE, default='always_on', verbose_name='Device Active Mode')

    from datetime import time
    active_hour_start = time(hour=23, minute=0, second=0)
    active_hour_end = time(hour=6, minute=0, second=0)

    dev_active_hour_start = models.TimeField(default=active_hour_start, verbose_name='Active Hour Start')
    dev_active_hour_end = models.TimeField(default=active_hour_end, verbose_name='Active Hour End')

    change_pending = models.BooleanField(default=False, verbose_name='Active Mode Change Pending')
    # ----------------------------------------------------------------------------------------------
    ALERT_TYPE = (('call', 'Call'), ('sms', 'SMS'), ('email', 'Email'), ('all', 'All'), ('off', 'Off'))
    dev_alert_type = models.CharField(max_length=30, choices=ALERT_TYPE, default='call', verbose_name='Alert Type')

    alert_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Alert Number')
    alert_email = models.CharField(max_length=200, blank=True, null=True, verbose_name='Alert Email')

    snooze_delay = models.IntegerField(default=5, blank=True, null=True, verbose_name='Snooze Minute')
    # ----------------------------------------------------------------------------------------------
    busy_status = models.BooleanField(default=False, verbose_name='Device Busy Status')
    # ----------------------------------------------------------------------------------------------
    remark = models.CharField(max_length=300, blank=True, null=True, verbose_name='Remarks')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '03. Device Detail'
        verbose_name_plural = '03. Devices Details'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.dev_sl}, {self.dev_name}"

    # def __str__(self):
    #     return f"{self.dev_user}, " \
    #            f"{self.dev_sl}, " \
    #            f"{self.dev_name}, " \
    #            f"{self.dev_ver}, " \
    #            f"{self.esp_mac}, " \
    #            f"{self.active}, " \
    #            f"{self.dev_active_mode}, " \
    #            f"{self.active_status}, " \
    #            f"{self.active_hour_start}, " \
    #            f"{self.active_hour_end}, " \
    #            f"{self.dev_active_hour_start}, " \
    #            f"{self.dev_active_hour_end}, " \
    #            f"{self.dev_alert_type}, " \
    #            f"{self.alert_number}, " \
    #            f"{self.alert_email}, " \
    #            f"{self.busy_status}, " \
    #            f"{self.remark}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class HbDelayCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='HbDelayCommand_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    cmd_name = models.CharField(max_length=30, verbose_name='CMD Name')
    hb_delay = models.IntegerField(default=10, verbose_name='HB Delay')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'D. HB Delay CMD'
        verbose_name_plural = 'D. HB Delay CMDs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.cmd_name}"\
               f"{self.hb_delay}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class DeviceHeartbeat(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_info_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='DeviceHeartbeat_device_info_id', verbose_name='Device info id')
    hb_time = models.DateTimeField(default=now, verbose_name='Last HB time')
    no_of_reboot = models.IntegerField(default=0, blank=True, null=True, verbose_name='Number of Reboot')
    # -----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '05. Device HB'
        verbose_name_plural = '05. Device HBs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_info_id}, " \
               f"{self.no_of_reboot}" \
               f"{self.hb_time}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ImageResolutionList(models.Model):
    # ----------------------------------------------------------------------------------------------
    cmd_visual = models.CharField(max_length=30, verbose_name='Image resolution')
    cmd = models.IntegerField(default=7, verbose_name='Value')
    active = models.BooleanField(default=False, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '04. Photo Resolution'
        verbose_name_plural = '04. Photo Resolutions'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.cmd_visual}" \
               f"{self.cmd}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ImageCaptureCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='ImageCaptureCommandForDevice_device_id', verbose_name='Device ID')
    resolution = models.ForeignKey(ImageResolutionList, on_delete=models.CASCADE, verbose_name='Resolution')

    # FLASH_STATUS = (('1', 'ON'), ('0', 'OFF'))
    # flashlight = models.CharField(max_length=10, choices=FLASH_STATUS, default='ON', verbose_name='Flash')
    flashlight = models.BooleanField(default=True, verbose_name='Flash')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'A. Photo Capture CMD'
        verbose_name_plural = 'A. Photo Capture CMDs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.resolution}"\
               f"{self.flashlight}" \
               f"{self.cmd_status}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ManualCapturedImage(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_info_id = models.ForeignKey(DeviceInfo, on_delete=models.CASCADE, related_name='ManualCapturedImage_device_info_id', verbose_name='Device info id')
    insert_date_time = models.DateTimeField(default=now, verbose_name='Insert date time')
    image_size = models.IntegerField(default=0, blank=True, null=True, verbose_name='Image size')
    image_path = models.ImageField(verbose_name='Image path')
    # -----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '06. Captured Photo'
        verbose_name_plural = '06. Captured Photos'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_info_id}, " \
               f"{self.insert_date_time}, " \
               f"{self.image_size}, " \
               f"{self.image_path}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ControlMotionCapture(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='ControlMotionCapture_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    enable_or_disable_motion_capture = models.BooleanField(default=True, verbose_name='Is Motion Capture')
    enable_or_disable_flash_light = models.BooleanField(default=True, verbose_name='Is Flash')
    no_of_frame_capture_limit = models.IntegerField(default=33, verbose_name='Frame Limit')
    vdo_frame_size = models.IntegerField( default=7, verbose_name='Frame Size')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'E. VDO Setting CMD'
        verbose_name_plural = 'E. VDO Setting CMDs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.enable_or_disable_motion_capture}"\
               f"{self.enable_or_disable_flash_light}" \
               f"{self.no_of_frame_capture_limit}"\
               f"{self.vdo_frame_size}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class MotionVideoFromDevice(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_info_id = models.ForeignKey(DeviceInfo, on_delete=models.CASCADE, related_name='MotionVideoFromDevice_device_info_id', verbose_name='Device info id')
    insert_date_time = models.DateTimeField(default=now, verbose_name='Insert date time')
    # -----------------------------------------------------------------------------------------------
    video_size = models.IntegerField(default=0, verbose_name='Size')
    total_frame = models.IntegerField(default=0, verbose_name='Frames')
    video_path = models.ImageField(verbose_name='Video Path')
    # -----------------------------------------------------------------------------------------------
    is_detection_applied = models.BooleanField(default=False, verbose_name='Detection Applied')
    # -----------------------------------------------------------------------------------------------
    is_motion_found = models.BooleanField(default=False, verbose_name='Is Motion')
    motion_found_frame_no = models.IntegerField(default=0, verbose_name='Motion at Frame')
    motion_found_frame_path = models.ImageField(blank=True, null=True, verbose_name='Motion Path')
    # -----------------------------------------------------------------------------------------------
    is_person_found = models.BooleanField(default=False, verbose_name='Is Person')
    person_found_frame_no = models.IntegerField(default=0, verbose_name='Person at Frame')
    person_found_frame_path = models.ImageField(blank=True, null=True, verbose_name='Person Path')
    # -----------------------------------------------------------------------------------------------
    is_alert_done = models.BooleanField(default=False, verbose_name='Is Alert Sent')
    is_alert_snooze = models.BooleanField(default=False, verbose_name='Is Alert Snooze')
    # -----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '07. Captured VDO'
        verbose_name_plural = '07. Captured VDOs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    # def short_filename(self):
    #     if self.video_path:
    #         filename = self.video_path.name  # "videos/465142496_...n.mp4"
    #         return filename[-15:]  # last 20 characters
    #     return ""
    #
    # short_filename.short_description = "Video File"
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_info_id}, " \
               f"{self.insert_date_time}, " \
               f"{self.video_size}, "\
               f"{self.total_frame}, " \
               f"{self.video_path}, " \
               f"{self.is_detection_applied}, " \
               f"{self.is_motion_found}, " \
               f"{self.motion_found_frame_no}, " \
               f"{self.motion_found_frame_path}, " \
               f"{self.is_person_found}, " \
               f"{self.person_found_frame_no}, " \
               f"{self.person_found_frame_path}, " \
               f"{self.is_alert_done}, " \
               f"{self.is_alert_snooze}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOnCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='LightAlarmOnCommand_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'B. Alarm ON CMD'
        verbose_name_plural = 'B. Alarm ON CMDs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOnLog(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_info_id = models.ForeignKey(DeviceInfo, on_delete=models.CASCADE, related_name='LightAlarmOnLog_device_info_id', verbose_name='Device info id')
    insert_date_time = models.DateTimeField(default=now, verbose_name='Insert date time')
    # -----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '08. Alarm ON Logs'
        verbose_name_plural = '08. Alarm ON Logs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_info_id}, " \
               f"{self.insert_date_time}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOffCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='LightAlarmOffCommand_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'C. Alarm OFF CMD'
        verbose_name_plural = 'C. Alarm OFF CMDs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class LightAlarmOffLog(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_info_id = models.ForeignKey(DeviceInfo, on_delete=models.CASCADE, related_name='LightAlarmOffLog_device_info_id', verbose_name='Device info id')
    insert_date_time = models.DateTimeField(default=now, verbose_name='Insert date time')
    # -----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '09. Alarm OFF Log'
        verbose_name_plural = '09. Alarm OFF Logs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_info_id}, " \
               f"{self.insert_date_time}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class WiFiSSIDPassCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='WiFiSSIDPassCommand_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    cmd_name = models.CharField(max_length=30, verbose_name='CMD Name')
    ssid = models.CharField(max_length=50, default='BS-Rokkhi', verbose_name='WiFi SSID')
    password = models.CharField(max_length=50, default='Rokkhi-4231', verbose_name='WiFi Password')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'G. WiFi SSID-Pass CMD'
        verbose_name_plural = 'G. WiFi SSID-Pass CMDs'

    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.cmd_name}" \
               f"{self.ssid}" \
               f"{self.password}"\
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class CloudIPDomainPortCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='CloudIPDomainPortCommand_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    cmd_name = models.CharField(max_length=30, verbose_name='CMD Name')
    cloud_ip = models.CharField(max_length=30, default='192.168.9.99', verbose_name='Cloud IP')
    cloud_domain = models.CharField(max_length=100, default='rokkhi.banglasolutions.com', verbose_name='Cloud Domain')
    cloud_port = models.IntegerField(default=1234, verbose_name='Cloud Port')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'H. Cloud IP Domain Port CMD'
        verbose_name_plural = 'H. Cloud IP Domain Port CMDs'

    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.cmd_name}" \
               f"{self.cloud_ip}" \
               f"{self.cloud_domain}" \
               f"{self.cloud_port}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class ResetRebootCounterCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='ResetRebootCounterCommand_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    cmd_name = models.CharField(max_length=30, verbose_name='CMD Name')
    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'I. Reset Reboot Counter CMD'
        verbose_name_plural = 'I. Reset Reboot Counter CMDs'

    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.cmd_name}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class CameraInitSettingCommand(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_id = models.OneToOneField(DeviceInfo, on_delete=models.CASCADE, related_name='CameraInitSettingCommand_device_id', verbose_name='Device ID')

    CMD_STATUS = (('processing', 'Processing'), ('done', 'Done'))
    cmd_status = models.CharField(max_length=30, choices=CMD_STATUS, default='done', verbose_name='CMD Status')

    cmd_name = models.CharField(max_length=30, verbose_name='CMD Name')
    cam_flip = models.BooleanField(default=True, verbose_name='Camera Flip')
    cam_mirror = models.BooleanField(default=True, verbose_name='Camera Mirror')

    active = models.BooleanField(default=True, verbose_name='CMD active status')
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'F. Camera Init Setting CMD'
        verbose_name_plural = 'F. Camera Init Setting CMDs'

    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_id}" \
               f"{self.cmd_status}" \
               f"{self.cmd_name}" \
               f"{self.cam_flip}" \
               f"{self.cam_mirror}" \
               f"{self.active}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************


# ***************************************************************************************************************
class DevTempLog(models.Model):
    # ----------------------------------------------------------------------------------------------
    device_info_id = models.ForeignKey(DeviceInfo, on_delete=models.CASCADE, related_name='DevTempLog_device_info_id', verbose_name='Device info id')
    insert_date_time = models.DateTimeField(default=now, verbose_name='Insert date time')
    dev_temp = models.CharField(max_length=10, blank=True, null=True, verbose_name='Device Temperature')
    # -----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = 'J. Temperature Log'
        verbose_name_plural = 'J. Temperature Logs'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.device_info_id}, " \
               f"{self.dev_temp}" \
               f"{self.insert_date_time}"
    # ----------------------------------------------------------------------------------------------
# ***************************************************************************************************************
