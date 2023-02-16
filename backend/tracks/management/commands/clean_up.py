from django.core.management.base import BaseCommand
from tracks.models.track import Track

class Command(BaseCommand):
    help = """ Removes all tracks that don't meet certain criteria.
    For example, used to delete tracks that get created during development and thus don't contain any useful real world usage data. """

    def handle(self):
        print(f"Starting scheduled clean up of tracks... Current amount of tracks: {Track.objects.count()}")
        
        tracks = Track.objects.all()
        
        # Used for logging purposes.
        debug_count = 0
        staging_count = 0
        positioning_mode_count = 0
        
        for track in tracks:
            if track.debug:
                track.delete()
                debug_count += 1
                continue
            if track.backend == 'staging':
                track.delete()
                staging_count += 1
                continue
            if track.positioning_mode == 'follow18kmh' or track.positioning_mode == 'follow40kmh' or\
            track.positioning_mode == 'recordedDresden' or track.positioning_mode == 'recordedHamburg' or\
            track.positioning_mode == 'hamburgStatic1' or track.positioning_mode == 'dresdenStatic1' or\
            track.positioning_mode == 'dresdenStatic2':
                positioning_mode_count += 1
                track.delete()
                continue
            
        print(f""" Cleaned up {debug_count + staging_count + positioning_mode_count} tracks in total. Amount of tracks after clean up: {Track.objects.count()}
              Reasons: {debug_count}x times debug mode, {staging_count}x times staging backend, {positioning_mode_count}x times positioning mode. """)