# https://github.com/serv0id/skipera
import click
import requests
import config
import os
from loguru import logger
from assessment.solver import GradedSolver
from watcher.watch import Watcher
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue


class Skipera(object):
    def __init__(self, course: str, llm: bool, eva: bool, max_workers: int = 4):
        self.user_id = None
        self.course_id = None
        self.base_url = config.BASE_URL
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.session.cookies.update(config.COOKIES)
        self.course = course
        self.llm = llm
        self.eva = eva
        self.max_workers = max_workers
        self.session_lock = threading.Lock()
        if not self.get_userid():
            self.login()

    def login(self):
        """Attempt to authenticate using cookies.

        This project originally relied on pre-set cookies. If `get_userid`
        fails we try the following, in order:
        - Use `COURSES_CAUTH` and `COURSES_CSRF3_TOKEN` environment variables
        - Use `config.COOKIES` values if present
        - Prompt interactively for `CAUTH` and `CSRF3-Token` cookie values

        The function will exit the program if authentication cannot be
        established. This avoids hardcoding credentials in the repository.
        """
        # 1) Try environment variables
        cauth = os.getenv("COURSES_CAUTH")
        csrf = os.getenv("COURSES_CSRF3_TOKEN")

        # 2) Fall back to values from config.COOKIES (already loaded)
        if not cauth:
            cauth = config.COOKIES.get("CAUTH")
        if not csrf:
            csrf = config.COOKIES.get("CSRF3-Token")

        if cauth and csrf:
            self.session.cookies.update({"CAUTH": cauth, "CSRF3-Token": csrf})
            if self.get_userid():
                logger.info("Authenticated using provided cookies")
                return

        # 3) Interactive prompt fallback
        logger.info("Authentication required. You can provide cookie values interactively or set env vars `COURSES_CAUTH` and `COURSES_CSRF3_TOKEN`.")
        try:
            cauth_input = input("Enter CAUTH cookie value (leave blank to abort): ").strip()
            csrf_input = input("Enter CSRF3-Token cookie value (leave blank to abort): ").strip()
        except Exception:
            logger.error("Interactive input failed; aborting login.")
            raise SystemExit(1)

        if not cauth_input or not csrf_input:
            logger.error("No cookies provided; cannot authenticate.")
            raise SystemExit(1)

        self.session.cookies.update({"CAUTH": cauth_input, "CSRF3-Token": csrf_input})
        if not self.get_userid():
            logger.error("Login failed with provided cookies.")
            raise SystemExit(1)
        logger.info("Authenticated using interactive cookies")

    def get_userid(self) -> bool:
        r = self.session.get(self.base_url + "adminUserPermissions.v1?q=my").json()
        try:
            self.user_id = r["elements"][0]["id"]
            logger.info("User ID: " + self.user_id)
        except KeyError:
            if r.get("errorCode"):
                logger.error("Error Encountered: " + r["errorCode"])
            return False
        return True

    def get_course(self) -> None:
        r = self.session.get(self.base_url + f"onDemandCourseMaterials.v2/", params={
            "q": "slug",
            "slug": self.course,
            "includes": "modules,lessons,passableItemGroups,passableItemGroupChoices,passableLessonElements,items,"
                        "tracks,gradePolicy,gradingParameters,embeddedContentMapping",
            "fields": "moduleIds,onDemandCourseMaterialModules.v1(name,slug,description,timeCommitment,lessonIds,"
                      "optional,learningObjectives),onDemandCourseMaterialLessons.v1(name,slug,timeCommitment,"
                      "elementIds,optional,trackId),onDemandCourseMaterialPassableItemGroups.v1(requiredPassedCount,"
                      "passableItemGroupChoiceIds,trackId),onDemandCourseMaterialPassableItemGroupChoices.v1(name,"
                      "description,itemIds),onDemandCourseMaterialPassableLessonElements.v1(gradingWeight,"
                      "isRequiredForPassing),onDemandCourseMaterialItems.v2(name,originalName,slug,timeCommitment,"
                      "contentSummary,isLocked,lockableByItem,itemLockedReasonCode,trackId,lockedStatus,itemLockSummary,"
                      "customDisplayTypenameOverride),onDemandCourseMaterialTracks.v1(passablesCount),"
                      "onDemandGradingParameters.v1(gradedAssignmentGroups),"
                      "contentAtomRelations.v1(embeddedContentSourceCourseId,subContainerId)",
            "showLockedItems": True
        }).json()

        self.course_id = r["elements"][0]["id"]

        logger.info("Course ID: " + self.course_id)
        logger.info("Number of Modules: " + str(len(r["linked"]["onDemandCourseMaterialModules.v1"])))
        logger.info(f"Processing {len(r['linked']['onDemandCourseMaterialItems.v2'])} items with {self.max_workers} workers...")

        items = r["linked"]["onDemandCourseMaterialItems.v2"]

        # Group items by type for parallel processing
        videos = []
        readings = []
        assessments = []

        for item in items:
            if item["contentSummary"]["typeName"] == "lecture":
                if not self.eva:
                    videos.append(item)
            elif item["contentSummary"]["typeName"] == "supplement":
                if not self.eva:
                    readings.append(item)
            elif item["contentSummary"]["typeName"] in ["ungradedAssignment", "staffGraded"]:
                if self.llm or self.eva:
                    assessments.append(item)

        # Process items concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            # Submit video processing tasks
            for video in videos:
                logger.info(f"Queueing video: {video['name']}")
                futures.append(executor.submit(self._process_video, video))

            # Submit reading processing tasks
            for reading in readings:
                logger.info(f"Queueing reading: {reading['name']}")
                futures.append(executor.submit(self._process_reading, reading))

            # Submit assessment processing tasks
            for assessment in assessments:
                logger.info(f"Queueing assessment: {assessment['name']}")
                futures.append(executor.submit(self._process_assessment, assessment))

            # Wait for all tasks to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Task failed: {e}")

        logger.info("All items processed!")

    def _process_video(self, item: dict):
        """Process a single video item"""
        try:
            logger.info(f"Processing video: {item['name']}")
            metadata = self.get_video_metadata(item["id"])

            # Create a new session for thread safety
            thread_session = self._create_thread_session()
            watcher = Watcher(thread_session, item, metadata, self.user_id, self.course, self.course_id)
            watcher.watch_item()
            logger.info(f"Completed video: {item['name']}")
        except Exception as e:
            logger.error(f"Error processing video {item['name']}: {e}")

    def _process_reading(self, item: dict):
        """Process a single reading item"""
        try:
            logger.info(f"Processing reading: {item['name']}")
            thread_session = self._create_thread_session()
            self.read_item_threaded(thread_session, item["id"])
            logger.info(f"Completed reading: {item['name']}")
        except Exception as e:
            logger.error(f"Error processing reading {item['name']}: {e}")

    def _process_assessment(self, item: dict):
        """Process a single assessment item"""
        try:
            logger.info(f"Processing assessment: {item['name']}")
            thread_session = self._create_thread_session()
            solver = GradedSolver(thread_session, self.course_id, item["id"])
            solver.solve()
            logger.info(f"Completed assessment: {item['name']}")
        except Exception as e:
            logger.error(f"Error processing assessment {item['name']}: {e}")

    def _create_thread_session(self) -> requests.Session:
        """Create a new session for thread safety"""
        with self.session_lock:
            thread_session = requests.Session()
            thread_session.headers.update(config.HEADERS)
            thread_session.cookies.update(config.COOKIES)
            return thread_session

    def read_item_threaded(self, session: requests.Session, item_id: str):
        """Thread-safe version of read_item"""
        r = session.post(self.base_url + "onDemandSupplementCompletions.v1", json={
            "courseId": self.course_id,
            "itemId": item_id,
            "userId": int(self.user_id)
        })
        if "Completed" not in r.text:
            logger.debug(f"Couldn't read item {item_id}!")

    def get_video_metadata(self, item_id: str) -> dict:
        r = self.session.get(self.base_url + f"onDemandLectureVideos.v1/{self.course_id}~{item_id}", params={
            "includes": "video",
            "fields": "disableSkippingForward,startMs,endMs"
        }).json()

        return {"can_skip": not r["elements"][0]["disableSkippingForward"],
                "tracking_id": r["linked"]["onDemandVideos.v1"][0]["id"]}

    def watch_item(self, item: dict, metadata: dict) -> None:
        watcher = Watcher(self.session, item, metadata, self.user_id, self.course, self.course_id)
        watcher.watch_item()

    def read_item(self, item_id) -> None:
        r = self.session.post(self.base_url + "onDemandSupplementCompletions.v1", json={
            "courseId": self.course_id,
            "itemId": item_id,
            "userId": int(self.user_id)
        })
        if "Completed" not in r.text:
            logger.debug("Couldn't read item!")


@logger.catch
@click.command()
@click.option('--slug', required=True, help="The course slug from the URL")
@click.option('--llm', is_flag=True, help="Whether to use an LLM to solve graded assignments (completes videos + assessments).")
@click.option('--eva', is_flag=True, help="Only solve graded assessments, skip videos and readings.")
@click.option('--workers', default=4, type=int, help="Number of parallel workers for processing (default: 4).")
def main(slug: str, llm: bool, eva: bool, workers: int) -> None:
    if eva and llm:
        logger.warning("Both --llm and --eva flags provided. Using --eva mode (assessments only).")
        llm = False

    logger.info(f"Starting Skipera with {workers} parallel workers")
    skipera = Skipera(slug, llm, eva, workers)
    skipera.get_course()


if __name__ == '__main__':
    main()
