from os import name

from django.urls import path, include
from user.views import *
from rest_framework.authtoken.views import obtain_auth_token
app_name='user' 

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path("home/", home, name = 'home'),
    # path("login/", UserLoginApiView.as_view()),
    # path("forgotpass/", ForgotPassView.as_view()),
    # path("available_forgotpass/", ForgotPassByEmailAvailability.as_view()),
    path("signup/", signup, name ='signup'),
    path("login/", login, name ='login')
    # path("profile/", ProfileView.as_view()),
    # path("changepass/", PasswordChange.as_view()),
    # path("corporate_login/", CorporateLogin.as_view()),
    # path("verify_email/", VerifyEmailView.as_view()),
    # path("verify_email_back/", VerifyEmailCallBack.as_view()),
    # path("forgot_pass_back/", ForgotPassEmailCallBack.as_view()),
    # path("forgot_pass_sms_back/", ForgotPassSMSCallBack.as_view()),
    # path("operator_update_user_profile/", OperatorUpdatesUserProfile.as_view()),
]
