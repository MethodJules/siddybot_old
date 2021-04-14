from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

# Action zum Initalisieren von Entiaeten
class InitialExplainedEntititesAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_initial_explained_entitites"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      """
      Methode initialisiert die Werte der Slots mit False
      Die hier initalisierte Slots sind: 
      explained_add_entity
      explained_add_person
      semantic_search_result
      shall_explain_add_entity
      shall_explain_add_person
      """
      print("action_initial_explained_entitites")
      return [SlotSet(Constants.slot_explained_add_entity, False), SlotSet(Constants.slot_explained_add_person, False), SlotSet(Constants.slot_semantic_search_result, False),
              SlotSet(Constants.slot_shall_explain_add_entity, False), SlotSet(Constants.slot_shall_explain_add_person, False)]