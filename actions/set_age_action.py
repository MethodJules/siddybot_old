from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

class SetAgeAction(Action):

  def name(self) -> Text:
      return "action_set_age"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      age = tracker.get_slot(Constants.slot_cardinal)
      print(age)
      return [SlotSet(Constants.slot_age, age), SlotSet(Constants.slot_cardinal)]