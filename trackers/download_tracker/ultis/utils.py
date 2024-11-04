from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Peer, File
from datetime import datetime


# def add_peer(info_hash, peer_id, ip_address, port, uploaded, downloaded, left, event):
#     peer, created = Peer.objects.update_or_create(
#         peer_id=peer_id,
#         defaults={
#             'ip_address': ip_address,
#             'port': port,
#             'last_seen': datetime.now(),
#             'is_active': event != 'stopped'
#         }
#     )

#     if event == 'stopped':
#         peer.is_active = False
#         peer.save()

#     file = File.objects.get(hash_code=info_hash)
#     PeerPiece.objects.update_or_create(
#         peer=peer,
#         piece__file=file,
#         defaults={'download_at': datetime.now()}
#     )


# def get_peers_by_torrent(info_hash):
#     file = File.objects.get(hash_code=info_hash)
#     peers = Peer.objects.filter(peerpiece__piece__file=file, is_active=True)
#     return peers


def validate_required_fields(data, required_fields):
    missing_fields = [
        field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None


def generate_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def authorize_peer(request):
    jwt_authenticator = JWTAuthentication()
    try:
        user, token = jwt_authenticator.authenticate(request)
        if user is None or not user.is_active:
            raise PermissionDenied("Peer is not active")
        return user
    except Exception as e:
        raise PermissionDenied(f"Authorization failed: {str(e)}")
