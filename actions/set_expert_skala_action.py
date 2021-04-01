from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

class SetExpertValueAction(Action):

  def name(self) -> Text:
      return "action_set_expert_value"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      expert_value = tracker.get_slot(Constants.slot_cardinal)
      print(expert_value)
      return [SlotSet(Constants.slot_expert_value, expert_value), SlotSet(Constants.slot_cardinal)]