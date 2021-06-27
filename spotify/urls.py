from django.urls import path
from . import views
urlpatterns= [
    path('',views.login,name='log'),
    path('lobby/<int:lobbyPK>',views.lobby,name='lobby'),
    path('callback/',views.callback,name='redirect'),
    path('test',views.test),
]
