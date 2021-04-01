from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

class InitialExplainedEntititesAction(Action):

  def name(self) -> Text:
      return "action_initial_explained_entitites"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      return [SlotSet(Constants.slot_explained_add_entity, False), SlotSet(Constants.slot_explained_add_person, False), SlotSet(Constants.slot_semantic_search_result, False),
              SlotSet(Constants.slot_shall_explain_add_entity, False), SlotSet(Constants.slot_shall_explain_add_person, False)]