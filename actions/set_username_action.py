from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

# Action zum setzen des Usernames
class SetUsernameAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_set_username"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      """
      Methode damit aus dem Slot "Person" der Name ausgelesen wird
      """
      # Auslesen des Slots Person
      username = tracker.get_slot(Constants.slot_person)
      # Setzen des Slots username mit den Daten aus dem Slots Person
      # zuruecksetzen des Slots Person auf None  
      return [SlotSet(Constants.slot_username, username), SlotSet(Constants.slot_person)]