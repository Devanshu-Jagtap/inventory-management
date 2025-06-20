# utils.py

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum
from .models import *

def success(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)

def error(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status_code)

