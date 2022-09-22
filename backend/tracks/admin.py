from django.contrib import admin

from tracks.models import Track, TracksAdmin

admin.site.register(Track, TracksAdmin)
