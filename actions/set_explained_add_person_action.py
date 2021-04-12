from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
import json
from actions.db_call import DbCall
from actions.constants import Constants
#import base64,cv2

# Action zum setzen des Slots, dass erklaert wurde wie eine Person angelegt wird
class SetExplainedAddPersonAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_set_exlpained_add_person"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      """
      Methode setzt den Slots explained_add_person auf True
      """
      return [SlotSet(Constants.slot_explained_add_person, True)]