from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import File, Peer, PeerFile, Tracker
import json
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import requests
from rest_framework.response import Response
import os
import uuid
from .serializer import PeerSerializer, FileSerializer, PeerFileSerializer
from django.views.decorators.csrf import csrf_exempt
from .ultis.utils import validate_required_fields
# TRACKERID = os.environ.get('TRACKERID')
# print(f"Tracker ID: {TRACKERID}")
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


def testAPI(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'API is working'}, status=200)


def addFileToTrackerList(request):
    if requests.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data['name']
            hash_code = data['hash_code']
            file = File.objects.create(name=name, hash_code=hash_code)
            return JsonResponse({'message': 'File added successfully'}, status=201)
        except KeyError:
            return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def announce(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)

            print("here1")
            required_fields = ['info_hash', 'peer_id', 'ip_address',
                               'port', 'uploaded', 'downloaded', 'left']
            print("here1")
            is_valid, error_message = validate_required_fields(
                data, required_fields)
            if is_valid == False:
                return JsonResponse({'failure reason': str(error_message)}, status=401)

            print("here1")
            info_hash = data.get('info_hash', None)
            peer_id = data.get('peer_id', None)
            ip_address = data.get('ip_address', None)
            port = data.get('port', None)
            uploaded = data.get('uploaded', None)
            downloaded = data.get('downloaded', None)
            left = data.get('left', None)
            event = data.get('event', None)
            compact = data.get('compact', 0)
            trackerid = data.get('trackerid', instance_tracker.tracker_id)
            print("here1")
            try:  # WHATEEVER THE EVENT IS, UPDATE THE PEER
                print("here1")
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
            # CREATE FILE OR SEEDING
            if event == "completed" or (left == 0 and downloaded >= 0):

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

                # peers_ids = PeerFile.objects.filter(file=file).values_list(
                #     'peer_id', flat=True)
                # peers_list = Peer.objects.filter(
                #     peer_id__in=peers_ids).exclude(peer_id=peer_id)

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

            # PEER STOPPED
            elif event == "stopped":
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
                try:
                    file = File.objects.get(hash_code=info_hash)

                    if event == 'started' or (downloaded > 0 and left > 0):
                        try:
                            peerfile, created = PeerFile.objects.update_or_create(
                                peer=peer,
                                file=File.objects.get(hash_code=info_hash),
                                peer_type='leecher'
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
                except File.DoesNotExist:
                    query_response = query_other_trackers_for_peers(info_hash)
                    if query_response == None:
                        response_data = {
                            'failure reason': 'File not found in any trackers'
                        }
                    else:
                        peers_list = query_response['peers']
                        trackerid = query_response['trackerid']
                        response_data = {
                            'trackerid': trackerid,
                            'interval': 1800,
                            'complete': PeerFile.objects.filter(file=file, peer_type='seeder').count(),
                            'incomplete': PeerFile.objects.filter(file=file, peer_type='leecher').count(),
                            'peers': peers_list
                        }

                return JsonResponse(response_data, status=200)
        except Exception as e:
            return JsonResponse({'failure reason': str(e)}, status=402)


@csrf_exempt
def query_other_trackers_for_peers(info_hash):
    other_trackers = [
        "http://127.0.0.1:8080/getfile"
    ]

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


def getFile(request, info_hash):
    if request.method == 'GET':
        try:
            file = File.objects.get(hash_code=info_hash)
            peers_ids = PeerFile.objects.filter(file=file).values_list(
                'peer_id', flat=True)
            peers_list = Peer.objects.filter(peer_id__in=peers_ids)
            # print(peers_list)
            peer_serializer = PeerSerializer(peers_list, many=True).data
            response_data = {
                'trackerid': instance_tracker.tracker_id,
                'peers': peer_serializer
            }
            return JsonResponse(response_data, status=200)
        except File.DoesNotExist:
            return JsonResponse({'error': 'File not found'}, status=404)


# def scrape(request):
#     if request.method == 'GET':
#         info_hash = request.GET.get('info_hash')
#     file = get_object_or_404(File, hash_code=info_hash)
#     peers = Peer.objects.filter(
#         peerpiece__piece__file=file, is_active=True)

#     response_data = {
#         'files': {
#             info_hash: {
#                 'complete': peers.filter(peerpiece__piece__file=file, peerpiece__piece__file__size=0).count(),
#                 'downloaded': peers.count(),
#                 'incomplete': peers.filter(peerpiece__piece__file=file, peerpiece__piece__file__size__gt=0).count()
#             }
#         }
#     }
#     return JsonResponse(response_data)
