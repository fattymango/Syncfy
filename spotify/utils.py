from django.shortcuts import redirect
from django.contrib import messages

from spotipy.oauth2 import SpotifyOAuth

from .models import Lobby,Access_token,current_song
from .app_client import *

import time
import os
import spotipy

'''
    get info of the current song            
                                    '''
def get_context(sp):
    context = {}

    try:
        payload = sp.current_playback()
    except :
        pass       

    if payload:
        context['status'] = True   
        context['song_name'] = payload["item"]["name"]   
        context['song_img'] = payload["item"]['album']["images"][0]['url']
        context['artist'] = payload["item"]['album']['artists'][0]['name']
        context['uri'] = payload['item']['uri']

    else : 
        context['status'] = False  
        
           
    return context


'''
    creat a new authorization
                                '''    
def create_spotify_auth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE)


'''
    Get token or create a new one
                                ''' 
def get_token(token):
    if not token :
        print("error")
    
    if is_expired(int(token['expires_at'])):
        sp = create_spotify_auth()
        token = sp.refresh_access_token(token['refresh_token'])
        os.remove('.cache')
    return token        


def find_or_create_room(user,pk):
    try:
        lobby = Lobby.objects.get(id=pk)
    except Lobby.DoesNotExist:
        lobby = Lobby(owner = user)
        lobby.save()
    return lobby  


'''
    Check token expieration date
                                    ''' 
def is_expired(expires_at):
    return  int(expires_at)-int(time.time()) <60


def find_or_create_token(user):
    try:
        token = Access_token.objects.get(user=user)
        
    except Access_token.DoesNotExist:
        token = Access_token.objects.create(user=user)
        token.save()
    return token


'''
    Edit user's Access_token token object
                                            '''      
def edit_access_token_object(user,access_token=None,refresh_token=None,expiers_at=None):
    token = find_or_create_token(user)
    if access_token:
        token.access_token = access_token
    if refresh_token:    
        token.refresh_token = refresh_token
    if expiers_at:    
        token.expiers_at = expiers_at
    token.save()
    # print('called')
    return token     


def get_sp(user):
    token = find_or_create_token(user)
    
    if not is_expired(expires_at=token.expiers_at):
        sp = spotipy.Spotify(auth=token.access_token)
         
    else :
        try:  
            sp = create_spotify_auth()
            token = sp.refresh_access_token(token.refresh_token)  
            sp = spotipy.Spotify(auth=token['access_token']) 
        except:
            return redirect('/')    
    return sp


def get_current_lobby_song_or_create(lobby):
    '''
        Checking if any current_song 
        associated with the lobby
                                    '''     
    try:
        currentSong = current_song.objects.get(lobby=lobby)
    except current_song.DoesNotExist  :
        currentSong = current_song(lobby=lobby)      
    '''
        Checking if the current_song object
        has a song
                                    '''       
    if currentSong.current_uri:
        uri = currentSong.current_uri
    else:
        uri = False   
    return uri    


def pasue(user):
    sp = get_sp(user)
    try:
        sp.pause_playback()
         
    except:
        pass  


def play(user):
    sp = get_sp(user)
    try:
            sp.start_playback()
    except:
        pass 

def next_track(user):
    sp = get_sp(user)
    try:
            sp.next_track()

    except:
        pass 

def prev_track(user):
    sp = get_sp(user)
    try:
            sp.previous_track()

    except:
        pass 

def apply_changes_to_all(users,command):
    for user in users:
        if command == 1 :
            play(user)
        if command == 2 :
            pasue(user)
        if command == 3 :
            next_track(user)
        if command == 4 :
            prev_track(user) 