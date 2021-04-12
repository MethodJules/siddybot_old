from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.db_call import DbCall
from actions.constants import Constants
#import base64,cv2

# Action fuer das Zaehlen der Objekte eines bestimmten Types
class CountObjectTypeAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_count_object_type"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    """
    Funktion die aufgerufen wird, wenn nach der Anzahl von bestimmten Knoten gefragt wird. 
    Ruft mit dem identifizierten Objekt-Typ die Methode searchNodeCount ueber die Klasse DbCall auf und gibt die dort ermittelte Anzahl zurueck
    Wenn kein Objekttyp identifiziert werden konnte, dann wird darum gebeten Objekttyp mit anzugeben
    """
    print("Start action_count_object_type")
    object_type = tracker.get_slot(Constants.slot_object_type)
    # Pruefung ob Objekttyp gefunden werden konnte und dieser ein relevanter der Webseite ist 
    if ((not(object_type is None)) & (object_type in Constants.object_types)):
      # Aufruf der Methode zum ermitteln der Anzahl eines Objekttyps
      answer = DbCall.searchNodeCount(object_type)
      # Ausgabe der Antwort
      count = answer[0]
      dispatcher.utter_message(text=f""+str(count[Constants.node_count]))
    else: 
      # Wenn kein Objekttyp gefunden werden konnte oder dieser nicht zu den relevanten der Webseite gehoert,
      # dann wird ausgegeben, dass die Aussage mit einem Objekttyp wiederholt werden soll
      dispatcher.utter_message(text=f"Please repeate your question with a objecttype of these website. Here are some examples:")
      dispatcher.utter_message(text=f"person, religion, organizations, ...")
