from .models import File, Peer
from django.shortcuts import get_object_or_404
from .ultis.utils import authorize_peer, generate_jwt_token
from django.db import connection
from .ultis.utils import validate_required_fields
from django.views.decorators.csrf import csrf_exempt
from .serializer import PeerSerializer, FileSerializer, PeerFileSerializer
import uuid
import struct
import socket
import os
from rest_framework.response import Response
import requests
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import json
from .models import File, Peer, PeerFile, Tracker
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

ISLOGINREQUIRED = os.environ.get('ISLOGINREQUIRED', 0)
print(f"Is login required: {ISLOGINREQUIRED}")
TRACKERID = os.environ.get('TRACKERID')
print(f"Tracker ID: {TRACKERID}")
# try:
#     instance_tracker = Tracker.objects.get(tracker_id=TRACKERID)
# except ObjectDoesNotExist:
#     print(f"Tracker with tracker_id {
#           TRACKERID} does not exist. Creating new tracker...")
#     instance_tracker = Tracker.objects.create(
#         tracker_id=TRACKERID,
#         ip_address="localhost",
#         port=8000,
#         status='active',
#     )


@csrf_exempt
def testAPI(request):
    if request.method == 'GET':
        db_info = {
            'engine': connection.settings_dict['ENGINE'],
            'name': connection.settings_dict['NAME'],
            'user': connection.settings_dict['USER'],
            'host': connection.settings_dict['HOST'],
            'port': connection.settings_dict['PORT'],
        }

        print(f"Database connection info: {db_info}")
        return JsonResponse({'message': 'API is working',
                             'dbinfo': db_info,
                             'trackerid': TRACKERID,
                             'ISLOGINREQUIRED': ISLOGINREQUIRED},
                            status=200)


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        if ISLOGINREQUIRED == 0:
            return JsonResponse({'failure reason': 'Login is not required'}, status=400)

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'failure reason': 'Username and password are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'failure reason': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        token = generate_jwt_token(user)
        return JsonResponse(token, status=201)
    else:
        return JsonResponse({'failure reason': 'Invalid request method'}, status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':

        if ISLOGINREQUIRED == 0:
            return JsonResponse({'failure reason': 'Login is not required'}, status=400)

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'failure reason': 'Username and password are required'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            token = generate_jwt_token(user)
            return JsonResponse(token, status=200)
        else:
            return JsonResponse({'failure reason': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'failure reason': 'Invalid request method'}, status=405)


@csrf_exempt
def announce(request):
    if request.method == 'GET':
        try:
            # if ISLOGINREQUIRED == 1:
            #     peer = authorize_peer(request)

            # data = json.loads(request.body)

            # print("here1")
            # required_fields = ['info_hash', 'peer_id',
            #                    'port', 'uploaded', 'downloaded', 'left']
            # print("here2")
            # is_valid, error_message = validate_required_fields(
            #     data, required_fields)
            # if is_valid == False:
            #     return JsonResponse({'failure reason': str(error_message)}, status=401)

            print("here3")
            info_hash = request.GET.get('info_hash')
            peer_id = request.GET.get('peer_id')
            ip_address = request.META.get('REMOTE_ADDR')
            port = request.GET.get('port')
            uploaded = request.GET.get('uploaded')
            downloaded = request.GET.get('downloaded')
            left = request.GET.get('left')
            event = request.GET.get('event')
            compact = request.GET.get('compact')
            print(compact)

            print("here4")
            try:  # WHATEEVER THE EVENT IS, UPDATE THE PEER
                print("here5")
                peer, created = Peer.objects.update_or_create(
                    peer_id=peer_id,
                    defaults={
                        'ip_address': ip_address,
                        'port': port,
                        'last_seen': datetime.now(),
                        'is_active': event != 'stopped'
                    }
                )
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

            response_data = {}
            print("here5.5")
            # CREATE FILE OR SEEDING
            if event == "completed" or (left == 0 and downloaded > 0):
                print("here6")
                print(event, left, downloaded)

                try:  # AFTER THIS THE FILE IS GUARANTEED TO EXIST
                    file = File.objects.get(hash_code=info_hash)
                except File.DoesNotExist:
                    file = File.objects.create(
                        hash_code=info_hash)

                try:
                    peerfile, created = PeerFile.objects.update_or_create(
                        peer=peer,
                        file=file,
                        peer_type='seeder'
                    )
                except Exception as e:
                    return JsonResponse({'failure reason': str(e)}, status=400)

                peers_list = Peer.objects.filter(
                    peerfile__file=file).exclude(peer_id=peer_id)

                peers_serialized = PeerSerializer(
                    peers_list, many=True).data

                response_data = {
                    'interval': 1800,
                    'complete': PeerFile.objects.filter(file=file, peer_type='seeder').count(),
                    'incomplete': PeerFile.objects.filter(file=file, peer_type='leecher').count(),
                    'peers': peers_serialized
                }
                print("here7")

            # PEER STOPPED
            elif event == "stopped":
                print("here_stopped")
                try:
                    # Mark the peer as inactive
                    peer.is_active = False
                    peer.last_seen = datetime.now()
                    peer.save()

                    # Remove the PeerFile entry
                    PeerFile.objects.filter(
                        peer=peer, file__hash_code=info_hash).delete()

                    peers_list = Peer.objects.filter(
                        peerfile__file=file).exclude(peer_id=peer_id)

                    peers_serialized = PeerSerializer(
                        peers_list, many=True).data

                    response_data = {
                        'interval': 1800,
                        'complete': PeerFile.objects.filter(file=file, peer_type='seeder').count(),
                        'incomplete': PeerFile.objects.filter(file=file, peer_type='leecher').count(),
                        'peers': peers_serialized
                    }

                except Exception as e:
                    return JsonResponse({'failure reason': f'Failed to handle stopped event: {str(e)}'}, status=500)

            # DOWNLOAD AND LEECH
            else:
                print("here_leech")
                try:
                    print("here5.6")
                    file = File.objects.get(hash_code=info_hash)

                    if event == 'started' or (downloaded > 0 and left > 0):
                        try:
                            print("here6")
                            peerfile, created = PeerFile.objects.update_or_create(
                                peer=peer,
                                file=File.objects.get(hash_code=info_hash),
                                peer_type='leecher'
                            )
                        except Exception as e:
                            return JsonResponse({'failure reason': str(e)}, status=400)
                    print("here7")
                    peers_list = Peer.objects.filter(
                        peerfile__file=file).exclude(peer_id=peer_id)

                    peers_serialized = PeerSerializer(
                        peers_list, many=True).data
                    response_data = {
                        'interval': 1800,
                        'complete': PeerFile.objects.filter(file=file, peer_type='seeder').count(),
                        'incomplete': PeerFile.objects.filter(file=file, peer_type='leecher').count(),
                        'peers': peers_serialized
                    }
                except Exception as e:
                    query_response = query_other_trackers_for_peers(info_hash)
                    print("here7.5")
                    if query_response == None:
                        response_data = {
                            'failure reason': 'File not found in this tracker'
                        }
                    else:
                        print("here7.6")
                        peers_list = query_response['peers']
                        trackerid = query_response['trackerid']
                        complete = query_response['complete']
                        incomplete = query_response['incomplete']
                        response_data = {
                            'trackerid': trackerid,
                            'interval': 1800,
                            'complete': complete or 0,
                            'incomplete': incomplete or 0,
                            'peers': peers_list
                        }
            print("here8")
            print(compact)
            if int(compact) == 1:
                print("here9")
                compact_peers = ''.join(
                    f"{peer['ip_address']}:{peer['port']},"
                    for peer in peers_serialized
                ).strip(',')
                response_data['peers'] = compact_peers

                return JsonResponse(response_data, status=200)
            else:
                print("here10")
                return JsonResponse(response_data, status=200)
        except Exception as e:
            return JsonResponse({'failure reason': str(e)}, status=402)


@csrf_exempt
def query_other_trackers_for_peers(info_hash):
    other_trackers = []

    for tracker_url in other_trackers:
        try:
            response = requests.get(tracker_url, params={
                                    'info_hash': info_hash})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Failed to query tracker {tracker_url}: {str(e)}")
            # response_data = {
            #     'trackerid': instance_tracker.tracker_id,
            #     'peers': peer_serializer
            # }
    return None


def getFile(request):
    if request.method == 'GET':
        try:
            info_hash = request.GET.get('info_hash')
            file = File.objects.get(hash_code=info_hash)
            peers_ids = PeerFile.objects.filter(file=file).values_list(
                'peer_id', flat=True)
            peers_list = Peer.objects.filter(peer_id__in=peers_ids)
            # print(peers_list)
            peer_serializer = PeerSerializer(peers_list, many=True).data
            response_data = {
                'trackerid': TRACKERID,
                'peers': peer_serializer,
                'complete': PeerFile.objects.filter(file=file, peer_type='seeder').count(),
                'incomplete': PeerFile.objects.filter(file=file, peer_type='leecher').count()
            }
            return JsonResponse(response_data, status=200)
        except File.DoesNotExist:
            return JsonResponse({'error': 'File not found'}, status=404)


def scrape(request):
    if request.method == 'GET':
        info_hashes = request.GET.getlist('info_hash')
        print(info_hashes)
        response_data = {'files': {}}

        for info_hash in info_hashes:
            try:
                file = File.objects.get(hash_code=info_hash)
                peers_list = Peer.objects.filter(
                    peerfile__file=file)
                peers_serialized = PeerSerializer(
                    peers_list, many=True).data

                response_data['files'][info_hash] = {
                    'complete': PeerFile.objects.filter(file=file, peer_type='seeder').count(),
                    'downloaded': PeerFile.objects.filter(file=file).count(),
                    'incomplete': PeerFile.objects.filter(file=file, peer_type='leecher').count(),
                    'peers': peers_serialized
                }
            except File.DoesNotExist:
                response_data['files'][info_hash] = {
                    'failure reason': 'File not found'
                }

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
