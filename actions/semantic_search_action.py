from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from typing import Any, Text, Dict, List
from actions.semantic_search import SemanticSearch
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType

class SemanticSearchAction(Action):

  def name(self) -> Text:
      return "action_semantic_search"

  def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[EventType]:
    print("action_semantic_search")
    entities = tracker.latest_message[Constants.entities]
    if ((entities == None) | (len(entities) == 0)):
       dispatcher.utter_message(template="utter_ask_rephrase")
    print(entities)
    search_return = SemanticSearch.searchSemanticSearchListOfEntities(dispatcher, entities, tracker)
    print(search_return.successfull)
    if ((search_return.successfull is None) | (search_return.successfull == False)):
        dispatcher.utter_message(template="utter_ask_rephrase")
    return search_return.events
 #   intent = tracker.latest_message["text"]
 #   SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)