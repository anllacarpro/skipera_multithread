# https://github.com/serv0id/skipera
import time
import requests
from loguru import logger
import config
import threading
from concurrent.futures import ThreadPoolExecutor


class Watcher(object):
    def __init__(self, session: requests.Session, item: dict, metadata: dict, user_id: str, slug: str, course_id: str):
        self.metadata = metadata
        self.session = session
        self.item = item
        self.slug = slug
        self.user_id = user_id
        self.course_id = course_id

        self.session.headers.update({
            "x-csrf3-token": self.session.cookies["CSRF3-Token"]
        })

    def watch_item(self) -> None:
        if self.metadata["can_skip"]:
            logger.debug("Skippable video!")
            self.start_item()
            time.sleep(2)  # Wait a bit before ending
            self.update_progress()
            self.end_item()
        else:
            self.start_item()
            self.update_progress()
            self.end_item()

    def start_item(self):
        """
        Start watching a video item.
        """
        res = self.session.post(url=f'{config.BASE_URL}opencourse.v1/user/{self.user_id}/course/{self.slug}/'
                                    f'item/{self.item["id"]}/lecture/videoEvents/play?autoEnroll=false',
                                data='{"contentRequestBody":{}}')

        if res.status_code != 200:
            logger.error(f"Couldn't start video {self.item['name']}!")

    def end_item(self):
        """
        End watching a video item.
        Can be called directly for a skippable video.
        """
        res = self.session.post(url=f'{config.BASE_URL}opencourse.v1/user/{self.user_id}/course/{self.slug}/'
                                    f'item/{self.item["id"]}/lecture/videoEvents/ended?autoEnroll=false',
                                data='{"contentRequestBody":{}}')

        if res.status_code != 200:
            logger.error(f"Couldn't end watching {self.item['name']} - Status: {res.status_code}, Response: {res.text}")

    def update_progress(self):
        """
        Updates the watchtime progress of a video with parallel API calls.
        """
        video_duration_ms = self.item["timeCommitment"]  # Duration in milliseconds
        video_duration = video_duration_ms / 1000  # Convert to seconds

        # Wait 25% of the video duration
        wait_time = video_duration * 0.25

        logger.debug(f"Video duration: {video_duration:.0f}s, waiting {wait_time:.0f}s before marking complete")

        # Progress updates to be made
        progress_updates = [
            (int(video_duration_ms * 0.3), wait_time * 0.3),  # 30% progress
            (int(video_duration_ms * 0.7), wait_time * 0.3),  # 70% progress
            (video_duration_ms, wait_time * 0.4)  # 100% progress
        ]

        # Make progress updates in parallel where possible
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []

            for progress, delay in progress_updates:
                futures.append(executor.submit(self._update_progress_step, progress, delay))

            # Wait for all progress updates to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Progress update failed for {self.item['name']}: {e}")

    def _update_progress_step(self, progress_ms: int, delay: float):
        """
        Updates video progress to a specific percentage and waits.
        """
        try:
            res = self.session.put(
                url=f'{config.BASE_URL}onDemandVideoProgresses.v1/{self.user_id}~{self.course_id}~'
                f'{self.metadata["tracking_id"]}',
                json={
                    "videoProgressId": f'{self.user_id}~{self.course_id}~{self.metadata["tracking_id"]}',
                    "viewedUpTo": progress_ms
                }
            )

            if res.status_code != 204:
                logger.warning(f"Couldn't update progress to {progress_ms}ms for {self.item['name']} - Status: {res.status_code}")
            else:
                logger.debug(f"Updated progress to {progress_ms}ms for {self.item['name']}")

            if delay > 0:
                time.sleep(delay)

        except Exception as e:
            logger.error(f"Error in progress update for {self.item['name']}: {e}")
