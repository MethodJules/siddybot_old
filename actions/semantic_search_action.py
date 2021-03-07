from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from typing import Any, Text, Dict, List
from actions.semantic_search import SemanticSearch
from actions.constants import Constants

class SemanticSearchAction(Action):

  def name(self) -> Text:
      return "action_semantic_search"

  def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("action_semantic_search")
    entities = tracker.latest_message[Constants.entities]
    print(entities)
    successfull = SemanticSearch.searchSemanticSearchListOfEntities(dispatcher, entities, tracker)
    print(successfull)
    if ((successfull is None) | (successfull == False)):
        dispatcher.utter_message(template="utter_ask_rephrase")
 #   intent = tracker.latest_message["text"]
 #   SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)