import json
import socket
import tempfile
import time

import requests
from answers.models import Answer
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from tracks.models import Track


class Command(BaseCommand):
    """
    This command is executed by the manager to download data from the workers.

    The command goes through all workers, downloads new tracks, and inserts them into the database.
    """

    def add_arguments(self, parser):
        parser.add_argument("--host", type=str, help="The host to sync from.")
        parser.add_argument("--port", type=int, help="The port to sync from.")
        parser.add_argument("--interval", type=int, default=60, help="The interval in seconds to sync.")

    def handle(self, *args, **options):
        if not options["host"]:
            raise ValueError("Missing required argument: --host")
        if not options["port"]:
            raise ValueError("Missing required argument: --port")
        if not options["interval"]:
            raise ValueError("Missing required argument: --interval")
        
        host = options["host"]
        port = options["port"]
        interval = options["interval"]

        while True:
            tracks_before = Track.objects.count()
            answers_before = Answer.objects.count()

            # Get the data from the workers.
            worker_hosts = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
            worker_ips = [worker_host[4][0] for worker_host in worker_hosts]

            # Fetch the status for now
            for worker_ip in worker_ips:
                print(f"Syncing with worker: {worker_ip}")
                url = f"http://{worker_ip}:{port}/sync/sync"
                try:
                    response = requests.get(url, params={"key": settings.SYNC_KEY})
                except requests.exceptions.ConnectionError:
                    print(f"Worker {worker_ip} seems offline")
                    continue
                if response.status_code != 200:
                    print(f"Failed to sync with worker {worker_ip}: status {response.status_code}")
                    continue
                if not response.text:
                    print(f"Empty response from worker {worker_ip}")
                    continue
                print(f"Loaded fixtures from worker {worker_ip}")

                # ---------------------
                # This section is time critical: we don't want to wait too long
                # until telling the worker to delete all data.
                with tempfile.TemporaryDirectory() as temp_dir:
                    filepath = f"{temp_dir}/fixtures.xml"
                    with open(filepath, "w") as f:
                        f.write(response.text)
                    call_command("loaddata", "--format=xml", filepath)
                # ---------------------

                # Tell the worker to delete all data
                url = f"http://{worker_ip}:{port}/sync/sync"
                response = requests.delete(url, data=json.dumps({"key": settings.SYNC_KEY}))
                if response.status_code != 200:
                    print(f"Failed to delete data on worker {worker_ip}: status {response.status_code}")
                    continue
                print(f"Deleted data on worker {worker_ip}")

            # Delete all answers that are not associated with a valid track.
            session_ids_to_keep = Track.objects.values('session_id').distinct()
            # Delete all answers that are not associated with a valid track.
            Answer.objects.exclude(session_id__in=session_ids_to_keep).delete()

            # Check if we need to generate new metrics
            tracks_after = Track.objects.count()
            answers_after = Answer.objects.count()
            if tracks_after > tracks_before or answers_after > answers_before:
                new_tracks = tracks_after - tracks_before
                new_answers = answers_after - answers_before
                print(f"Inserted {new_tracks} new tracks and {new_answers} new answers into the database.")
                call_command("generate_metrics")
                print("Updated promeheus metrics.")

            print(f"Finished sync routine. Sleeping for {interval} seconds.")
            time.sleep(interval)