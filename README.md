# priobike-tracking-service

A microservice to receive tracks and feedback from users.

[Learn more about PrioBike](https://github.com/priobike)

## Quickstart

The easiest way to run the tracking service is to use the contained `docker-compose`:
```
docker-compose up
```

## API and CLI

To balance load we run this service in two instances:
- The **worker** receives and checks tracks (can be scaled). Data stored in the worker DB can be lost at any time.
- The **manager** fetches tracks from the worker, tells them to flush their DB once new tracks are finished, and exposes a download API for all tracks. This service should be persisted.

### Tracks - REST Endpoint

#### MANAGER *GET* `/tracks/fetch/` - Get a single track with an API key.

#### Response format

Get the contents of a specific track. This request is performed against the manager.

```
curl "http://localhost:8000/tracks/fetch/?pk=\[012345\]&key=secret"
```

Example response:

```
{"metadata": {"startTime": 0, "endTime": 1, "debug": true, "backend": "staging", "positioningMode": "gnss", "userId": "[012345]", "sessionId": "[012345]", "deviceType": "iPhone 11,2", "deviceHeight": 812, "deviceWidth": 375, "appVersion": "1.0.0", "buildNumber": "1234", "statusSummary": {}, "taps": [], "selectedWaypoints": [], "routes": [], "predictions": []}, "gpsCSV": "timestamp,longitude,latitude,speed,accuracy\n0,0,0,0,0", "accelerometerCSV": "timestamp,x,y,z\n0,0,0,0", "gyroscopeCSV": "timestamp,x,y,z\n0,0,0,0", "magnetometerCSV": "timestamp,x,y,z\n0,0,0,0", "pk": 9}
```

If anything else happens, the server will respond with a response code other than 200.

Parameters:

* `key` - The API key to use.
* `pk` - The primary key of the track to get.

#### MANAGER *GET* `/tracks/list/` - Get tracks with an API key.

#### Response format

Get a list of tracks. This request is performed against the manager.

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

#### WORKER *POST* `/tracks/post/` - Post a new track.

#### Response format

Perform an example multipart request:

```
curl -X POST \
    -F gps.csv.gz='@example-gps.csv.gz' \
    -F accelerometer.csv.gz='@example-accelerometer.csv.gz' \
    -F magnetometer.csv.gz='@example-magnetometer.csv.gz' \
    -F gyroscope.csv.gz='@example-gyroscope.csv.gz' \
    -F metadata.json.gz='@example-metadata.json.gz' \
    http://localhost/tracks/post/
```

Response:

```
{
    "success": true
}
```

If anything else happens, the server will respond with a response code other than 200.

#### Feedback REST Endpoint

#### WORKER *POST* `/answers/post/` - Post a new answer.

#### Request format

Publish a new answer. The body of the POST request should contain at least the following information:

```
{
    "userId": <The id of the user. Max length: 100>,
    "questionText": <The text of the question. Max length: 300>
}
```

However, there are more fields that can be passed:

```
{
    "userId": <The id of the user. Max length: 100>,
    "questionText": <The text of the question. Max length: 300>,
    "questionImage": <The base 64 encoded image of this question, if provided. Max length: 10MB>,
    "sessionId": <The id of the session, if provided. Max length: 100>,
    "value": <The value of the answer, if provided. Max length: 1000>
}
```

#### Response format

Perform an example POST request:

```
curl --data "@example.json" http://localhost/answers/post/
```

Response:

```
{
    "success": true
}
```

If anything else happens, the server will respond with a response code other than 200.

## Generate Metrics for Prometheus

Prometheus metrics are generated on every sync call if the track count has changed.

### How to test metrics

Metric generation can be tested by adding tracks. Therefore different ```example-metadata-x.json``` can be used.
The metrics.txt is stored under ```/backend/data/``` and can be requested with: 

```
curl "http://localhost:8000/monitoring/metrics?api_key=secret"
```

#### Note
The metric only contains tracks, that did not charge the battery during tracks. 
The ```Track``` attribute ```has_battery_data``` is also false for tracks that did charge during the track.

## Contributing

We highly encourage you to open an issue or a pull request. You can also use our repository freely with the `MIT` license.

Every service runs through testing before it is deployed in our release setup. Read more in our [PrioBike deployment readme](https://github.com/priobike/.github/blob/main/wiki/deployment.md) to understand how specific branches/tags are deployed.

## Anything unclear?

Help us improve this documentation. If you have any problems or unclarities, feel free to open an issue.
