from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

# Action zum setzen wie hoch ein Anwender sein Wissen ueber das Thema der Webseite einschaetzt
class SetExpertValueAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_set_expert_value"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      """
      Setzt den Slot fuer den Wert des Expertenwissens des Anwenders
      """
      print("action_set_expert_value")
      intent = tracker.get_intent_of_latest_message()
      if (intent == "expertlevel_1"):
           return [SlotSet(Constants.slot_expert_value, "1")]
      elif (intent == "expertlevel_2"):
           return [SlotSet(Constants.slot_expert_value, "2")]
      elif (intent == "expertlevel_3"):
           return [SlotSet(Constants.slot_expert_value, "3")]
      elif (intent == "expertlevel_4"):
           return [SlotSet(Constants.slot_expert_value, "4")]
      elif (intent == "expertlevel_5"):
           return [SlotSet(Constants.slot_expert_value, "5")]
      elif (intent == "expertlevel_6"):
           return [SlotSet(Constants.slot_expert_value, "6")]
      elif (intent == "expertlevel_7"):
           return [SlotSet(Constants.slot_expert_value, "7")]