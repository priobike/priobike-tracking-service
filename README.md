# Tracking Service

A microservice to receive tracks from users.

## REST Endpoint

### *GET* `/tracks/fetch/` - Get a single track with an API key.

#### Response format

Perform an example request with the example preset route:

```
curl "http://localhost:8000/tracks/fetch/?pk=1&key=secret"
```

Response:

```
{ "pk": <Primary key>, "data": <Raw track data> }
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
                "deviceId": track.device_id,
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
* `deviceId` - The kind of device ID to look for. Default: `None` (Include all).
* `page` - The page to get. Default: `1`.
* `pageSize` - The page size to get. Default: `10`. Limited to `100`.

### *POST* `/tracks/post/` - Post a new track.

#### Response format

Perform an example request with the example preset route:

```
curl --data "@example-track.json" http://localhost:8000/tracks/post/
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