import json
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from asgiref.sync import async_to_sync,sync_to_async
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from.models import Lobby,current_song
from .utils import find_or_create_room,apply_changes_to_all
class LobbyConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['lobby_id']
        self.room_group_name =  str(self.room_id)
        self.user = self.scope['user']
        await connect_user(self.room_id,self.user)
        
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

       
        await self.accept()

    async def disconnect(self, close_code):
        await disconnect_user(self.room_id,self.user)

        await self.channel_layer.group_discard(
            self.room_group_name,self.channel_name
        )   
    
    async def receive(self,text_data):
        print('hi')
        payload = json.loads(text_data)
        command = payload['command']
        user_email = payload['user']
        lobbypk = payload['lobbypk']
        user = await get_user(user_email)
        lobby = await get_room(user,lobbypk)
        print((command,user,lobbypk))
        if user_email == await get_owner(lobby):
            
            if command == 'play':
                await apply(lobby.users_connected.all(),1)
            elif command == 'stop':
                await apply(lobby.users_connected.all(),2)
            elif command == 'next':
                await apply(lobby.users_connected.all(),3)
            elif command == 'prev':
                await apply(lobby.users_connected.all(),4)

        await self.channel_layer.group_send(
            str(self.room_group_name),{
               'type':'send_message',
                
            }
        )

    async def send_message(self,content):

        
        await self.send(text_data= json.dumps({}))

@database_sync_to_async
def connect_user(lobbypk,user):
    lobby = find_or_create_room(user,lobbypk)
    lobby.connect_user(user)

@database_sync_to_async
def disconnect_user(lobbypk,user):
    lobby = find_or_create_room(user,lobbypk)
    lobby.remove_user(user)  
    if user == lobby.owner:
        clear_current_song(lobby)
        lobby.is_active_playback = False
        lobby.save()


@database_sync_to_async
def change_track_status(lobbypk,command):
    lobby = find_or_create_room(user,lobbypk)
    users = lobby.users_connected.all()
    apply_changes_to_all(users,command)

   
def clear_current_song(lobby):
    current = current_song.objects.get(lobby=lobby)
    current.current_uri = ''
    current.save()

@database_sync_to_async    
def get_user(email):
    return User.objects.get(email=email)
@database_sync_to_async
def get_room  (user,lobbypk) :
    return find_or_create_room(user,lobbypk)
@database_sync_to_async    
def get_owner(lobby):
    return lobby.owner.email    
@database_sync_to_async
def apply (users,command):
    apply_changes_to_all(users,command)    