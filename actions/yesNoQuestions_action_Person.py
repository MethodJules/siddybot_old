from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.db_call import DbCall
#import base64,cv2

class YesNoQuestionsPersonAction(Action):

  def name(self) -> Text:
      return "action_yes_no_questions_person"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_yes_no_questions")
    person = tracker.get_slot("PERSON")
    object_type = "PERSON"
    person_exist = DbCall.validationPerson(person)
    intent = tracker.latest_message(text)
    attribute = tracker.get_slot("attribute")
    if (person_exist == "false"):
      if (attribute is None):
        SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
      else:
        SemanticSearch.searchSemanticSearchAttribute(dispatcher, person, attribute)
      return
    if (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_attributes"):
      if (not(attribute is None)):
        answer = DbCall.searchForEntityRelationship(person, object_type)
        checked = "No"
        for x in answer["entites-relationships"]:
            if (x["rel"] == attribute):
                checked = "Yes"
                break
        dispatcher.utter_message(text=f""+checked)
      else:
        SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_GPE"):
        value_gpe = tracker.get_slot("GPE")
        answer = DbCall.searchForEntityRelationship(person, object_type)
        checked = "No"
        for x in answer["entites-relationships"]:
            if (x["ent2_text"] == value_gpe):
                checked = "Yes"
                break
        dispatcher.utter_message(text=f""+checked)
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_ORG"):
        value_org = tracker.get_slot("ORG")
        answer = DbCall.searchForEntityRelationship(person, object_type)
        checked = "No"
        for x in answer["entites-relationships"]:
            if (x["ent2_text"] == value_org):
                checked = "Yes"
                break
        dispatcher.utter_message(text=f""+checked)
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_RELIGION"):
        value_rel = tracker.get_slot("RELIGION")
        answer = DbCall.searchForEntityRelationship(person, object_type)
        checked = "No"
        for x in answer["entites-relationships"]:
            if (x["ent2_text"] == value_rel):
                checked = "Yes"
                break
        dispatcher.utter_message(text=f""+checked)