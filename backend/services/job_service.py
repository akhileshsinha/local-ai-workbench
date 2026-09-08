import os
import requests


class LinkedInJobService:

    def __init__(self):

        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = os.getenv("RAPIDAPI_HOST")

        self.base_url = (
            "https://linkedin-job-search-api.p.rapidapi.com"
        )

    def get_active_jobs(
        self,
        time_frame="24h",
        limit=10,
        offset=0,
        description_format="text",
        title="Frontend",
        location="India",
    ):

        url = f"{self.base_url}/active-jb"

        params = {
            "time_frame": time_frame,
            "limit": limit,
            "offset": offset,
            "description_format": description_format,
            "title": title,
            "location": location,
        }

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
            "Content-Type": "application/json",
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()