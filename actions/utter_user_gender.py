from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType
#import base64,cv2

# Action zum setzen des Usernames
class UtterUserGenderAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_utter_user_gender"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
        if (tracker.get_slot("gender") == "female"):
            dispatcher.utter_message(template="utter_user_gender_is_female")
        elif (tracker.get_slot("gender") == "male"):
            dispatcher.utter_message(template="utter_user_gender_is_male")
        elif (tracker.get_slot("gender") == "divers"):
            dispatcher.utter_message(template="utter_user_gender_is_divers")
        else: 
            dispatcher.utter_message(template="utter_do_not_know_the_answer")