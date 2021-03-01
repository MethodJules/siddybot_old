from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json
from actions.db_call import DbCall
#import base64,cv2

class SetExplainedAddPersonAction(Action):

  def name(self) -> Text:
      return "action_set_exlpained_add_person"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      return SlotSet("explained_add_person", True)