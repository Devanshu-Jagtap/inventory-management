from django.shortcuts import render
from ..serializers import SignupSerializer,UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from ..utils import success, error
from ..models import CustomUser

class SignupAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user_type = request.data.get("user_type", CustomUser.UserType.EMPLOYEE)

        if CustomUser.objects.filter(email=email).exists():
            return error("User with this email already exists")

        if user_type == CustomUser.UserType.EMPLOYEE:
            if not request.user.is_authenticated or request.user.user_type != CustomUser.UserType.ADMIN:
                return error("Only admin can register an employee", status_code=403)
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "user_type": user.user_type,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            return success("Signup successful", data, status_code=201)

        return error("Signup failed", serializer.errors)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return error("Email and password are required")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                return error("Account is inactive", status_code=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)

            data = {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "user_type": user.user_type,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }

            return success("Login successful", data)

        return error("Invalid email or password", status_code=status.HTTP_401_UNAUTHORIZED)
    
