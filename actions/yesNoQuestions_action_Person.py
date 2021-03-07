from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.db_call import DbCall
from actions.general_methods import GeneralMethods
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType
#import base64,cv2

class YesNoQuestionsPersonAction(Action):

  def name(self) -> Text:
      return "action_yes_no_questions_person"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
    print("start action_yes_no_questions")
    person = tracker.get_slot(Constants.slot_person)
    person_exist = DbCall.validationPerson(person)
    intent = tracker.get_intent_of_latest_message()
    attribute = tracker.get_slot("attribute")
    checked_bool = False
    if (person_exist == False):
      return SemanticSearch.returnPersonNotExist(dispatcher, tracker)
    if (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_attributes"):
      if ((not(attribute is None))):
        answer = DbCall.searchForEntityRelationship(person, Constants.person)
        checked = "No"
        for x in answer[Constants.entities_relation]:
            if (x[Constants.relationship] == attribute):
                checked_bool = True
                break
      else:
        SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker.latest_message["text"])
        return
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_GPE"):
        value_gpe = tracker.get_slot(Constants.slot_place)
        if ((not(attribute is None))):
          checked_bool = GeneralMethods.checkAttributeAndEntity(person,  Constants.person, attribute, value_gpe)
        else:
          checked_bool = GeneralMethods.checkEntity(person,  Constants.person, value_gpe)
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_ORG"):
        value_org = tracker.get_slot(Constants.slot_org)
        if ((not(attribute is None))):
          checked_bool = GeneralMethods.checkAttributeAndEntity(person,  Constants.person, attribute, value_org)
        else:
          checked_bool = GeneralMethods.checkEntity(person,  Constants.person, value_org)
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_RELIGION"):
        value_rel = tracker.get_slot(Constants.slot_religion)
        if ((not(attribute is None))):
          checked_bool = GeneralMethods.checkAttributeAndEntity(person,  Constants.person, attribute, value_rel)
        else:
          checked_bool = GeneralMethods.checkEntity(person,  Constants.person, value_rel)
    else: 
        dispatcher.utter_message(template="utter_ask_rephrase")
        return
    if (checked_bool == True):
      dispatcher.utter_message(text=f"Yes")
    else: 
      dispatcher.utter_message(text=f"No")