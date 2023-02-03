# Tracking Service

A microservice to receive tracks from users.

## REST Endpoint

### *GET* `/tracks/fetch/` - Get a single track with an API key.

#### Response format

Perform an example request with the example preset route:

```
curl "http://localhost:8000/tracks/fetch/?pk=1&key=secret"
```

Example response:

```
{"metadata": {"startTime": 0, "endTime": 1, "debug": true, "backend": "staging", "positioningMode": "gnss", "userId": "[012345]", "sessionId": "[012345]", "deviceType": "iPhone 11,2", "deviceHeight": 812, "deviceWidth": 375, "appVersion": "1.0.0", "buildNumber": "1234", "statusSummary": {}, "taps": [], "selectedWaypoints": [], "routes": [], "predictions": []}, "gpsCSV": "timestamp,longitude,latitude,speed,accuracy\n0,0,0,0,0", "accelerometerCSV": "timestamp,x,y,z\n0,0,0,0", "gyroscopeCSV": "timestamp,x,y,z\n0,0,0,0", "magnetometerCSV": "timestamp,x,y,z\n0,0,0,0", "pk": 9}
```

If anything else happens, the server will respond with a response code other than 200.

Parameters:

* `key` - The API key to use.
* `pk` - The primary key of the track to get.

### *GET* `/tracks/list/` - Get tracks with an API key.

#### Response format

Perform an example request with the example preset route:

```
curl "http://localhost:8000/tracks/list/?key=secret"
```

Response:

```
[
    { 
        "results": [
            {
                "pk": track.pk,
                "startTime": track.start_time,
                "endTime": track.end_time,
                "debug": track.debug,
                "backend": track.backend,
                "positioningMode": track.positioning_mode,
                "deviceType": track.device_type,
                "userId": track.user_id,
            },
            ...
        ], 
        "page": page,
        "pageSize": page_size,
        "totalPages": tracks.paginator.num_pages,
    },
    ...
]
```

If anything else happens, the server will respond with a response code other than 200.

Parameters: 

* `key` - The API key to use.
* `from` - The start date to get tracks from. Format: unix milliseconds. Default: `None` (Include all).
* `to` - The end date to get tracks to. Format: unix milliseconds. Default: `None` (Include all).
* `debug` - If set to `false`, the server won't return debug tracks. Default: `None` (Include all).
* `backend` - The kind of backend to look for. Default: `None` (Include all).
* `positioning` - The kind of positioning to look for. Default: `None` (Include all).
* `deviceType` - The kind of device type to look for. Default: `None` (Include all).
* `userId` - The kind of user ID to look for. Default: `None` (Include all).
* `page` - The page to get. Default: `1`.
* `pageSize` - The page size to get. Default: `10`. Limited to `100`.

### *POST* `/tracks/post/` - Post a new track.

#### Response format

Perform an example multipart request:

```
curl -X POST \
    -F gps.csv.gz='@example-gps.csv.gz' \
    -F accelerometer.csv.gz='@example-accelerometer.csv.gz' \
    -F magnetometer.csv.gz='@example-magnetometer.csv.gz' \
    -F gyroscope.csv.gz='@example-gyroscope.csv.gz' \
    -F metadata.json.gz='@example-metadata.json.gz' \
    http://localhost:8000/tracks/post/
```

Response:

```
{
    "success": true
}
```

If anything else happens, the server will respond with a response code other than 200.

## Debug Setup

To validate that everything works behind our reverse proxies, we provide a docker-compose setup with 2 NGINX proxies.