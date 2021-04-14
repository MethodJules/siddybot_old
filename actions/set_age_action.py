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
      # Auslesen des Slots der Kardinalitaet
      age = tracker.get_slot(Constants.slot_cardinal)
      # Setzt den Wert des Alters in den passenden Slot 
      # der Wert des Slots fuer die Kardinalitaeten wird wieder auf None gesetzt
      return [SlotSet(Constants.slot_age, age), SlotSet(Constants.slot_cardinal)]