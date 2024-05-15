from celery import Celery
from celery import Task
from utils.utils import process_results
from redashAPI import RedashAPIClient
import os
from dotenv import load_dotenv

# load the .env file
load_dotenv()

# Get the values of the Keys from the environment variables or the .env file
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
REDASH_API_KEY = os.environ.get("REDASH_API_KEY")
REDASH_URL = os.environ.get("REDASH_URL")

class CeleryManage:
    def __init__(self, app):
        self.celery = Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL']
        )
        self.celery.conf.update(app.config)
        self.redash_api = RedashAPIClient(REDASH_API_KEY, REDASH_URL)

    def init_app(self, app):
        self.celery.conf.update(app.config)


    class RedashQueryTask(self.celery.Task):
        name = "redash_query_task"  # Name your task for identification

        def run(self, query):
            """
            Executes the Redash query and updates the task state with results or errors.
            """
            try:
                self.update_state(state='STARTED', meta={'progress': 0})

                # Fetching results and processing logic
                results = self.redash_api.query_and_wait_result(1, query)
                processed_results = process_results(results)

                self.update_state(state='SUCCESS', meta={'result': processed_results})
            except Exception as e:
                self.update_state(state='FAILURE', meta={'error': str(e)})
                raise  # Re-raise the exception for Celery to handle retries

