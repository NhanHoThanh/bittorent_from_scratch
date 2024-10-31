from rest_framework import serializers
from .models import Peer, File, PeerFile


class PeerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peer
        fields = '__all__'  # Or specify specific fields if needed


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'  # Or specify specific fields if needed


class PeerFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeerFile
        fields = '__all__'  # Or specify specific fields if needed
