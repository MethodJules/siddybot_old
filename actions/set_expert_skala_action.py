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
      # Liest den Slot der Kardinalitaet aus
      expert_value = tracker.get_slot(Constants.slot_cardinal)
      # Setzt den Wert des Expertenwissens in den passenden Slot 
      # der Wert des Slots fuer die Kardinalitaeten wird wieder auf None gesetzt
      return [SlotSet(Constants.slot_expert_value, expert_value), SlotSet(Constants.slot_cardinal)]