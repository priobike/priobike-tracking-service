# Tracking Service

A microservice to receive tracks from users.

## REST Endpoint

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