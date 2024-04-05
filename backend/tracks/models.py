from django.contrib import admin
from django.db import models
from tracks.fields import JSONField


class Track(models.Model):
    """
    A track is a collection of data points that are related to each other.

    The track stores the raw json data that is sent to the server.
    Additionally, it extracts some information that is useful for querying.
    """

    ####### Fields that are extracted from the raw json data for querying. #######

    # The start time of the track in unix milliseconds since epoch.
    start_time = models.BigIntegerField()

    # The end time of the track in unix milliseconds since epoch.
    # Can be null if the app was terminated before the track was finished.
    end_time = models.BigIntegerField(null=True, blank=True)

    # If the track was created in debug mode.
    debug = models.BooleanField(default=False)

    # The type of backend that was used to create the track.
    backend = models.CharField(max_length=255, default='unknown')

    # The positioning mode that was used to create the track.
    positioning_mode = models.CharField(max_length=255, default='unknown')

    # The user id.
    user_id = models.CharField(max_length=255, default='unknown')

    # The session id.
    session_id = models.CharField(max_length=255, default='unknown')

    # The device model.
    device_type = models.CharField(max_length=255, default='unknown')

    # The date the track was received.
    date = models.DateTimeField(auto_now_add=True)

    # The bike type that was used to create the track.
    bike_type = models.CharField(max_length=255, default='unknown')

    # The preference type that was used to create the track.
    preference_type = models.CharField(max_length=255, default='unknown')

    # The activity type that was used to create the track.
    activity_type = models.CharField(max_length=255, default='unknown')

    # Whether the track is able to be analyzed for battery consumption.
    can_battery_analysis = models.BooleanField(blank=True, null=True)

    # The average battery consumption of the track.
    avg_battery_consumption = models.FloatField(blank=True, null=True)

    ####### Fields that contain raw data. #######

    # The plain json data of the track.
    metadata = JSONField()

    # The CSV file containing the GPS data.
    gps_csv = models.TextField(null=True, blank=True)

    # The CSV file containing the accelerometer data.
    accelerometer_csv = models.TextField(null=True, blank=True)

    # The CSV file containing the gyroscope data.
    gyroscope_csv = models.TextField(null=True, blank=True)

    # The CSV file containing the magnetometer data.
    magnetometer_csv = models.TextField(null=True, blank=True)

    def __str__(self):
        output = ""
        if self.debug:
            output += "[DEBUG] "
        output += f"Positioning: {self.positioning_mode}, Backend: {self.backend}, Date: {self.date}"
        output += f", Device: {self.device_type} ({self.user_id})"
        return output

    class Meta:
        ordering = ['-date']


class TracksAdmin(admin.ModelAdmin):
    fields = (
        'start_time',
        'end_time',
        'debug',
        'backend',
        'positioning_mode',
        'user_id',
        'session_id',
        'device_type',
        'date',
        'metadata',
        'gps_csv',
        'accelerometer_csv',
        'gyroscope_csv',
        'magnetometer_csv',
    )
    readonly_fields = (
        'start_time',
        'end_time',
        'debug',
        'backend',
        'positioning_mode',
        'user_id',
        'session_id',
        'device_type',
        'date',
        'metadata',
        'gps_csv',
        'accelerometer_csv',
        'gyroscope_csv',
        'magnetometer_csv',
    )
