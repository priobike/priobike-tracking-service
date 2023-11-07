import pandas as pd
from io import StringIO
from django.core.management.base import BaseCommand
from tracks.models import Track
from answers.models import Answer

class Command(BaseCommand):
    help = """ Removes all tracks that don't meet certain criteria.
    For example, used to delete tracks that get created during development and thus don't contain any useful real world usage data. """
    
    def validate_track(self, track):
        if track.debug:
            raise ValueError("Track is in debug mode.")
        if track.positioning_mode != "gnss":
            raise ValueError("Track is created using mock position mode.")
        
        track_gps_data = pd.read_csv(StringIO(track.gps_csv), sep=",")
        
        if len(track_gps_data.index) < 6:
            raise ValueError("Track is too short.")
        
        if track.backend == 'staging':
            # Bounding box Dresden 
            min_lat, max_lat = 50.8, 51.3
            min_lon, max_lon = 13.2, 14.3
        elif track.backend == 'production':
            # Bounds for Hamburg
            min_lat, max_lat = 53.1, 54.0
            min_lon, max_lon = 9.1, 10.9
        elif track.backend == 'release':
            # Bounds for Hamburg
            min_lat, max_lat = 53.1, 54.0
            min_lon, max_lon = 9.1, 10.9
        else:
            raise ValueError("Track is not from a valid backend.")
        
        # Get the maximum and minimum latitude and longitude values of the track.
        try:
            track_max_lat = track_gps_data['latitude'].max()
            track_min_lat = track_gps_data['latitude'].min()
            track_max_lon = track_gps_data['longitude'].max()
            track_min_lon = track_gps_data['longitude'].min()
        except KeyError as e:
            print(f"Track with id {track.id} has no latitude or longitude column (in GPS data).")
            return
        
        # Check if the track is fully within the bounding box of the city.
        if track_max_lat > max_lat or track_min_lat < min_lat or track_max_lon > max_lon or track_min_lon < min_lon:
            raise ValueError("Track is out of bounding box of the city.")

    def handle(self, *args, **options):
        print(f"Starting scheduled clean up of tracks and feedback... Current number of tracks: {Track.objects.count()}. Current number of answers: {Answer.objects.count()}.")
        
        track_ids_to_delete = []
        
        for track in Track.objects.all():
            try:
                self.validate_track(track=track)
            except ValueError as e:
                track_ids_to_delete.append(track.id)
                print(f"Deleting track with id {track.id}. Reason: {e}")
                
        Track.objects.filter(id__in=track_ids_to_delete).delete()
        
        session_ids_to_keep = Track.objects.values('session_id').distinct()
        # Delete all answers that are not associated with a valid track.
        Answer.objects.exclude(session_id__in=session_ids_to_keep).delete()
        
        print(f"Finished clean up of tracks. Number of tracks after clean up: {Track.objects.count()}. Number of answers after clean up: {Answer.objects.count()}.")