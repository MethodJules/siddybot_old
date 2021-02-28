from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.db_call import DbCall
#import base64,cv2

class YesNoQuestionsOrganizationAction(Action):

  def name(self) -> Text:
      return "action_yes_no_questions_organization"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_yes_no_questions_organization")
    intent = tracker.latest_message(text)
    attribute = tracker.get_slot("attribute")
    if (not(attribute is None)):
        value = tracker.get_slot("ORG")
        object_type = "ORGANIZATION"
        answer = DbCall.searchForEntityRelationship(value, object_type)
        checked = "No"
        for x in answer["entites-relationships"]:
            if (x["rel"] == attribute):
                checked = "Yes"
        dispatcher.utter_message(text=f""+checked)