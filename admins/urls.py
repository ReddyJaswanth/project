from django.urls import path
from admins.views import *

urlpatterns = [
    path('adminhome/', adminhome, name='adminhome'),
    path('AdminActiveUsers/', AdminActiveUsers, name='AdminActiveUsers'),
    path('AdmindeActiveUsers/', AdmindeActiveUsers, name='AdmindeActiveUsers'),

]