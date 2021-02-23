from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from typing import Any, Text, Dict, List

class SemanticSearchAction(Action):

  app=Flask(__name__)
  def name(self) -> Text:
      return "action_semantic_search"

  def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    #self.semanticSearch(dispatcher, name, attribute)
    dispatcher.utter_message(text=f"Hier soll die semantische Suche mit dem Satz der eingegeben wurde ausgefuehrt werden")
    intent = tracker.get_intent_of_latest_message()
    self.searchSemanticSearch(dispatcher, intent)

  @app.route("/semantic-search", methods=['POST'])
  def semanticSearch(self, dispatcher, searchquery):
      print("Start der semantischen Suche")
      answer = requests.post('https://semanticsearch.x-navi.de/semantic-search',searchquery)
      answer = json.loads(answer.text,encoding="utf-8")
      print(answer)
      if (answer["type"] == "success"):
        result = answer["result"]
        print(result)
        if (len(result) > 0):
          result = result[0]
          print(result)
          dispatcher.utter_message(text=f"I have found these results for your question:")
          for x in result["sents"]:
            dispatcher.utter_message(text=f""+x)
          self.linkErstellen(dispatcher, result["node_title"])
        else: 
          dispatcher.utter_message(text=f"I'm sorry but I don't have a answer for your question.")
      else: 
        dispatcher.utter_message(text=f"I don't found something to this person.")

  def searchSemanticSearch(self, dispatcher, name, attribute):
    searchquery = '{"search_query":"'+name+' ' + attribute+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    self.semanticSearch(self, dispatcher, searchquery)

  def searchSemanticSearch(self, dispatcher, intent):
    searchquery = '{"search_query":"'+intent+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    self.semanticSearch(self, dispatcher, searchquery)