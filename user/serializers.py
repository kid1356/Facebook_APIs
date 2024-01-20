from .models import *
from rest_framework import serializers
from rest_framework.response import Response
from pyotp import TOTP
from facebook.settings import *
from django.core.mail import EmailMessage
from django.contrib.auth import password_validation

class Util:
    @staticmethod
    def send_mail(data):
        email  = EmailMessage(subject=data['subject'],    # for sending emails
                              body=data['body'],
                              to= [data["to_email"]])
        email.send()




class RegisterSerilizer(serializers.ModelSerializer):
    confirm_password  = serializers.CharField(style = {'input_type':'password'}, write_only=True)
    class Meta:
        model  = User
        fields = ['email','username','first_name','last_name',
                'password','confirm_password','gender','country','city','profile_picture','biograpghy','date_of_birth' ]
        
        extra_kwargs = {
            'first_name':{'required':True},
            'password':{'write_only' :True},
            'email':{'required':True},
            'gender':{'required':True},
            
        }

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:

            raise serializers.ValidationError("both passsword should be same. ")
        
        return attrs
     
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model  = User
        fields = ['email', 'password']
        

class UserProfileSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = ['id','email','first_name']


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length = 255,style = {'input_type':'password'}, write_only = True)
    confirm_password = serializers.CharField(max_length = 255,style = {'input_type':'password'}, write_only = True)
    class Meta:
        model = User
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')

        if password != confirm_password:
            raise serializers.ValidationError("Both password must be same!")
        
        user.set_password(password)
        user.save()
        return attrs        
        

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 255)
    
    def validate(self, attrs):
        email = attrs.get('email')
     
        try:  
           user = User.objects.get(email = email)
        except User.DoesNotExist:
            return serializers.ValidationError("User does not Exists!")
        
        user.generated_otp_seceret_key()

        otp_secret_key = user.secret_key

        otp = TOTP(otp_secret_key,digits=TOTP_DIGITS, interval=TOTP_TIME_STEP, digest= TOTP_ALGORITHM)

        otp_value = otp.now()

        User.objects.get(secret_key = otp_secret_key)

        data = {
            'subject':"Your Password Reset OTP",
            'body':f'Your OTP is : {otp_value}',
            'to_email':user.email
        }

        Util.send_mail(data)

        return attrs

class ForgetPasswordSerializer(serializers.Serializer):
    otp_value = serializers.CharField(max_length = 255)
    password = serializers.CharField(max_length = 255, style={'input_type':'password'}, write_only = True)
    confirm_password = serializers.CharField(max_length = 255, style={'input_type':'password'}, write_only = True)

    def validate(self, attrs):
        otp_value = attrs.get('otp_value')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')

        otp = TOTP(user.secret_key,digits=TOTP_DIGITS, interval=TOTP_TIME_STEP, digest= TOTP_ALGORITHM)

        if not otp.verify(otp_value):
            raise serializers.ValidationError('Invalid OTP')
        

        if password != confirm_password:
            return serializers.ValidationError("Both Password Should be equal!")
        
        
        password_validation.validate_password(password, user=user)

        user.set_password(password)
        user.save()

        return attrs