from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

# Action zu Setzen des Slots fuer das Alter des Anwenders
class SetAgeAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_set_age"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      print("action_set_age")
      intent = tracker.get_intent_of_latest_message()
      if (intent == "younger_than_10"):
           return [SlotSet(Constants.slot_age, "younger than 10")]
      elif (intent == "between11_20"):
           return [SlotSet(Constants.slot_age, "between 11 and 20")]
      elif (intent == "between21_30"):
           return [SlotSet(Constants.slot_age, "between 21 and 30")]
      elif (intent == "between31_40"):
           return [SlotSet(Constants.slot_age, "between 31 and 40")]
      elif (intent == "between41_50"):
           return [SlotSet(Constants.slot_age, "between 41 and 50")]
      elif (intent == "between51_60"):
           return [SlotSet(Constants.slot_age, "between 51 and 60")]
      elif (intent == "between61_70"):
           return [SlotSet(Constants.slot_age, "between 61 and 70")]
      elif (intent == "older_than_71"):
           return [SlotSet(Constants.slot_age, "older than 70")]