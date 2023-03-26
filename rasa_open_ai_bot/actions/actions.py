from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import openai

import messages


class ActionDeleteRequestsHistory(Action):

    def name(self) -> Text:
        return "action_delete_requests_history"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        messages.messages_history = []
        dispatcher.utter_message(text="History is successfully deleted")

        return []


class ActionMakeSingleRequest(Action):

    def name(self) -> Text:
        return "action_make_single_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        openai.api_key = messages.api_key
        text = tracker.latest_message.get('text')
        response = openai.Completion.create(
            engine=messages.single_request_model,
            prompt=text,
            max_tokens=516,
            temperature=0.5
        )
        result = response['choices'][0]['text']

        dispatcher.utter_message(text=result)

        return []


class ActionMakeContextRequest(Action):

    def name(self) -> Text:
        return "action_make_context_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        openai.api_key = messages.api_key
        text = tracker.latest_message.get('text')
        messages.messages_history.append({"role": "user", "content": text})
        response = openai.ChatCompletion.create(
            model=messages.chat_model,
            messages=messages.messages_history
        )

        result = response['choices'][0]['message']['content']
        messages.messages_history.append({"role": "assistant", "content": result})
        dispatcher.utter_message(text=result)

        return []
