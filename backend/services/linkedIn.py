import os
import requests


class LinkedInJobsService:

    def __init__(self):

        self.api_key = os.getenv(
            "RAPIDAPI_KEY"
        )

        self.api_host = os.getenv(
            "RAPIDAPI_HOST"
        )

        self.base_url = (
            "https://linkedin-job-search-api.p.rapidapi.com/active-jb-count/"
        )

    def get_latest_jobs(self):

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
        }

        response = requests.get(
            self.base_url,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()