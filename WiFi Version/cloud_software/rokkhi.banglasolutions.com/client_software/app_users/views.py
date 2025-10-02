# ----------------------------------------------------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Subquery, OuterRef
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from datetime import datetime, timedelta, time
from django.db.models import Q
from . form import SignMeUpForm, SignMeInForm, AvatarForm, ChangeMyPasswordForm, ForgotPasswordForm, RecoverPasswordForm
from . models import Profile
import pytz, socket, math, json, os, re
from django.core import serializers
from django.contrib import auth, messages
from django.contrib.auth import logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# from app_products.models import Category, SubCategory, SubSubCategory, MostPopularProduct
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import forms, UserCreationForm
from app_devices.models import *
from app_devices.models import *
from . form import *
# ----------------------------------------------------------------------------------------------


# **********************************************************************************************
def check_email_validity(email):
    # re module provides support for regular expressions
    # Make a regular expression
    # for validating an Email
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    # pass the regular expression and the string in search() method
    if re.search(regex, email):
        return 1
    else:
        return 0
# **********************************************************************************************


# **********************************************************************************************
def check_mobile_no_validity(mobile_no):
    # cell_no = '+88 016-1T8,35,a44,@$4s4'
    # print('mobile_no:', mobile_no)
    # ----------------------------------------------------------------------------------------------
    mobile_no_cleaned = re.sub("\D", '', mobile_no)
    # print('mobile_no_cleaned:', mobile_no_cleaned)
    """
    \D matches any non-digit character.
     So, the code above, is essentially replacing every non-digit character.
    """
    # ----------------------------------------------------------------------------------------------
    start_with_88 = mobile_no_cleaned.startswith('88')
    # print('start_with_88:', start_with_88)
    start_with_01 = mobile_no_cleaned.startswith('01')
    # print('start_with_01:', start_with_01)
    # ----------------------------------------------------------------------------------------------
    mobile_no_validity = False

    if start_with_88:
        if len(mobile_no_cleaned) == 13:
            mobile_no_validity = True
    elif start_with_01:
        if len(mobile_no_cleaned) == 11:
            mobile_no_validity = True

    # print('mobile_no_validity:', mobile_no_validity)
    # ----------------------------------------------------------------------------------------------
    return mobile_no_validity
# **********************************************************************************************


# **********************************************************************************************
def check_meter_status(meter_no):
    meter_status = 'Unknown'

    last_10_values = PhotoFromDevice.objects.filter(
        device_info_id__dev_sl=meter_no,
        reading_valid=True).values_list(
        'meter_reading',
        flat=True).order_by(
        '-insert_date_time')[:20]

    # print('Latest 10 Values of Meter No: ' + meter_no + ':', last_10_values)
    # ----------------------------------------------------------------------------------
    if len(last_10_values) >= 20:
        # Above check is required else "List Len" exception occurred when 10 data not available at initial stage
        if last_10_values[0] == last_10_values[1] == last_10_values[2] == last_10_values[3] == last_10_values[4] == last_10_values[5] == last_10_values[6] == last_10_values[7] == last_10_values[8] == last_10_values[9] == last_10_values[10] == last_10_values[11] == last_10_values[12] == last_10_values[13] == last_10_values[14] == last_10_values[15] == last_10_values[16] == last_10_values[17] == last_10_values[18] == last_10_values[19]:
            meter_status = 'Paused'
        elif last_10_values[0] >= last_10_values[1] >= last_10_values[2] >= last_10_values[3] >= last_10_values[4] >= last_10_values[5] >= last_10_values[6] >= last_10_values[7] >= last_10_values[8] >= last_10_values[9] >= last_10_values[10] >= last_10_values[11] >= last_10_values[12] >= last_10_values[13] >= last_10_values[14] >= last_10_values[15] >= last_10_values[16] >= last_10_values[17] >= last_10_values[18] >= last_10_values[19]:
            meter_status = 'Running'
        elif last_10_values[0] <= last_10_values[1] <= last_10_values[2] <= last_10_values[3] <= last_10_values[4] <= last_10_values[5] <= last_10_values[6] <= last_10_values[7] <= last_10_values[8] < last_10_values[9] < last_10_values[10] < last_10_values[11] < last_10_values[12] < last_10_values[13] < last_10_values[14] < last_10_values[15] < last_10_values[16] < last_10_values[17] < last_10_values[18] < last_10_values[19]:
            meter_status = 'Reverse Running'
    # ----------------------------------------------------------------------------------
    # print('Status of Meter No: ' + meter_no + ':', meter_status)
    # ----------------------------------------------------------------------------------
    return meter_status
