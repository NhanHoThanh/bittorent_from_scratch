Đảm bảo kết nối dc vs mysql. Tạo 1 database trống tên test_torret.

vào ./trackers/download_trackers/views.py và comment đoạn code sau (ở đầu):

```python
# Cái này để tạo multitrackers
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

```

Để đường dẫn terminal ở ./trackers/ (folder trackers đầu tiên), chạy các lệnh:

```terminal
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations trackers
python manage.py migrate
python manage.py runserver
```

uncomment đoạn code, vào file test.http để test thử API (Hiện tại chỉ cho 1 tracker)
