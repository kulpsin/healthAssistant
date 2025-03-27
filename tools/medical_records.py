import os
import requests
from pydantic import BaseModel, Field
from datetime import datetime


class Tools:
    class Valves(BaseModel):
        patient_id: str = Field(
            default="7384d82c-2d1e-4595-99e4-f0ae962dddf1",
            description="Patient id in database.",
        )
        pass

    def __init__(self):
        self.valves = self.Valves()

    # Add your custom tools using pure Python code here, make sure to add type hints
    # Use Sphinx-style docstrings to document your tools, they will be used for generating tools specifications
    # Please refer to function_calling_filter_pipeline.py file from pipelines project for an example

    def get_user_medical_records(self, __user__: dict = {}) -> str:
        """
        Get the user's official medical records.
        :return: The official medical records in markdown format
        """
        base_url = (
            #"http://retrieval:8000/patient/7384d82c-2d1e-4595-99e4-f0ae962dddf1/report"
             f"http://retrieval:8000/patient/{self.valves.patient_id}/report"
        )
        try:
            response = requests.get(base_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            return response.text
        except requests.RequestException as e:
            return f"Error fetching health records: {str(e)}"
