from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.
class Lobby (models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="lobbyuser1")  
    users_connected = models.ManyToManyField(User,blank=True,related_name="users_conntected")
    date_created = models.DateField(auto_now_add=True,blank=True,null=True)
    is_active_playback = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True,null=True,blank=True)  
    

    def connect_user(self,user):
        check = self.users_connected.filter(username=user.username)
        if not check.exists():
            self.users_connected.add(user)
            self.save()
            
    def remove_user(self,user):
        check = self.users_connected.filter(username=user.username)
        if check.exists():
            self.users_connected.remove(user)
            self.save()        
    def __str__(self):
        return f'{self.owner.username} - {self.is_active}'
class Access_token (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="token_user")
    access_token = models.CharField(max_length=500,null=True,blank=True)
    refresh_token = models.CharField(max_length=500,null=True,blank=True)
    expiers_at = models.CharField(max_length=100,null=True,blank=True)

class current_song (models.Model):
    lobby = models.ForeignKey(Lobby,on_delete=models.CASCADE,related_name='lobby')
    current_uri = models.CharField(max_length=100,blank=True,null=True)
    date_created = models.DateField(auto_now_add=True,blank=True,null=True)  
