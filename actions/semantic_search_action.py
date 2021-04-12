from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from typing import Any, Text, Dict, List
from actions.semantic_search import SemanticSearch
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType

# Action zum durchfuehren der semantischen Suche wenn keine passende Aktion gefunden wurde
class SemanticSearchAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_semantic_search"

  def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[EventType]:
    print("action_semantic_search")
    # Ermittlung alle Entitaeten
    entities = tracker.latest_message[Constants.entities]
    # Pruefung ob Entitaeten gefunden werden konnten
    if ((entities == None) | (len(entities) == 0)):
       # Wenn keine Entitaeten gefunden werden konnten, dann wird 
       # der Anwender gebeten seine Frage umzuformulieren
       dispatcher.utter_message(template="utter_ask_rephrase")
       return
    # Wenn Entitaeten gefunden werden konnten, dann wird mit diesen eine semantische Suche durchgefuehrt
    search_return = SemanticSearch.searchSemanticSearchListOfEntities(dispatcher, entities, tracker)
    # Pruefung ob Daten ueber die semantische Suche ermittelt werden konnten
    if ((search_return.successfull is None) | (search_return.successfull == False)):
        # Wenn keine Daten ueber die semantische Suche ermittelt werden konnten, 
        # dann wird der Anwender darum gebeten die Frage neu zu formulieren
        dispatcher.utter_message(template="utter_ask_rephrase")
    # Rueckgabe aller Events die ueber die semantische Suche ermittelt werden konnten
    return search_return.events