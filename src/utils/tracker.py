import json

from loguru import logger
from config_reader import config


class Tracker:
    def __init__(self):
        self.feedback_ratings = self._load_feedback_ratings()

    def _load_feedback_ratings(self):
        """Feedback data loader"""
        try:
            with open(config.json_file, "r") as file:
                feedback_ratings = json.load(file)
        except Exception:
            feedback_ratings = {}
            logger.error("Could not load feedback json", action="load_feedback_ratings")

        return feedback_ratings

    def _dump_feedback_ratings(self):
        """Feedback data exporter"""
        try:
            with open(config.json_file, "w") as file:
                json.dump(self.feedback_ratings, file)

        except Exception as e:
            logger.error(f"Could not dump feedback json {e.args}", action="dump_feedback_ratings")


tracker = Tracker()
