# 2. Endpoints

## 2.1 Announce Endpoint

**Endpoint:** `/announce`  
**Method:** `POST`  
**Purpose:** Register a peer’s presence, update peer status, and retrieve a list of peers sharing the same torrent file.
|

### Request Example:

```json
POST /api/v1/announce
Content-Type: application/json

{
  "peer_id": "ABC123XYZ456",
  "torrent_id": "9F86D081884C7D659A2FEAA0C55AD015",
  "port": 6881,
  "ip": "192.168.1.5",
  "uploaded": 1000000,
  "downloaded": 500000,
  "left": 250000,
  "event": "started",
  "pieces": [0, 1, 3, 4, 6, 7]
}
```

### Respond Example

```json
{
    "interval": 1800,
    "tracker_id": "TRACKER123",
    "peers": [
        {
            "peer_id": "XYZ789ABC123",
            "ip": "192.168.1.10",
            "port": 6881
        },
        {
            "peer_id": "LMN456OPQ789",
            "ip": "192.168.1.11",
            "port": 6882
        }
    ]
}
```
