from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.db_call import DbCall
#import base64,cv2

class CountObjectTypeAction(Action):

  def name(self) -> Text:
      return "action_count_object_type"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    """
    Action die aufgerufen wird, wenn nach der Anzahl von bestimmten Knoten gefragt wird. 
    Ruft mit dem identifizierten Objekt-Typ die Methode searchNodeCount auf und gibt die dort ermittelte Anzahl zurück
    """
    object_type = tracker.get_slot("object_type")
    print(object_type)
    if (not(object_type is None)):
      answer = DbCall.searchNodeCount(object_type)
      count = answer[0]
      dispatcher.utter_message(text=f""+str(count["node_count"]))
    else: 
      dispatcher.utter_message(text=f"Please tell me which type of property would you like to have the number of. Here are some examples:")
      dispatcher.utter_message(text=f"City, Person, Religion, organizations, title...")
