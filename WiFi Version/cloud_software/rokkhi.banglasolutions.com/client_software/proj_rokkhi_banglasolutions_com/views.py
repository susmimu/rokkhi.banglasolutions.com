# ---------------------------------------------------------------------------------------------------
from django.http import HttpResponse
from django.utils import timezone
import pytz
import socket
import math
from datetime import datetime
import json
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.core import serializers
from django.contrib import auth
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import forms, UserCreationForm
from app_users.form import SignMeUpForm, SignMeInForm
from app_devices.models import *
# ---------------------------------------------------------------------------------------------------


# ***************************************************************************************************
def home(request):
    try:
        logout(request)

        return render(request, 'proj_ee_zeronesolution_com/home.html', {
            'login_form': SignMeInForm,
            'current_year': datetime.now().year,
        })
    except Exception as e:
        print('e:home:', e)
# ***************************************************************************************************


# ***************************************************************************************************
def get_motion_call_and_sms_nos(request):
    try:
        # call_info = MotionCallAndSMS.objects.all().filter(call_pending_status=True)
        
        
        call_info = list(MotionCallAndSMS.objects.filter(call_pending_status=True).values('device_info_id', 'called_to'))  # Convert QuerySet to list of dictionaries
        
        return JsonResponse({'call_info': call_info})

        #return {'call_info': call_info}
    except Exception as e:
        print('e:get_motion_call_and_sms_nos:', e)
# ***************************************************************************************************



# ***************************************************************************************************
def reset_motion_call_pending_status(request):
    try:
        MotionCallAndSMS.objects.update(call_pending_status=False)

        return JsonResponse({"message": "success"})
    except Exception as e:
        print('e:reset_motion_call_pending_status:', e)
# ***************************************************************************************************




