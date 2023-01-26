from django.contrib import admin
from django.db import models
from tracks.fields import JSONField


class Track(models.Model):
    """
    A track is a collection of data points that are related to each other.

    The track stores the raw json data that is sent to the server.
    Additionally, it extracts some information that is useful for querying.
    """
    # The plain json data of the track.
    raw = JSONField()

    # The start time of the track in unix milliseconds since epoch.
    start_time = models.BigIntegerField()

    # The end time of the track in unix milliseconds since epoch.
    end_time = models.BigIntegerField()

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
    fields = ('raw', 'start_time', 'end_time', 'debug', 'backend', 'positioning_mode', 'date', 'user_id', 'session_id', 'device_type')
    readonly_fields = ('raw', 'start_time', 'end_time', 'debug', 'backend', 'positioning_mode', 'date', 'user_id', 'session_id', 'device_type')
