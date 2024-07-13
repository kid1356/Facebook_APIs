from django.shortcuts import render
from .serializers import *
from rest_framework.views import APIView 
from rest_framework import status,viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .permissions import *
# Create your views here.

def generated_token(user):
    refresh = RefreshToken.for_user(user)      #token for every user 

    return {
        'refresh': str(refresh),
        'access' : str(refresh.access_token),
    }


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerilizer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token  = generated_token(user)
        return Response({"token":token,'register successfully':serializer.data}, status=status.HTTP_201_CREATED)
            

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:

            token=generated_token(user)

            return Response({'token':token,'user':serializer.data, 'msg':f'welcome {user.first_name}'}, status=status.HTTP_200_OK)
        return Response('Login credential is Invalid', status=status.HTTP_404_NOT_FOUND)


class UpdateUserInfoView(APIView):
    permission_classes =[IsAuthenticated, IsOwner]
    def patch(self, request,id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response("No User is found!", status=status.HTTP_404_NOT_FOUND)
        
        self.check_object_permissions(request, user)

        serializer = RegisterSerilizer(user, data = request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"User Info Updated Successfully":serializer.data}, status=status.HTTP_200_OK)



class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data = request.data, context = {'user':request.user})
        serializer.is_valid(raise_exception=True)

        return Response('Password change successfully', status=status.HTTP_200_OK)
    

class ForgetPasswordEmailView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response("An email is sent Please Check Your Mail Box",status=status.HTTP_200_OK)
    
class ForgetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data, context = {'user':request.user})
        serializer.is_valid(raise_exception=True)

        return Response("Password change successfully", status=status.HTTP_200_OK)



class ActiveUserView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def patch(self, request,id):
        try:
            user = User.objects.get(id=id)

        except User.DoesNotExist:
            return Response("User does not found", status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = True
        user.save()

        return Response("user is active Successfully",status=status.HTTP_200_OK)
    
class DeActiveUserView(APIView):
    permission_classes = [IsAdminUser,IsAuthenticated]

    def patch(self,request,id):
        try:
            user = User.objects.get(id=id)

        except User.DoesNotExist:
            return Response("User does not exists",status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = False
        user.save()
        return Response("user in unactive successfully", status=status.HTTP_200_OK)