# **********************************************************************************************


# **********************************************************************************************
def sign_me_up(request):
    try:
        if request.method == 'POST':
            try:
                # ------------------------------------------------------------------------------------------------
                # Primary validation checking (Manual)
                username = request.POST['username']
                # print('username:', username)
                email = request.POST['email']
                # print('email:', email)
                password = request.POST['password1']
                # print('password:', password)
                confirm_password = request.POST['password2']
                # print('confirm_password:', confirm_password)
                failed_flag = 0
                # ------------------------------------------------------------------------------------------------
                if not username or not email or not password or not confirm_password:
                    messages.warning(request, 'No empty field allowed!', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if not check_mobile_no_validity(username):
                    messages.warning(request, 'Incorrect mobile number!\nUse format like: 8801xxxxxxxxx, 01xxxxxxxxx', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if not check_email_validity(email):
                    messages.warning(request, 'Email address format incorrect!', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if password != confirm_password:
                    messages.warning(request, 'Password and confirm password didn\'t match!', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if User.objects.filter(username=username).exists():
                    messages.warning(request, 'Mobile number already exists!', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if User.objects.filter(email=email).exists():
                    messages.warning(request, 'Email address already exists!', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if failed_flag:
                    messages.error(request, 'New user creation failed!', fail_silently=False)
                    return sign_me_out(request)
                # ------------------------------------------------------------------------------------------------
                sign_me_up_form = SignMeUpForm(request.POST)

                if sign_me_up_form.is_valid():
                    sign_me_up_form.full_clean()
                    username = sign_me_up_form.cleaned_data.get('username')
                    # print('username:', username)
                    email = sign_me_up_form.cleaned_data.get('email')
                    # print('email:', email)
                    # ------------------------------------------------------------------------------------------------
                    user = sign_me_up_form.save(commit=False)
                    user.is_active = True
                    # ------------------------------------------------------------------------------------------------
                    # Send user activation email
                    current_site = get_current_site(request)
                    mail_subject = 'Please Activate your account'
                    # ------------------------------------------------------------------------------------------------
                    message = render_to_string('app_users/account_verification_email.html', {
                        'email': email,
                        'domain': current_site,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                    })
                    # ------------------------------------------------------------------------------------------------
                    email_to = email
                    send_email = EmailMessage(mail_subject, message, to=[email_to])
                    send_email.send()
                    # print('Email sent success!')
                    # ------------------------------------------------------------------------------------------------
                    user.save()
                    # ------------------------------------------------------------------------------------------------
                    messages.success(request, 'Congrats! Your account create success :)', fail_silently=False)
                    messages.info(request, 'Please check your email and activate the account. Don\'t forget to check spam folder', fail_silently=False)
                    return sign_me_out(request)
                # ------------------------------------------------------------------------------------------------
                else:
                    print('Form validity problem!')
                    messages.error(request, 'New user creation failed!', fail_silently=False)
                    return redirect('sign_me_up')
            # ------------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:sign_me_up:', e)
                messages.error(request, 'New user creation failed!', fail_silently=False)
                return redirect('sign_me_up')
        # ----------------------------------------------------------------------------------
        sign_me_up_form = SignMeUpForm()

        return render(request, 'app_users/sign_me_up.html', {
            'sign_me_up_form': sign_me_up_form,
        })
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:sign_me_up:', e)
        messages.error(request, e, fail_silently=False)
        return sign_me_out(request)
# **********************************************************************************************


# **********************************************************************************************
def sign_me_in(request):
    try:
        if request.method == 'POST':
            # ------------------------------------------------------------------------------------------------
            # Primary validation checking (Manual)
            username = request.POST['username']
            # print('username:', username)
            password = request.POST['password']
            # print('password:', password)
            # ------------------------------------------------------------------------------------------------
            if not username or not password:
                messages.error(request, 'Username or Password can\'t be empty!', fail_silently=False)
                return sign_me_out(request)
            # ------------------------------------------------------------------------------------------------
            sign_me_in_form = SignMeInForm(request.POST)
            # ------------------------------------------------------------------------------------------------
            if sign_me_in_form.is_valid():
                # print('sign_me_in_form valid!')
                username = sign_me_in_form.cleaned_data['username']
                password = sign_me_in_form.cleaned_data['password']
                # ----------------------------------------------------------------------------------
                user = auth.authenticate(username=username, password=password)
                # ----------------------------------------------------------------------------------
                if not user:
                    messages.error(request, 'Wrong Username or password!', fail_silently=False)
                    return sign_me_out(request)
                # ----------------------------------------------------------------------------------
                acc_status = user.profile.acc_status
                # ----------------------------------------------------------------------------------
                if not acc_status:
                    messages.info(request, 'Your account exists but not activated. Please contact to customer care', fail_silently=False)
                    return sign_me_out(request)
                # ----------------------------------------------------------------------------------
                if user and acc_status:
                    auth.login(request, user)
                    return redirect('user_dashboard')
                else:
                    messages.error(request, 'Something went wrong. Please try again!', fail_silently=False)
                    return sign_me_out(request)
            # ----------------------------------------------------------------------------------
            else:
                messages.error(request, 'Something went wrong. Please try again!', fail_silently=False)
                return sign_me_out(request)
        # ----------------------------------------------------------------------------------
        return sign_me_out(request)
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:sign_me_in:', e)
        messages.error(request, e, fail_silently=False)
        return sign_me_out(request)
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def sign_me_out(request):
    logout(request)

    return redirect('/')
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def change_my_photo(request):
    try:
        # ----------------------------------------------------------------------------------
        if request.method == 'POST':
            user_info = request.user.profile
            avatar_form = AvatarForm(request.POST, request.FILES, instance=user_info)

            if avatar_form.is_valid():
                # ----------------------------------------------------------------------------------
                try:
                    file_name = request.FILES['avatar'].name
                    file_size = request.FILES['avatar'].size
                    print("file_name", file_name)
                    print("file_size", type(file_size))
                    # ----------------------------------------------------------------------------------
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        pass
                    else:
                        messages.warning(request, 'You have selected wrong file type :(', fail_silently=False)
                        return redirect('user_dashboard')
                    # ----------------------------------------------------------------------------------
                    if file_size <= 512000:
                        pass
                    else:
                        messages.warning(request, 'File size must be in 500KB :(', fail_silently=False)
                        return redirect('user_dashboard')
                # ----------------------------------------------------------------------------------
                except Exception as e:
                    print('e:change_my_photo:', e)
                    messages.warning(request, 'Empty field not allowed :(', fail_silently=False)
                    return redirect('user_dashboard')
                # ----------------------------------------------------------------------------------
                avatar_form.save()
                messages.success(request, 'Your photo successfully updated!', fail_silently=False)
                return redirect('user_dashboard')
            else:
                messages.error(request, 'You have input wrong file :(\nTry again', fail_silently=False)
                return redirect('user_dashboard')
        # ----------------------------------------------------------------------------------
        else:
            avatar_form = AvatarForm()

            return render(request, 'app_users/change_avatar.html', {
                'avatar_form': avatar_form,
                'current_year': datetime.now().year,
            })
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:change_my_photo:', e)
        messages.error(request, 'Photo update failed :(\nPlease try again', fail_silently=False)
        return redirect('user_dashboard')
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def change_my_password(request):
    try:
        if request.method == 'POST':
            # ------------------------------------------------------------------------------------------------
            old_password = request.POST['old_password']
            # print('old_password:', old_password)
            new_password1 = request.POST['new_password1']
            # print('new_password1:', new_password1)
            new_password2 = request.POST['new_password2']
            # print('new_password1:', new_password1)
            failed_flag = 0
            # ------------------------------------------------------------------------------------------------
            if not old_password or not new_password1 or not new_password2:
                messages.warning(request, 'No empty field allowed!', fail_silently=False)
                failed_flag = 1
            # ------------------------------------------------------------------------------------------------
            if new_password1 != new_password2:
                messages.warning(request, 'Password and confirm password didn\'t match!', fail_silently=False)
                failed_flag = 1
            # ------------------------------------------------------------------------------------------------
            if failed_flag:
                messages.error(request, 'Password change failed!', fail_silently=False)
                return redirect('user_dashboard_dm')
            # ------------------------------------------------------------------------------------------------
            change_my_password_form = ChangeMyPasswordForm(data=request.POST, user=request.user)

            if change_my_password_form.is_valid():
                change_my_password_form.full_clean()
                change_my_password_form.save()
                messages.success(request, 'Password change success!\nPlease login again', fail_silently=False)
                logout(request)
                return sign_me_out(request)
            else:
                messages.error(request, 'Password change failed :(', fail_silently=False)
                logout(request)
                return redirect('user_dashboard_dm')
        # ----------------------------------------------------------------------------------
        else:
            change_my_password_form = ChangeMyPasswordForm(data=request.POST, user=request.user)

            return render(request, 'app_users/change_password.html', {
                'change_my_password_form': change_my_password_form,
                'current_year': datetime.now().year,
            })
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:change_my_password:', e)
        messages.error(request, 'Password change failed :(\nPlease try again', fail_silently=False)
        return sign_me_out(request)
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def user_dashboard(request):
    try:
        # ------------------------------------------------------------------------------------------------
        my_cameras = DeviceInfo.objects.filter(dev_user=request.user)
        # print('my_cameras:', my_cameras)
        img_resolution = ImageResolutionList.objects.filter(active=True)
        # print('img_resolution:', img_resolution)
        flash = FlashlightList.objects.filter(active=True)
        # print('flash:', flash)

        # for a in my_cameras:
        #     print(a.DeviceHeartbeat_device_info_id.hb_time)
        #     print(a.PhotoFromDevice_device_info_id.all().values_list())

        # queryset = DeviceInfo.objects.prefetch_related('DeviceHeartbeat_device_info_id', 'PhotoFromDevice_device_info_id').all()
        # print('queryset:', queryset)
        #
        # for a in queryset:
        #     print(a)
        #     # Access related objects from B
        #     for b in a.DeviceHeartbeat_device_info_id.all():
        #         print(b)
        #     # Access related objects from C
        #     for c in a.PhotoFromDevice_device_info_id.all():
        #         print(c)

        # ----------------------------------------------------------------------------------
        return render(request, 'app_users/user_dashboard.html', {
            'my_cameras': my_cameras,
            'img_resolution': img_resolution,
            'flash': flash,
        })
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:user_dashboard:', e)
        messages.error(request, e, fail_silently=False)
        return redirect('/')
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def capture_image(request):
    try:
        if request.method == 'POST':
            try:
                # ------------------------------------------------------------------------------------------------
                # Primary validation checking (Manual)
                dev_id_pk = request.POST.get('dev_id_pk', '')
                # print('dev_id_pk:', dev_id_pk)
                resolution = request.POST.get('resolution', '')
                # print('resolution:', resolution)
                flashlight = request.POST.get('flash', '')
                # print('flashlight:', flashlight)
                # ------------------------------------------------------------------------------------------------
                if not dev_id_pk or resolution == 'x' or flashlight == 'x':
                    messages.warning(request, 'Wrong option(s) selected', fail_silently=False)
                    return redirect('user_dashboard')
                # ------------------------------------------------------------------------------------------------
                img_cap_cmd_obj = ImageCaptureCommand.objects.get(device_id=dev_id_pk)
                img_cap_cmd_obj.resolution_id = ImageResolutionList.objects.get(cmd=resolution)
                img_cap_cmd_obj.flashlight = flashlight
                img_cap_cmd_obj.cmd_status = 'processing'
                img_cap_cmd_obj.save()
                # ------------------------------------------------------------------------------------------------
                dev_obj = DeviceInfo.objects.get(pk=dev_id_pk)
                dev_obj.busy_status = True
                dev_obj.save()
                # ------------------------------------------------------------------------------------------------
                messages.success(request, 'Operation success!', fail_silently=False)
                return redirect('user_dashboard')
            # ------------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:capture_image:', e)
                messages.error(request, 'Something went wrong :(', fail_silently=False)
                return redirect('user_dashboard')
        # ----------------------------------------------------------------------------------
        print('Not a POST request!')
        messages.error(request, 'Not a POST request!', fail_silently=False)
        return redirect('user_dashboard')
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:capture_image:', e)
        messages.error(request, e, fail_silently=False)
        return redirect('user_dashboard')
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def alarm_light_on(request):
    try:
        if request.method == 'POST':
            try:
                # ------------------------------------------------------------------------------------------------
                # Primary validation checking (Manual)
                dev_id_pk = request.POST.get('dev_id_pk', '')
                # print('dev_id_pk:', dev_id_pk)
                alarm_light_on = request.POST.get('alarm_light_on_off', '')
                # print('alarm_light_on:', alarm_light_on)
                # ------------------------------------------------------------------------------------------------
                light_alarm_cmd_obj = LightAlarmOnCommand.objects.get(device_id=dev_id_pk, active=True)
                light_alarm_cmd_obj.cmd_status = 'processing'
                light_alarm_cmd_obj.save()
                # ------------------------------------------------------------------------------------------------
                dev_obj = DeviceInfo.objects.get(pk=dev_id_pk)
                dev_obj.busy_status = True
                dev_obj.save()
                # ------------------------------------------------------------------------------------------------
                messages.success(request, 'Operation success!', fail_silently=False)
                return redirect('user_dashboard')
            # ------------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:alarm_light_on:', e)
                messages.error(request, 'Something went wrong :(', fail_silently=False)
                return redirect('user_dashboard')
        # ----------------------------------------------------------------------------------
        print('Not a POST request!')
        messages.error(request, 'Not a POST request!', fail_silently=False)
        return redirect('user_dashboard')
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:alarm_light_on:', e)
        messages.error(request, e, fail_silently=False)
        return redirect('user_dashboard')
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def alarm_light_off(request):
    try:
        if request.method == 'POST':
            try:
                # ------------------------------------------------------------------------------------------------
                # Primary validation checking (Manual)
                dev_id_pk = request.POST.get('dev_id_pk', '')
                # print('dev_id_pk:', dev_id_pk)
                alarm_light_off = request.POST.get('alarm_light_on_off', '')
                # print('alarm_light_off:', alarm_light_off)
                # ------------------------------------------------------------------------------------------------
                light_alarm_cmd_obj = LightAlarmOffCommand.objects.get(device_id=dev_id_pk, active=True)
                light_alarm_cmd_obj.cmd_status = 'processing'
                light_alarm_cmd_obj.save()
                # ------------------------------------------------------------------------------------------------
                dev_obj = DeviceInfo.objects.get(pk=dev_id_pk)
                dev_obj.busy_status = True
                dev_obj.save()
                # ------------------------------------------------------------------------------------------------
                messages.success(request, 'Operation success!', fail_silently=False)
                return redirect('user_dashboard')
            # ------------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:alarm_light_off:', e)
                messages.error(request, 'Something went wrong :(', fail_silently=False)
                return redirect('user_dashboard')
        # ----------------------------------------------------------------------------------
        print('Not a POST request!')
        messages.error(request, 'Not a POST request!', fail_silently=False)
        return redirect('user_dashboard')
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:alarm_light_off:', e)
        messages.error(request, e, fail_silently=False)
        return redirect('user_dashboard')
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def change_working_mode(request, dev_sl):
    try:
        if request.method == 'POST':
            try:
                # ------------------------------------------------------------------------------------------------
                # Primary validation checking (Manual)
                dev_sl = request.POST.get('dev_sl', '')
                # print('dev_sl:', dev_sl)
                work_mode = request.POST.get('work_mode', '')
                # print('work_mode:', work_mode)
                start_time = request.POST.get('start_time', '')
                # print('start_time:', start_time)
                end_time = request.POST.get('end_time', '')
                # print('end_time:', end_time)
                # ------------------------------------------------------------------------------------------------
                if work_mode == 'x':
                    messages.warning(request, 'Nothing selected!', fail_silently=False)
                    return redirect('user_dashboard')
                # ------------------------------------------------------------------------------------------------
                elif work_mode == 'schedule' and (not start_time or not end_time):
                    messages.warning(request, 'Both Start Time and End Time needed!', fail_silently=False)
                    return redirect('user_dashboard')
                # ------------------------------------------------------------------------------------------------
                elif work_mode == 'schedule' and start_time and end_time:
                    dev_obj = DeviceInfo.objects.get(dev_sl=dev_sl)
                    dev_obj.dev_active_mode=work_mode
                    dev_obj.dev_active_hour_start = start_time
                    dev_obj.dev_active_hour_end = end_time
                    dev_obj.save()
                    # ------------------------------------------------------------------------------------------------
                    messages.success(request, 'Schedule set success :)', fail_silently=False)
                    return redirect('user_dashboard')
                # ------------------------------------------------------------------------------------------------
                elif work_mode == 'always on':
                    dev_obj = DeviceInfo.objects.get(dev_sl=dev_sl)
                    dev_obj.dev_active_mode = work_mode
                    dev_obj.active_status = 1
                    dev_obj.save()
                    # ------------------------------------------------------------------------------------------------
                    messages.success(request, 'Always ON set OK :)', fail_silently=False)
                    return redirect('user_dashboard')
                # ------------------------------------------------------------------------------------------------
                elif work_mode == 'manual':
                    dev_obj = DeviceInfo.objects.get(dev_sl=dev_sl)
                    dev_obj.dev_active_mode = work_mode
                    dev_obj.active_status = 0
                    dev_obj.save()
                    # ------------------------------------------------------------------------------------------------
                    messages.success(request, 'Manual Mode set OK :)', fail_silently=False)
                    return redirect('user_dashboard')
                # ------------------------------------------------------------------------------------------------
                elif work_mode == 'disable':
                    dev_obj = DeviceInfo.objects.get(dev_sl=dev_sl)
                    dev_obj.dev_active_mode = work_mode
                    dev_obj.active_status = 5
                    dev_obj.save()
                    # ------------------------------------------------------------------------------------------------
                    messages.success(request, 'Motion Alart Disabled OK!', fail_silently=False)
                    return redirect('user_dashboard')
                 # ------------------------------------------------------------------------------------------------
                else:
                    messages.error(request, 'Motion Alart Disabled OK!', fail_silently=False)
                    return redirect('user_dashboard')
            # ------------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:change_working_mode:', e)
                messages.error(request, 'Something went wrong :(', fail_silently=False)
                return redirect('user_dashboard')
        # ----------------------------------------------------------------------------------
        else:
            return render(request, 'app_users/change_working_mode.html', {
                'dev_sl': dev_sl,
            })
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:change_working_mode:', e)
        messages.error(request, e, fail_silently=False)
        return redirect('user_dashboard')
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def manually_activate_deactivate(request, dev_sl, act_deact):
    try:
        print('dev_sl:', dev_sl)
        print('act_deact:', act_deact)
        # ------------------------------------------------------------------------------------------------
        dev_obj = DeviceInfo.objects.get(dev_sl=dev_sl)
        dev_obj.active_status = act_deact
        dev_obj.save()
        # ------------------------------------------------------------------------------------------------
        messages.success(request, 'Set Ok :)', fail_silently=False)
        return redirect('user_dashboard')
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:manually_activate_deactivate:', e)
        messages.error(request, e, fail_silently=False)
        return redirect('user_dashboard')
# **********************************************************************************************




# **********************************************************************************************
@login_required(login_url='/')
def single_meter_log(request, meter_id):
    try:
        # print('request.user.groups.all().get().name:', request.user.groups.all().get().name)

        if request.user.groups.all().get().name == 'Admin':
            # ----------------------------------------------------------------------------------
            last_hb = DeviceHeartbeat.objects.get(device_info_id__dev_sl=meter_id).hb_time
            # print('last_hb:', last_hb)
            dev_info = DeviceInfo.objects.get(dev_sl=meter_id)
            # print('dev_info:', dev_info)

            all_imgs = PhotoFromDevice.objects.filter(device_info_id__dev_sl=meter_id).order_by('-insert_date_time')[:1000]
            # print('all_imgs:', all_imgs)
            # ----------------------------------------------------------------------------------
            return render(request, 'app_users/single_meter_log.html', {
                'last_hb': last_hb,
                'dev_info': dev_info,
                'all_imgs': all_imgs,
            })
        # ----------------------------------------------------------------------------------
        elif request.user.groups.all().get().name == 'Guest':
            # ----------------------------------------------------------------------------------
            last_hb = DeviceHeartbeat.objects.get(device_info_id__dev_sl=meter_id).hb_time
            # print('last_hb:', last_hb)
            dev_info = DeviceInfo.objects.get(dev_sl=meter_id)
            # print('dev_info:', dev_info)

            all_imgs = PhotoFromDevice.objects.filter(
                device_info_id__dev_sl=meter_id,
                reading_valid=True
            ).order_by('-insert_date_time')[:100]
            # print('all_imgs:', all_imgs)
            # ----------------------------------------------------------------------------------
            return render(request, 'app_users/single_meter_log_guest.html', {
                'last_hb': last_hb,
                'dev_info': dev_info,
                'all_imgs': all_imgs,
            })
        # ----------------------------------------------------------------------------------
        elif request.user.groups.all().get().name == 'TestLab':
            # ----------------------------------------------------------------------------------
            last_hb = DeviceHeartbeat.objects.get(device_info_id__dev_sl=meter_id).hb_time
            # print('last_hb:', last_hb)
            dev_info = DeviceInfo.objects.get(dev_sl=meter_id)
            # print('dev_info:', dev_info)

            all_imgs = PhotoFromDevice.objects.filter(
                device_info_id__dev_sl=meter_id,
                reading_valid=True
            ).order_by('-insert_date_time')[:100]
            # print('all_imgs:', all_imgs)
            # ----------------------------------------------------------------------------------
            return render(request, 'app_users/single_meter_log_guest.html', {
                'last_hb': last_hb,
                'dev_info': dev_info,
                'all_imgs': all_imgs,
            })
        # ----------------------------------------------------------------------------------
        else:
            return sign_me_out(request)
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:single_meter_log:', e)
        messages.error(request, e, fail_silently=False)
        return sign_me_out(request)
# **********************************************************************************************


# **********************************************************************************************
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception as e:
        print('e:', e)
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.profile.acc_status = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated. You can login now')
        return redirect('sign_me_in')
    else:
        messages.error(request, 'Invalid activation link')
        return sign_me_out(request)
# **********************************************************************************************


# **********************************************************************************************
def forgot_password(request):
    try:
        if request.method == 'POST':
            try:
                # ------------------------------------------------------------------------------------------------
                # Primary validation checking (Manual)
                username = request.POST['username']
                # print('username:', username)
                email = request.POST['email']
                # print('email:', email)
                failed_flag = 0
                # ------------------------------------------------------------------------------------------------
                if not username or not email:
                    messages.warning(request, 'No empty field allowed!', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if not check_mobile_no_validity(username):
                    messages.warning(request, 'Incorrect mobile number!\nUse format like: 8801xxxxxxxxx, 01xxxxxxxxx', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if not check_email_validity(email):
                    messages.warning(request, 'Email address format incorrect!', fail_silently=False)
                    failed_flag = 1
                # ------------------------------------------------------------------------------------------------
                if failed_flag:
                    return sign_me_out(request)
                # ------------------------------------------------------------------------------------------------
                if User.objects.filter(username=username, email=email, profile__acc_status=True).exists():
                    # print('Record found')
                    forgot_password_form = ForgotPasswordForm(request.POST)

                    if forgot_password_form.is_valid():
                        forgot_password_form.full_clean()
                        username = forgot_password_form.cleaned_data.get('username')
                        # print('username:', username)
                        email = forgot_password_form.cleaned_data.get('email')
                        # print('email:', email)
                        # ------------------------------------------------------------------------------------------------
                        user = User.objects.get(username=username, email=email, profile__acc_status=True)
                        # ------------------------------------------------------------------------------------------------
                        # Send user email
                        current_site = get_current_site(request)
                        mail_subject = 'Reset your password'

                        message = render_to_string('app_users/forgot_password_email.html', {
                            'email': email,
                            'domain': current_site,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': default_token_generator.make_token(user),
                        })
                        email_to = email
                        send_email = EmailMessage(mail_subject, message, to=[email_to])
                        send_email.send()
                        # print('Email sent success!')
                        messages.success(request, 'Password reset email has been sent', fail_silently=False)
                        messages.info(request, 'Please check your email. Don\'t forget to check spam folder', fail_silently=False)
                        return sign_me_out(request)
                    # ------------------------------------------------------------------------------------------------
                    else:
                        print('Form validity problem!')
                        messages.error(request, 'Something went wrong :(', fail_silently=False)
                        return sign_me_out(request)
                # ------------------------------------------------------------------------------------------------
                else:
                    messages.warning(request, 'No Record found', fail_silently=False)
                    return sign_me_out(request)
                # ------------------------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:forgot_password:', e)
                messages.error(request, 'Something went wrong :(', fail_silently=False)
                return sign_me_out(request)
        # ----------------------------------------------------------------------------------
        forgot_password_form = ForgotPasswordForm()

        return render(request, 'app_users/forgot_password.html', {
            'forgot_password_form': forgot_password_form,
        })
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:forgot_password:', e)
        messages.error(request, e, fail_silently=False)
        return sign_me_out(request)
# **********************************************************************************************


# **********************************************************************************************
def forgot_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        # ----------------------------------------------------------------------------------
        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid

            if request.method == 'POST':
                try:
                    # ------------------------------------------------------------------------------------------------
                    password = request.POST['password1']
                    # print('password:', password)
                    confirm_password = request.POST['password2']
                    # print('confirm_password:', confirm_password)
                    failed_flag = 0
                    # ------------------------------------------------------------------------------------------------
                    if not password or not confirm_password:
                        messages.warning(request, 'No empty field allowed!', fail_silently=False)
                        failed_flag = 1
                    # ------------------------------------------------------------------------------------------------
                    if password != confirm_password:
                        messages.warning(request, 'Password and confirm password didn\'t match!', fail_silently=False)
                        failed_flag = 1
                    # ------------------------------------------------------------------------------------------------
                    if failed_flag:
                        return sign_me_out(request)
                    # ------------------------------------------------------------------------------------------------
                    recover_password_form = RecoverPasswordForm(request.POST)

                    if recover_password_form.is_valid():
                        recover_password_form.full_clean()
                        # ------------------------------------------------------------------------------------------------
                        password = recover_password_form.cleaned_data.get('password1')
                        confirm_password = recover_password_form.cleaned_data.get('password2')
                        # ------------------------------------------------------------------------------------------------
                        uid = request.session.get('uid')
                        user = User.objects.get(pk=uid)
                        user.set_password(password)
                        user.save()
                        del request.session['uid']
                        # ------------------------------------------------------------------------------------------------
                        messages.success(request, 'New password set success :)', fail_silently=False)
                        return sign_me_out(request)
                    # ------------------------------------------------------------------------------------------------
                    else:
                        print('Form validity problem!')
                        messages.error(request, 'New password set failed!', fail_silently=False)
                        return sign_me_out(request)
                # ------------------------------------------------------------------------------------------------
                except Exception as e:
                    print('e:forgot_password_validate:', e)
                    messages.error(request, 'Password recovery failed!', fail_silently=False)
                    return sign_me_out(request)
            # ------------------------------------------------------------------------------------------------
            else:
                recover_password_form = RecoverPasswordForm()

                return render(request, 'app_users/reset_password.html', {
                    'recover_password_form': recover_password_form,
                })
        else:
            messages.error(request, 'Invalid link!', fail_silently=False)
            return sign_me_out(request)
    except Exception as e:
        print('User does not exist :(')
        print('e:', e)
        messages.error(request, 'Something went wrong :(', fail_silently=False)
        return sign_me_out(request)
# **********************************************************************************************


# **********************************************************************************************
@login_required(login_url='/')
def image_capture_command(request):
    try:
        if request.method == 'POST':
            try:
                # ------------------------------------------------------------------------------------------------
                # Primary validation checking (Manual)
                device_id = request.POST['device_id']
                # print('device_id:', device_id)
                resolution = request.POST['resolution']
                # print('resolution:', resolution)
                flashlight = request.POST['flashlight']
                # print('flashlight:', flashlight)
                cmd_status = request.POST['cmd_status']
                # print('cmd_status:', cmd_status)
                # ------------------------------------------------------------------------------------------------
                if not device_id or not resolution or not flashlight or not cmd_status:
                    messages.warning(request, 'No empty field allowed!', fail_silently=False)
                    return redirect('user_dashboard')
                if device_id not in str(Profile.objects.get(user=request.user).assigned_cameras.filter(active=True)):
                    messages.warning(request, 'You are not allowed for this camera!', fail_silently=False)
                    return redirect('user_dashboard')
                if not ImageResolutionList.objects.filter(cmd=resolution):
                    messages.warning(request, 'Select a correct image resolution!', fail_silently=False)
                    return redirect('user_dashboard')
                if not FlashlightList.objects.filter(cmd=flashlight):
                    messages.warning(request, 'Select a correct flashlight option!', fail_silently=False)
                    return redirect('user_dashboard')
                if not ImageCaptureCommand.objects.filter(cmd_status=cmd_status):
                    messages.warning(request, 'Invalid command status!', fail_silently=False)
                    return redirect('user_dashboard')
                # ------------------------------------------------------------------------------------------------
                img_cap_cmd_obj = ImageCaptureCommand.objects.get(device_id=DeviceInfo.objects.get(dev_sl=device_id))
                # print('img_cap_cmd_obj:', img_cap_cmd_obj)
                img_cap_cmd_obj.resolution = ImageResolutionList.objects.get(cmd=resolution)
                img_cap_cmd_obj.flashlight = FlashlightList.objects.get(cmd=flashlight)
                img_cap_cmd_obj.cmd_status = 'processing'
                img_cap_cmd_obj.save()
                # ------------------------------------------------------------------------------------------------
                messages.success(request, 'Operation success!', fail_silently=False)
                return redirect('user_dashboard')
            # ------------------------------------------------------------------------------------------------
            except Exception as e:
                print('e:image_capture_command:', e)
                messages.error(request, 'Something went wrong :(', fail_silently=False)
                return redirect('user_dashboard')
        # ----------------------------------------------------------------------------------
        print('Not a POST request!')
        messages.error(request, 'Not a POST request!', fail_silently=False)
        return redirect('user_dashboard')
    # ----------------------------------------------------------------------------------
    except Exception as e:
        print('e:image_capture_command:', e)
        messages.error(request, e, fail_silently=False)
        return redirect('user_dashboard')
# **********************************************************************************************
