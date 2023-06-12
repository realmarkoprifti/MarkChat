from django.shortcuts import render
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests, random
from .serializers import (RegisterSerializer, VerifyVerificationCodeSerializer, LoginSerializer)
from MarkChat.settings import MARKMAIL_CAPTCHA
from .models import User, UserProfile
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.

MARKMAIL_URL = "https://markmail-production.up.railway.app"


def login_markmail():
    data = {
        "email": "admin@markmail.com",
        "password": "unejammarko",
        "recaptcha_token": MARKMAIL_CAPTCHA    
    }
    
    request = requests.post(MARKMAIL_URL + "/api/login", json=data)
    response = request.json()
    
    return response["access"]


def send_confirmation_code(email):
    access_token = login_markmail()
    random_code = random.randint(1000, 9999)
    data = {
        "content": f"Here's your verification code: {random_code}",
        "receiver": email,
        "subject": "Verify your MarkChat account"
    }

    request = requests.post(MARKMAIL_URL + "/api/compose", json=data, headers={"Authorization": "Bearer " + access_token})
    
    return random_code
    


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.validated_data["verification_code"] = send_confirmation_code(serializer.validated_data["email"])
        serializer.save()  
        
        return Response({"message": "user_registered"}, status=HTTP_201_CREATED)
    
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_verification_code(request):
    serializer = VerifyVerificationCodeSerializer(data=request.data)
    
    if serializer.is_valid():
        user = User.objects.get(username=serializer.validated_data["username"])
        profile = UserProfile.objects.get(user=user)
        profile.is_verified = True
        profile.save()
            
        return Response({"message": "user_verified"}, status=HTTP_200_OK)
        
            
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        if UserProfile.objects.get(user=User.objects.get(username=serializer.validated_data["username"])).is_verified == False:
            return Response({"message": "user_not_verified"}, HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])
        
        if user is None:
            return Response({"message": "auth_invalid"}, HTTP_400_BAD_REQUEST)
        
        tokens = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(tokens),
            "access": str(tokens.access_token)    
        }, HTTP_200_OK)
        
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)