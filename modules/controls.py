from flask import Flask, jsonify
import jsonrpclib, socket, struct
import urllib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *
import maraschino.logger as logger

global xbmc_error
xbmc_error = 'There was a problem connecting to the XBMC server'

@app.route('/xhr/play/<file_type>/<media_type>/<int:media_id>')
@requires_auth
def xhr_play_media(file_type, media_type, media_id):
    logger.log('CONTROLS :: Playing %s' % media_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        if file_type == 'video':
            xhr_clear_playlist('video')

            if media_type == 'tvshow':
                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, sort={ 'method': 'episode' })['episodes']

                for episode in tvshow_episodes:
                    episodeid = episode['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            elif 'season' in media_type:
                media_type = media_type.split('_')
                season = int(media_type[1])

                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, season=season, sort={ 'method': 'episode' })['episodes']

                for episodes in tvshow_episodes:
                    episodeid = episodes['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            else:
                item = { media_type + 'id': media_id }
                xbmc.Playlist.Add(playlistid=1, item=item)

            playlistid = 1

        else:
            xhr_clear_playlist('audio')

            item = { media_type + 'id': media_id }
            xbmc.Playlist.Add(playlistid=0, item=item)

            playlistid = 0

        item = { 'playlistid': playlistid }
        xbmc.Player.Open(item)
        return jsonify({ 'success': True })

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({ 'failed': True })

@app.route('/xhr/enqueue/<file_type>/<media_type>/<int:media_id>')
@requires_auth
def xhr_enqueue_media(file_type, media_type, media_id):
    logger.log('CONTROLS :: Queueing %s' % media_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        if file_type == 'video':

            if media_type == 'tvshow':
                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, sort={ 'method': 'episode' })['episodes']

                for episode in tvshow_episodes:
                    episodeid = episode['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            elif 'season' in media_type:
                media_type = media_type.split('_')
                season = int(media_type[1])

                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, season=season, sort={ 'method': 'episode' })['episodes']

                for episodes in tvshow_episodes:
                    episodeid = episodes['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            else:
                item = { media_type + 'id': media_id }
                xbmc.Playlist.Add(playlistid=1, item=item)

            playlistid = 1

        else:

            item = { media_type + 'id': media_id }
            xbmc.Playlist.Add(playlistid=0, item=item)

            playlistid = 0

        item = { 'playlistid': playlistid }
        return jsonify({ 'success': True })

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({ 'failed': True })

@app.route('/xhr/resume/video/<video_type>/<int:video_id>')
@requires_auth
def xhr_resume_video(video_type, video_id):
    logger.log('CONTROLS :: Resuming %s' % video_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        xhr_clear_playlist('video')

        if video_type == "episode":
            video = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=video_id, properties=['resume'])['episodedetails']
        else:
            video = xbmc.VideoLibrary.GetMovieDetails(movieid=video_id, properties=['resume'])['moviedetails']

        seconds = int(video['resume']['position'])

        hours = seconds / 3600
        seconds -= 3600*hours
        minutes = seconds / 60
        seconds -= 60*minutes

        position = { 'hours': hours, 'minutes': minutes, 'seconds': seconds }

        item = { video_type + 'id': video_id }
        xbmc.Playlist.Add(playlistid=1, item=item)

        item = { 'playlistid': 1 }
        xbmc.Player.Open(item)
        xbmc.Player.Seek(playerid=1, value=position)

        return jsonify({ 'success': True })

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({ 'failed': True })

@app.route('/xhr/play/trailer/<int:movieid>')
@requires_auth
def xhr_play_trailer(movieid):
    logger.log('CONTROLS :: Playing trailer', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        xhr_clear_playlist('video')

        trailer = xbmc.VideoLibrary.GetMovieDetails(movieid=movieid, properties= ['trailer'])['moviedetails']['trailer']
        item = { 'file': trailer }
        xbmc.Playlist.Add(playlistid=1, item=item)

        item = { 'playlistid': 1 }
        xbmc.Player.Open(item)

        return jsonify({ 'success': True })

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({ 'failed': True })

@app.route('/xhr/play_file/<file_type>/', methods=['POST'])
@requires_auth
def xhr_play_file(file_type):
    logger.log('CONTROLS :: Playing %s file' % file_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    try:
        if file_type == "music":
            file_type = "audio"
        xhr_clear_playlist(file_type)

        file = request.form['file']
        file = urllib.unquote(file.encode('ascii')).decode('utf-8')

        if file_type == "video":
            player = 1
        else:
            player = 0

        item = { 'file': file }
        xbmc.Playlist.Add(playlistid=player, item=item)

        item = { 'playlistid': player }
        xbmc.Player.Open(item)

        return jsonify({ 'success': True })

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({ 'failed': True })

@app.route('/xhr/enqueue_file/<file_type>/', methods=['POST'])
@requires_auth
def xhr_enqueue_file(file_type):
    logger.log('CONTROLS :: Queueing %s file' % file_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        file = request.form['file']
        file = urllib.unquote(file.encode('ascii')).decode('utf-8')

        if file_type == "video":
            player = 1
        else:
            player = 0

        item = { 'file': file }
        xbmc.Playlist.Add(playlistid=player, item=item)

        return jsonify({ 'success': True })

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({ 'failed': True })

@app.route('/xhr/clear_playlist/<playlist_type>')
@requires_auth
def xhr_clear_playlist(playlist_type):
    logger.log('CONTROLS :: Clearing %s playlist' % playlist_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        if playlist_type == 'audio':
            xbmc.Playlist.Clear(playlistid=0)
        elif playlist_type == 'video':
            xbmc.Playlist.Clear(playlistid=1)

        return jsonify({ 'success': True })

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({ 'failed': True })

@app.route('/xhr/controls/<command>')
@requires_auth
def xhr_controls(command):
    xbmc = jsonrpclib.Server(server_api_address())
    try:
        active_player = xbmc.Player.GetActivePlayers()
        if active_player[0]['type'] == 'video':
            playerid = 1
        elif active_player[0]['type'] == 'audio':
            playerid = 0
    except:
        active_player = None

    if command == 'play_pause':
        logger.log('CONTROLS :: Play/Pause', 'INFO')
        try:
            xbmc.Player.PlayPause(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'stop':
        logger.log('CONTROLS :: Stop', 'INFO')
        try:
            xbmc.Player.Stop(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif 'volume' in command:
        logger.log('CONTROLS :: Volume', 'INFO')
        try:
            volume = command.split('_')
            volume = int(volume[1])
            xbmc.Application.SetVolume(volume=volume)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'next':
        logger.log('CONTROLS :: Next', 'INFO')
        try:
            xbmc.Player.GoNext(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'previous':
        logger.log('CONTROLS :: Previous', 'INFO')
        try:
            xbmc.Player.GoPrevious(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'fast_forward':
        logger.log('CONTROLS :: Fast forward', 'INFO')
        try:
            xbmc.Player.SetSpeed(playerid=playerid, speed='increment')
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'rewind':
        logger.log('CONTROLS :: Rewind', 'INFO')
        try:
            xbmc.Player.SetSpeed(playerid=playerid, speed='decrement')
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif 'seek' in command:
        logger.log('CONTROLS :: Seek', 'INFO')
        try:
            percentage = command.split('_')
            percentage = int(percentage[1])
            xbmc.Player.Seek(playerid=playerid, value=percentage)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'shuffle':
        logger.log('CONTROLS :: Shuffle', 'INFO')
        try:
            shuffled = xbmc.Player.GetProperties(playerid=playerid, properties=['shuffled'])['shuffled']
            if shuffled == True:
                xbmc.Player.UnShuffle(playerid=playerid)
            else:
                xbmc.Player.Shuffle(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'repeat':
        logger.log('CONTROLS :: Repeat', 'INFO')
        try:
            states = ['off', 'one', 'all']
            repeat = xbmc.Player.GetProperties(playerid=playerid, properties=['repeat'])['repeat']
            state = states.index(repeat)
            if state <= 1:
                state = state + 1
            else:
                state = 0

            state = states[state]
            xbmc.Player.Repeat(playerid=playerid, state=state)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'update_video':
        logger.log('CONTROLS :: Updating video library', 'INFO')
        try:
            xbmc.VideoLibrary.Scan()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'clean_video':
        logger.log('CONTROLS :: Cleaning video library', 'INFO')
        try:
            xbmc.VideoLibrary.Clean()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'update_audio':
        logger.log('CONTROLS :: Updating audio library', 'INFO')
        try:
            xbmc.AudioLibrary.Scan()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'clean_audio':
        logger.log('CONTROLS :: Cleaning audio library', 'INFO')
        try:
            xbmc.AudioLibrary.Clean()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'poweroff':
        logger.log('CONTROLS :: Shutting down XBMC machine', 'INFO')
        try:
            xbmc.System.Shutdown()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'suspend':
        logger.log('CONTROLS :: Suspending XBMC machine', 'INFO')
        try:
            xbmc.System.Suspend()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'reboot':
        logger.log('CONTROLS :: Rebooting XBMC machine', 'INFO')
        try:
            xbmc.System.Reboot()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'poweron':
        logger.log('CONTROLS :: Powering on XBMC machine', 'INFO')
        server_macaddress = get_setting_value('server_macaddress')

        if not server_macaddress:
            logger.log('CONTROLS :: No XBMC machine MAC address defined', 'ERROR')
            return jsonify({ 'failed': True })

        else:
            try:
                addr_byte = server_macaddress.split(':')
                hw_addr = struct.pack('BBBBBB',
                int(addr_byte[0], 16),
                int(addr_byte[1], 16),
                int(addr_byte[2], 16),
                int(addr_byte[3], 16),
                int(addr_byte[4], 16),
                int(addr_byte[5], 16))

                msg = '\xff' * 6 + hw_addr * 16
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.sendto(msg, ("255.255.255.255", 9))
                return_response = 'success'

            except:
                logger.log('CONTROLS :: Failed to send WOL packet', 'ERROR')
                return_response = 'failed'

    if return_response == 'success':
        return jsonify({ 'success': True })
    else:
        return jsonify({ 'failed': True })
