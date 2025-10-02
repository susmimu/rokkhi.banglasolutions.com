# # ----------------------------------------------------------------------------------------------
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.utils.timezone import now
# from django.contrib.auth.models import User, Group
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
# from datetime import datetime, timedelta, time
# from datetime import datetime, timezone
# from django.db.models import Q
# from app_vehicles.models import VehicleInfo
# import pytz, socket, math, json, os, re
# from django.core import serializers
# from django.contrib import auth, messages
# from django.contrib.auth import logout
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.forms import forms, UserCreationForm
# from app_devices.models import GpsDataFromDevice, DeviceHeartbeat
# from app_users.models import Profile
# # ----------------------------------------------------------------------------------------------
#
#
# # **********************************************************************************************
# def is_this_user_authorized_for_this_vts(request, dev_hid):
#     # print('dev_hid:', dev_hid)
#     if Profile.objects.get(user=request.user).assigned_vehicles.filter(installed_vts__hid__hid__exact=dev_hid, installed_vts__active=True):
#         return 1
#     else:
#         return 0
# # **********************************************************************************************
#
#
# # **********************************************************************************************
# @login_required(login_url='/')
# def live_tracking(request, dev_hid):
#     try:
#         if is_this_user_authorized_for_this_vts(request, dev_hid):
#             # print('dev_hid:', dev_hid)
#             try:
#                 # ----------------------------------------------------------------------------------
#                 # Collect Other Data
#                 vehicle_name_qs = VehicleInfo.objects.filter(installed_vts__hid__hid__exact=dev_hid).values('name_or_no').get()
#                 # print('vehicle_name_qs:', vehicle_name_qs)
#                 vehicle_name = vehicle_name_qs['name_or_no']
#                 # print('vehicle_name:', vehicle_name)
#                 # ----------------------------------------------------------------------------------
#                 # Collect GPS Data
#                 # latest_packet_qs = GpsDataFromDevice.objects.filter(device_info_id__hid__hid=dev_hid).values().latest('pk')
#                 # print('latest_packet_qs:', latest_packet_qs)
#                 latest_packet_qs = GpsDataFromDevice.objects.filter(device_info_id__hid__hid=dev_hid).values(
#                     'insert_date_time',
#                     'no_of_satellite',
#                     'lat',
#                     'lon',
#                     'speed',
#                     'gps_status_bit4',
#                     'course_decimal_val',
#                     'mcc',
#                     'mnc',
#                     'lac',
#                     'cell_id',
#                     'acc',
#                     'hb_time',
#                     'hb_defence',
#                     'hb_acc',
#                     'hb_charge',
#                     'hb_gps_tracking',
#                     'hb_built_in_bat_level',
#                     'hb_gsm_signal_strength').latest('pk')
#                 # print('latest_packet_qs:', latest_packet_qs)
#                 # ----------------------------------------------------------------------------------
#                 gps_insert_time = (latest_packet_qs['insert_date_time'] + timedelta(hours=6)).strftime("%d-%m-%y, %I:%M %p")
#                 # print('gps_insert_time:', gps_insert_time)
#                 gps_no_of_satellite = latest_packet_qs['no_of_satellite']
#                 # print('gps_no_of_satellite:', gps_no_of_satellite)
#                 gps_lat = latest_packet_qs['lat']
#                 # print('gps_lat:', gps_lat)
#                 gps_lon = latest_packet_qs['lon']
#                 # print('gps_lon:', gps_lon)
#                 gps_speed = latest_packet_qs['speed']
#                 # print('gps_speed:', gps_speed)
#                 gps_positioned_status = latest_packet_qs['gps_status_bit4']
#                 # print('gps_positioned_status:', gps_positioned_status)
#                 gps_course_decimal_val = latest_packet_qs['course_decimal_val']
#                 # print('gps_course_decimal_val:', gps_course_decimal_val)
#                 gps_mcc = latest_packet_qs['mcc']
#                 # print('gps_mcc:', gps_mcc)
#                 gps_mnc = latest_packet_qs['mnc']
#                 # print('gps_mnc:', gps_mnc)
#                 gps_lac = latest_packet_qs['lac']
#                 # print('gps_lac:', gps_lac)
#                 gps_cell_id = latest_packet_qs['cell_id']
#                 # print('gps_cell_id:', gps_cell_id)
#                 gps_acc = latest_packet_qs['acc']
#                 # print('gps_acc:', gps_acc)
#                 # ----------------------------------------------------------------------------------
#                 # Collect HB Data
#                 hb_insert_time = (latest_packet_qs['hb_time'] + timedelta(hours=6)).strftime("%d-%m-%y, %I:%M %p")
#                 # print('hb_insert_time:', hb_insert_time)
#                 hb_defence = latest_packet_qs['hb_defence']
#                 # print('hb_defence:', hb_defence)
#                 hb_acc = latest_packet_qs['hb_acc']
#                 # print('hb_acc:', hb_acc)
#                 hb_charge = latest_packet_qs['hb_charge']
#                 # print('hb_charge:', hb_charge)
#                 hb_gps_tracking = latest_packet_qs['hb_gps_tracking']
#                 # print('hb_gps_tracking:', hb_gps_tracking)
#                 hb_built_in_bat_level = latest_packet_qs['hb_built_in_bat_level']
#                 # print('hb_built_in_bat_level:', hb_built_in_bat_level)
#                 hb_gsm_signal_strength = latest_packet_qs['hb_gsm_signal_strength']
#                 # print('hb_gsm_signal_strength:', hb_gsm_signal_strength)
#                 # ----------------------------------------------------------------------------------
#
#                 # ----------------------------------------------------------------------------------
#                 # If HB sending stopped for long time, some data manipulate forcefully
#                 # We can call to the SIM to check mobile network availability
#                 current_time = datetime.now().replace(microsecond=0)
#                 # print('current_time:', current_time)
#                 current_ts = int(current_time.timestamp())
#                 # print('current_ts:', current_ts)
#
#                 last_hb_ime = (latest_packet_qs['hb_time'] + timedelta(hours=6)).replace(microsecond=0, tzinfo=None)
#                 # print('last_hb_ime:', last_hb_ime)
#                 last_hb_ts = int(last_hb_ime.timestamp())
#                 # print('last_hb_ts:', last_hb_ts)
#
#                 lag_time_in_mins = int((current_ts - last_hb_ts) / 60)
#                 # print('lag_time_in_mins:', lag_time_in_mins)
#
#                 if lag_time_in_mins > 15:
#                     # print('No HB in last 15 minutes')
#                     gps_speed = '?'
#                     gps_positioned_status = '?'
#                     gps_acc = '?'
#                     hb_acc = '?'
#                     hb_gsm_signal_strength = '?'
#                 # ----------------------------------------------------------------------------------
#                 return render(request, 'app_devices/live_tracking.html', {
#                     'vehicle_name': vehicle_name,
#                     'gps_insert_time': gps_insert_time,
#                     'gps_no_of_satellite': gps_no_of_satellite,
#                     'gps_lat': gps_lat,
#                     'gps_lon': gps_lon,
#                     'gps_speed': gps_speed,
#                     'gps_positioned_status': gps_positioned_status,
#                     'gps_course_decimal_val': gps_course_decimal_val,
#                     'gps_mcc': gps_mcc,
#                     'gps_mnc': gps_mnc,
#                     'gps_lac': gps_lac,
#                     'gps_cell_id': gps_cell_id,
#                     'gps_acc': gps_acc,
#                     'hb_insert_time': hb_insert_time,
#                     'hb_defence': hb_defence,
#                     'hb_acc': hb_acc,
#                     'hb_charge': hb_charge,
#                     'hb_gps_tracking': hb_gps_tracking,
#                     'hb_built_in_bat_level': hb_built_in_bat_level,
#                     'hb_gsm_signal_strength': hb_gsm_signal_strength,
#                     'dev_hid': dev_hid,
#                 })
#             # ----------------------------------------------------------------------------------
#             except Exception as e:
#                 print('e:', e)
#                 print('No data received yet!')
#                 messages.info(request, 'No data received yet!', fail_silently=False)
#                 return redirect('user_dashboard')
#         # ----------------------------------------------------------------------------------
#         else:
#             messages.warning(request, "Don\'t try to play unfair!", fail_silently=False)
#             return redirect('user_dashboard')
#     # ----------------------------------------------------------------------------------
#     except Exception as e:
#         print('e:live_tracking:', e)
#         messages.error(request, 'Something went wrong :(', fail_silently=False)
#         return redirect('user_dashboard')
# # **********************************************************************************************
#
#
# # ***************************************************************************************************
# @login_required(login_url='/')
# def live_tracking_ajax(request):
#     try:
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
#             # ----------------------------------------------------------------------------------
#             # Get the parameters from the client side
#             dev_hid = request.GET.get('dev_hid', None)
#             # print('dev_hid:', dev_hid)
#             # ----------------------------------------------------------------------------------
#             try:
#                 if is_this_user_authorized_for_this_vts(request, dev_hid):
#                     try:
#                         # ----------------------------------------------------------------------------------
#                         # Collect Other Data
#                         # vehicle_name_qs = VehicleInfo.objects.filter(installed_vts__hid__hid__exact=dev_hid).values('name_or_no').get()
#                         # print('vehicle_name_qs:', vehicle_name_qs)
#                         # vehicle_name = vehicle_name_qs['name_or_no']
#                         # print('vehicle_name:', vehicle_name)
#                         # ----------------------------------------------------------------------------------
#                         # Collect GPS Data
#                         # latest_packet_qs = GpsDataFromDevice.objects.filter(device_info_id__hid__hid=dev_hid).values().latest('pk')
#                         # print('latest_packet_qs:', latest_packet_qs)
#                         latest_packet_qs = GpsDataFromDevice.objects.filter(device_info_id__hid__hid=dev_hid).values(
#                             'insert_date_time',
#                             'no_of_satellite',
#                             'lat',
#                             'lon',
#                             'speed',
#                             'gps_status_bit4',
#                             'course_decimal_val',
#                             'mcc',
#                             'mnc',
#                             'lac',
#                             'cell_id',
#                             'acc',
#                             'hb_time',
#                             'hb_defence',
#                             'hb_acc',
#                             'hb_charge',
#                             'hb_gps_tracking',
#                             'hb_built_in_bat_level',
#                             'hb_gsm_signal_strength').latest('pk')
#                         # print('latest_packet_qs:', latest_packet_qs)
#                         # ----------------------------------------------------------------------------------
#                         gps_insert_time = (latest_packet_qs['insert_date_time'] + timedelta(hours=6)).strftime("%d-%m-%y, %I:%M %p")
#                         # print('gps_insert_time:', gps_insert_time)
#                         gps_no_of_satellite = latest_packet_qs['no_of_satellite']
#                         # print('gps_no_of_satellite:', gps_no_of_satellite)
#                         gps_lat = latest_packet_qs['lat']
#                         # print('gps_lat:', gps_lat)
#                         gps_lon = latest_packet_qs['lon']
#                         # print('gps_lon:', gps_lon)
#                         gps_speed = latest_packet_qs['speed']
#                         # print('gps_speed:', gps_speed)
#                         gps_positioned_status = latest_packet_qs['gps_status_bit4']
#                         # print('gps_positioned_status:', gps_positioned_status)
#                         gps_course_decimal_val = latest_packet_qs['course_decimal_val']
#                         # print('gps_course_decimal_val:', gps_course_decimal_val)
#                         gps_mcc = latest_packet_qs['mcc']
#                         # print('gps_mcc:', gps_mcc)
#                         gps_mnc = latest_packet_qs['mnc']
#                         # print('gps_mnc:', gps_mnc)
#                         gps_lac = latest_packet_qs['lac']
#                         # print('gps_lac:', gps_lac)
#                         gps_cell_id = latest_packet_qs['cell_id']
#                         # print('gps_cell_id:', gps_cell_id)
#                         gps_acc = latest_packet_qs['acc']
#                         # print('gps_acc:', gps_acc)
#                         # ----------------------------------------------------------------------------------
#                         # Collect HB Data
#                         hb_insert_time = (latest_packet_qs['hb_time'] + timedelta(hours=6)).strftime("%d-%m-%y, %I:%M %p")
#                         # print('hb_insert_time:', hb_insert_time)
#                         hb_defence = latest_packet_qs['hb_defence']
#                         # print('hb_defence:', hb_defence)
#                         hb_acc = latest_packet_qs['hb_acc']
#                         # print('hb_acc:', hb_acc)
#                         hb_charge = latest_packet_qs['hb_charge']
#                         # print('hb_charge:', hb_charge)
#                         hb_gps_tracking = latest_packet_qs['hb_gps_tracking']
#                         # print('hb_gps_tracking:', hb_gps_tracking)
#                         hb_built_in_bat_level = latest_packet_qs['hb_built_in_bat_level']
#                         # print('hb_built_in_bat_level:', hb_built_in_bat_level)
#                         hb_gsm_signal_strength = latest_packet_qs['hb_gsm_signal_strength']
#                         # print('hb_gsm_signal_strength:', hb_gsm_signal_strength)
#                         # ----------------------------------------------------------------------------------
#                         # If HB sending stopped for long time, some data manipulate forcefully
#                         # We can call to the SIM to check mobile network availability
#                         current_time = datetime.now().replace(microsecond=0)
#                         # print('current_time:', current_time)
#                         current_ts = int(current_time.timestamp())
#                         # print('current_ts:', current_ts)
#
#                         last_hb_ime = (latest_packet_qs['hb_time'] + timedelta(hours=6)).replace(microsecond=0, tzinfo=None)
#                         # print('last_hb_ime:', last_hb_ime)
#                         last_hb_ts = int(last_hb_ime.timestamp())
#                         # print('last_hb_ts:', last_hb_ts)
#
#                         lag_time_in_mins = int((current_ts - last_hb_ts) / 60)
#                         # print('lag_time_in_mins:', lag_time_in_mins)
#
#                         if lag_time_in_mins > 15:
#                             # print('No HB in last 15 minutes')
#                             gps_speed = '?'
#                             gps_positioned_status = '?'
#                             gps_acc = '?'
#                             hb_acc = '?'
#                             hb_gsm_signal_strength = '?'
#                         # ----------------------------------------------------------------------------------
#                         # Serializing json
#                         data_string_json = json.dumps({
#                             "gps_insert_time": str(gps_insert_time),
#                             "gps_no_of_satellite": str(gps_no_of_satellite),
#                             "gps_lat": str(gps_lat),
#                             "gps_lon": str(gps_lon),
#                             "gps_speed": str(gps_speed),
#                             "gps_positioned_status": str(gps_positioned_status),
#                             "gps_course_decimal_val": str(gps_course_decimal_val),
#                             "gps_mcc": str(gps_mcc),
#                             "gps_mnc": str(gps_mnc),
#                             "gps_lac": str(gps_lac),
#                             "gps_cell_id": str(gps_cell_id),
#                             "gps_acc": str(gps_acc),
#                             "hb_insert_time": str(hb_insert_time),
#                             "hb_defence": str(hb_defence),
#                             "hb_acc": str(hb_acc),
#                             "hb_charge": str(hb_charge),
#                             "hb_gps_tracking": str(hb_gps_tracking),
#                             "hb_built_in_bat_level": str(hb_built_in_bat_level),
#                             "hb_gsm_signal_strength": str(hb_gsm_signal_strength)
#                         })
#                         # print("data_string_json:", data_string_json)
#
#                         return JsonResponse({'server_resp': data_string_json}, status=200)
#                     # ----------------------------------------------------------------------------------
#                     except Exception as e:
#                         print('e:', e)
#                         print('No data received yet!')
#                         messages.info(request, 'No data received yet!', fail_silently=False)
#                         return redirect('user_dashboard')
#                 # ----------------------------------------------------------------------------------
#                 else:
#                     print("Don\'t try to play unfair!")
#                     messages.warning(request, "Don\'t try to play unfair!", fail_silently=False)
#                     return redirect('user_dashboard')
#             except Exception as e:
#                 print('e:live_tracking_ajax:', e)
#                 messages.error(request, 'Something went wrong :(', fail_silently=False)
#                 return redirect('user_dashboard')
#         # ----------------------------------------------------------------------------------
#         return JsonResponse({}, status=400)
#     except Exception as e:
#         print('e:live_tracking_ajax:', e)
#         messages.error(request, 'Something went wrong :(', fail_silently=False)
#         return redirect('user_dashboard')
# # ***************************************************************************************************
