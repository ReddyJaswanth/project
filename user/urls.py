from django.urls import path
from user.views import *

urlpatterns = [
    path('userhome/',userhome, name='userhome'),
    path('updateprofile/', updateprofile, name='updateprofile'),
    path('userchat/', userchat, name='userchat'),
    path('chat/', userchat_action, name='userchat_action'),
    path('chat/<int:session_id>/', userchat_action, name='userchat_action_with_session'),
    path('delete_chat/<int:session_id>/', delete_chat_session, name='delete_chat_session'),

    path('previous_chats', previous_chats, name='previous_chats'),
    path('chat_details/<int:session_id>/', chat_details, name='chat_details'),
]