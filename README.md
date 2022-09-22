# Tracking Service

A microservice to receive tracks from users.

## REST Endpoint

### *POST* `/tracks/get/` - Get a single track with an API key.

#### Response format

Perform an example request with the example preset route:

```
curl "http://localhost:8000/tracks/get/?key=secret&pk=1"
```

Response:

```
{ "pk": <Primary key>, "data": <Raw track data> }
```

If anything else happens, the server will respond with a response code other than 200.

Parameters:

* `key` - The API key to use.
* `pk` - The primary key of the track to get.

### *POST* `/tracks/list/` - Get tracks with an API key.

#### Response format

Perform an example request with the example preset route:

```
curl "http://localhost:8000/tracks/list/?key=secret"
```

Response:

```
[
    { "pk": <Primary key>, "data": <Raw track data> },
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