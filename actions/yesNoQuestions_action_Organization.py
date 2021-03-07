from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.db_call import DbCall
from actions.general_methods import GeneralMethods
from actions.constants import Constants
#import base64,cv2

class YesNoQuestionsOrganizationAction(Action):

  def name(self) -> Text:
      return "action_yes_no_questions_organization"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_yes_no_questions_organization")
    intent = tracker.latest_message["text"]
    attribute = tracker.get_slot(Constants.slot_attribute)
    organization = tracker.get_slot(Constants.slot_org)
    checked_bool = False
    if (intent == "questionsYesNoOrganization_attributes") :
      if ((not(attribute is None))):
        answer = DbCall.searchForEntityRelationship(organization, Constants.organization)
        for x in answer[Constants.entities_relation]:
            if (x[Constants.relationship] == attribute):
                checked_bool = True
                break
      else:
        intent = tracker.latest_message["text"]
        SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
        return
    elif (intent == "questionsYesNoOrganization_connection_to_GPE"):
      value_gpe = tracker.get_slot[Constants.slot_place]
      if ((not(attribute is None))):
        checked_bool = GeneralMethods.checkAttributeAndEntity(organization, Constants.organization, attribute, value_gpe)
      else:
        checked_bool = GeneralMethods.checkEntity(organization, Constants.organization, value_gpe)
    elif (intent == "questionsYesNoOrganization_connection_to_RELIGION"):
      if ((not(attribute is None))):
        checked_bool = GeneralMethods.checkAttributeAndEntity(organization, Constants.organization, attribute, value_religion)
      else:
        checked_bool = GeneralMethods.checkEntity(organization, Constants.organization, value_religion)
    else: 
        dispatcher.utter_message(template="utter_ask_rephrase")
        return
    if (checked_bool == True):
      dispatcher.utter_message(text=f"Yes")
    else: 
      dispatcher.utter_message(text=f"No")




