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

TRACKERID = os.environ.get('TRACKERID')
print(f"Tracker ID: {TRACKERID}")
try:
    instance_tracker = Tracker.objects.get(tracker_id=TRACKERID)
except ObjectDoesNotExist:
    print(f"Tracker with tracker_id {
          TRACKERID} does not exist. Creating new tracker...")
    instance_tracker = Tracker.objects.create(
        tracker_id=TRACKERID,
        ip_address="localhost",
        port=8000,
        status='active',
    )


def query_other_trackers_for_peers(info_hash):
    # Example list of other trackers
    return None
    other_trackers = [
        "http://tracker1.example.com/getfile",
        "http://tracker2.example.com/getfile"
    ]

    for tracker_url in other_trackers:
        response = requests.get(tracker_url, params={'info_hash': info_hash})
        if response.status_code == 200:
            return response.json()
            # response_data = {
            #     'trackerid': instance_tracker.tracker_id,
            #     'peers': peer_serializer
            # }


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
            info_hash = data['info_hash']
            peer_id = data['peer_id']
            ip_address = data['ip_address']
            port = data['port']
            uploaded = data['uploaded']
            downloaded = data['downloaded']
            left = data['left']
            event = data['event']
            # compact = data['compact']
            # trackerid = data['tracker_id']

            # ADD OR UPADE PEER
            peer, created = Peer.objects.update_or_create(
                peer_id=peer_id,
                defaults={
                    'ip_address': ip_address,
                    'port': port,
                    'last_seen': datetime.now(),
                    'is_active': event != 'stopped'
                }
            )

            # IF CREATE FILE OR COMPLETE AND START SEEDING
            if event == "completed" or (left == 0 and downloaded >= 0):
                try:
                    file = File.objects.get(hash_code=info_hash)
                    peerfile, created = PeerFile.objects.update_or_create(
                        peer=peer,
                        file=File.objects.get(hash_code=info_hash),
                        peer_type='seeder'
                    )
                except File.DoesNotExist:
                    File.objects.create(
                        hash_code=info_hash)

                    peerfile, created = PeerFile.objects.update_or_create(
                        peer=peer,
                        file=File.objects.get(hash_code=info_hash),
                        peer_type='seeder'
                    )

            # # IF EVENT IS STARTED AND LEFT IS NOT 0 THEN ADD TO LEECHER
            # elif event == "started" and left > 0:
            #     try:
            #         file = File.objects.get(hash_code=info_hash)
            #         peerfile, created = PeerFile.objects.update_or_create(
            #             peer=peer,
            #             file=File.objects.get(hash_code=info_hash),
            #             peer_type='leecher'
            #         )
            #     except File.DoesNotExist:
            #         File.objects.create(
            #             hash_code=info_hash)

            #         peerfile, created = PeerFile.objects.update_or_create(
            #             peer=peer,
            #             file=File.objects.get(hash_code=info_hash),
            #             peer_type='leecher'
            #         )

            # IF FILE THEN RETURN IF NOT THEN SEARCH FILES IN OTHER TRACKERS
            try:
                file = File.objects.get(hash_code=info_hash)
                # print("here")
                # print(file)
                # return JsonResponse(FileSerializer(file).data)
                if event == "started" and left > 0 and downloaded > 0:
                    peerfile, created = PeerFile.objects.update_or_create(
                        peer=peer,
                        file=File.objects.get(hash_code=info_hash),
                        peer_type='leecher'
                    )
                peers_ids = PeerFile.objects.filter(file=file).values_list(
                    'peer_id', flat=True)
                peers_list = Peer.objects.filter(peer_id__in=peers_ids)
                # print(peers_list)
                peer_serializer = PeerSerializer(peers_list, many=True).data
                response_data = {
                    'interval': 1800,
                    'complete': PeerFile.objects.filter(file=file, peer_type='seeder').count(),
                    'incomplete': PeerFile.objects.filter(file=file, peer_type='leecher').count(),
                    'peers': peer_serializer
                }
                # print(peer_serializer)
                # return JsonResponse(peer_serializer, status=200, safe=False)
            except File.DoesNotExist:
                query_response = query_other_trackers_for_peers(info_hash)
                if query_response == None:
                    response_data = {
                        'failure reason': 'File not found in any tracker'
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
        except KeyError:
            return JsonResponse({'error': 'Invalid request'}, status=400)


def getFile(request, info_hash):
    if request.method == 'GET':
        try:
            file = File.objects.get(hash_code=info_hash)
            # print("here")
            # print(file)
            # return JsonResponse(FileSerializer(file).data)
            peers_ids = PeerFile.objects.filter(file=file).values_list(
                'peer_id', flat=True)
            peers_list = Peer.objects.filter(peer_id__in=peers_ids)
            # print(peers_list)
            peer_serializer = PeerSerializer(peers_list, many=True).data
            response_data = {
                'trackerid': instance_tracker.tracker_id,
                'peers': peer_serializer
            }
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
