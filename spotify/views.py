from django.shortcuts import render,redirect,HttpResponse
from django.urls import reverse

from spotipy.oauth2 import SpotifyOAuth
from .models import Lobby,current_song
from .utils import *


import time
import os
import spotipy

TOKEN_INFO = 'token_info'

def home (request):
    return render(request,'home.html',{})
'''
    Start the authorization process
                                    ''' 
def login(request):
    sp = create_spotify_auth()
    auth_url = sp.get_authorize_url()
    return redirect(auth_url)

'''
    Handling the call back from Spotify
                                        ''' 
def callback(request):
    sp = create_spotify_auth()
    code = request.GET.get('code')
    token = sp.get_access_token(code)
    edit_access_token_object(request.user,token['access_token'],token['refresh_token'],token['expires_at'])

    
    request.session[TOKEN_INFO] = token
    os.remove('.cache')
    try:
        lobby = Lobby.objects.get(owner=request.user)
    except Lobby.DoesNotExist:
        lobby = Lobby(owner = request.user)
        lobby.save()
    return redirect('lobby',lobbyPK = lobby.id)



def lobby (request,*args,**kwargs): 

    '''
        Checking authentication
                                    ''' 
         
    try :
        token = get_token(request.session.get(TOKEN_INFO))

    except : 
        print('user not logged in')
        return redirect('/')

    '''
        Getting lobby
                        ''' 
    lobbyPK = kwargs.get('lobbyPK')
    lobby = find_or_create_room(request.user,lobbyPK)

    uri = get_current_lobby_song_or_create(lobby)

    '''
        This whole process about the case if other user joined 
        the lobby while the owner is currently listening
                                                                ''' 
    
    
    # connecting to api 
    sp = spotipy.Spotify(auth=token['access_token'])    
    
    current_ms = False

    '''
     uris attribute only accepts list
                                        '''                                 
    if uri:                                    
        l = list()
        l.append(uri)

        '''
        if owner is listening = lobby is is_active_playback
        -> checking expieration date to make sure
                                                        '''
        if lobby.is_active_playback:
            try:
                sp.start_playback(uris=l)
                current_ms = get_sp(lobby.owner).current_playback()['progress_ms']+5000
            except:
                pass    
                    
        else :
            print("Lobby owner is not listening currently")  
            current_ms = False

    '''
        If the owner is playing a track

        and the request is not from the owner

        then we play the same track at the same position
                                                            '''
    


    context = get_context(sp)
    '''
        updating curent song in lobby
        from owner
                                        '''
    if request.user == lobby.owner:                                    
        if context['status']:
            current = current_song.objects.get(lobby=lobby)
            current.current_uri = context['uri']
            current.save()
            lobby.is_active_playback = True
            lobby.save()
    else:
        if  current_ms:
            try:
                sp.start_playback(uris=l,position_ms=current_ms)
            except:
                print('No device is playing')
        else:
            try:
                sp.start_playback(uris=l)
            except:
                print('No device is playing')     
            
    context['lobby_pk'] = lobbyPK


    return render(request,'lobby.html',context)

def test(request,*args,**kwargs):
    lobby = find_or_create_room(request.user,1)
    users = lobby.users_connected.all()
    apply_changes_to_all(users,1)            
    return HttpResponse('lol')