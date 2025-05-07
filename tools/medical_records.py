import os
import sys
import requests
import logging
from pydantic import BaseModel, Field
from datetime import datetime
from open_webui.env import GLOBAL_LOG_LEVEL
from open_webui.models.chats import Chats

logging.basicConfig(stream=sys.stdout, level=GLOBAL_LOG_LEVEL)
log = logging.getLogger(__name__)
log.setLevel(GLOBAL_LOG_LEVEL)


class Tools:
    class Valves(BaseModel):
        pass

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    # Add your custom tools using pure Python code here, make sure to add type hints
    # Use Sphinx-style docstrings to document your tools, they will be used for generating tools specifications
    # Please refer to function_calling_filter_pipeline.py file from pipelines project for an example

    async def get_user_medical_records(
        self,
        __user__: dict = {},
        __event_emitter__=None,
        __metadata__=None,
    ) -> str:
        """Get the user's official medical records.
        :return: The official medical records in markdown format
        """
        log.info("Agent fetched medical records.")
        chat = Chats.get_chat_by_id(__metadata__.get("chat_id"))
        chat = chat.chat
        history = chat.get("history", {})
        messages = history.get("messages", {})
        message_id = __metadata__.get("message_id")
        message = messages.get(message_id, [])
        status_history = message.get("statusHistory", [])
        status_history = [
            item["description"] for item in status_history if "description" in item
        ]

        log.info("Agent fetched medical records.")
        patient_id = __user__["name"]
        base_url = f"http://retrieval:8000/patient/{patient_id}/report"
        try:
            response = requests.get(base_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            status_history.append(f"Got health records")
            description = " | ".join(status_history)
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": description, "done": True},
                }
            )
            return response.text
        except requests.RequestException as e:
            status_history.append(f"No health records")
            description = " ".join(status_history)
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": description, "done": True},
                }
            )
            return f"Error fetching health records: {str(e)}"

    async def alert_help(
        self,
        criticality: int = 1,
        __user__: dict = {},
        __event_emitter__=None,
        __metadata__=None,
    ) -> str:
        """Only use this tool when you think the user needs immediate help. This causes dispatch to send ambulance to the users location and also call the user. The user's information is already available for the dispatch personnel.
        :param criticality: Criticality of immediate help on scale 1 to 5. Use 1 if the user would benefit a remote check-up from medical professional and 5 if it's likely that the user has suffered or witnessed likely fatal event.
        :return: Response from dispatch.
        """
        # Technically this tool could be connected to an actual alert system.

        chat = Chats.get_chat_by_id(__metadata__.get("chat_id"))
        chat = chat.chat
        history = chat.get("history", {})
        messages = history.get("messages", {})
        message_id = __metadata__.get("message_id")
        message = messages.get(message_id, [])
        status_history = message.get("statusHistory", [])
        status_history = [
            item["description"] for item in status_history if "description" in item
        ]
        status_history.append(f"Help alerted ({criticality})")
        description = " | ".join(status_history)
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": description, "done": True},
            }
        )

        log.info(f"Agent raised an alert with criticality {criticality}!")
        # Placeholder responses to the agent
        if criticality == 1:
            msg = "Task for remote check-up added. The call is estimated to happen likely tomorrow. Please ask if this is ok for the user."
        if criticality == 2:
            msg = "Task for remote check-up added. The call is estimated to happen likely tomorrow. Please ask if this is ok for the user."
        if criticality == 3:
            msg = "Task for remote check-up added. The call is estimated to happen in a few minutes by on duty officer. Let the user know about this."
        if criticality == 4:
            msg = "Task for check-up added. The call is estimated to happen in a few minutes by on duty officer. Let the user know about this."
        if criticality == 5:
            msg = "We will send an ambulance to the patients location. Estimated time of arrival: 15 minutes. Let the patient know that the help is on the way. Instruct the patient to keep phone line open."
        return msg
