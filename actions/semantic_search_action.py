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
          dispatcher.utter_message(text=f"I have found these results for your question:")
          for y in result:
            dispatcher.utter_message(text=f"For " + y["node_title"] + " I found :")
            print(y)
            for x in y["sents"]:
              print(x)
              dispatcher.utter_message(text=f""+x)
            self.linkErstellen(self, dispatcher, y["node_title"])
        else: 
          dispatcher.utter_message(text=f"I'm sorry but I don't have a answer for your question.")
      else: 
        dispatcher.utter_message(text=f"I don't found something to this person.")

  def searchSemanticSearch(self, dispatcher, name, attribute):
    searchquery = '{"search_query":"'+name+' ' + attribute+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    self.semanticSearch(dispatcher, searchquery)

  def searchSemanticSearch(self, dispatcher, intent):
    print("searchSemanticSearch")
    searchquery = '{"search_query":"'+intent+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    self.semanticSearch(self, dispatcher, searchquery)

  def linkErstellen(self, dispatcher: CollectingDispatcher, node_titel):
    """
    In dieser Methode wird mit Hilfe des node_title der Link zu der Seite der Person erstellt
    """
    node_titel = self.deleteMarks(self, node_titel)
    node = node_titel.split()
    link = ""
    while len(node) > 1:
      link = link + node[0] + "-"
      node.remove(node[0])
    link = link + node[0]
    dispatcher.utter_message(text=f"For more informations you can look here:")
    dispatcher.utter_message(text=f"https://www.jigsaw-navi.net/de/content/"+link)

  def deleteMarks(self, word) -> str:
    word = word.replace(".","")
    word = word.replace(",","")
    word = word.replace("/","")
    return word