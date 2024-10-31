from django.db import models


class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    hash_code = models.CharField(max_length=255)


class Peer(models.Model):
    peer_id = models.CharField(primary_key=True, max_length=255)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)


class PeerFile(models.Model):
    peer = models.ForeignKey(Peer, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    peer_type = models.CharField(max_length=10, choices=[
                                 ("leecher", "seeder")])


class PeerAuth(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    peer = models.ForeignKey(Peer, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[(
        'active', 'Active'), ('inactive', 'Inactive')])
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)


class Tracker(models.Model):
    tracker_id = models.AutoField(primary_key=True)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    status = models.CharField(max_length=10, choices=[(
        'active', 'Active'), ('inactive', 'Inactive')])
    last_sync = models.DateTimeField(auto_now=True)


# class FileAvailability(models.Model):
#     tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
#     peer = models.ForeignKey(Peer, on_delete=models.CASCADE)
#     file = models.ForeignKey(File, on_delete=models.CASCADE)
#     available_pieces = models.JSONField()


# class SyncLog(models.Model):
#     sync_id = models.AutoField(primary_key=True)
#     tracker = models.ForeignKey(
#         Tracker, on_delete=models.CASCADE, related_name='tracker')
#     target = models.ForeignKey(
#         Tracker, on_delete=models.CASCADE, related_name='target')
#     sync_time = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=10, choices=[(
#         'success', 'Success'), ('failure', 'Failure')])
