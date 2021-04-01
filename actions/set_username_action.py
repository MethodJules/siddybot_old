from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

class SetUsernameAction(Action):

  def name(self) -> Text:
      return "action_set_username"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      username = tracker.get_slot(Constants.slot_person)
      print(username)
      return [SlotSet(Constants.slot_username, username), SlotSet(Constants.slot_person)]