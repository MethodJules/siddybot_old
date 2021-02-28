from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from typing import Any, Text, Dict, List
from actions.semantic_search import SemanticSearch

class SemanticSearchAction(Action):

  def name(self) -> Text:
      return "action_semantic_search"

  def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    #self.semanticSearch(dispatcher, name, attribute)
    dispatcher.utter_message(text=f"Hier soll die semantische Suche mit dem Satz der eingegeben wurde ausgefuehrt werden")
    intent = tracker.latest_message["text"]
    SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)