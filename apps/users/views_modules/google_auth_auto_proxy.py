import logging
import requests
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
import json
import base64
import secrets

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthAutoProxyView(View):
    
