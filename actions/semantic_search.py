from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from actions.db_call import DbCall
from actions.general_methods import GeneralMethods
#import base64,cv2

# Funktionen zum Aufruf der semantischen Ausgabe. Hier werden die Daten dann auch ausgegeben
class SemanticSearch():

  def searchSemanticSearchAttribute(dispatcher: CollectingDispatcher, name, attribute):
    """
    Fuehrt eine semantische Suche mit den Eingaben attribute und name des Objektes durch
    """
    searchquery = '{"search_query":"'+name+' ' + attribute+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    result = DbCall.semanticSearch(searchquery)
    SemanticSearch.readSemanticSearchResult(dispatcher, result)

  def searchSemanticSearchIntent(dispatcher: CollectingDispatcher, intent):
    """
    Fuehrt eine semantische Suche mit der letzten Eingabe des Users durch
    """
    searchquery = '{"search_query":"'+intent+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    result = DbCall.semanticSearch(searchquery)
    SemanticSearch.readSemanticSearchResult(dispatcher, result)


  def readSemanticSearchResult(dispatcher: CollectingDispatcher, result):
    """
    Verarbeitung und Ausgabe des Ergebnisses der semantischen Suche 
    """
    if (len(result) > 0):
      dispatcher.utter_message(text=f"I have found these results for your question:")
      for y in result:
        dispatcher.utter_message(text=f"For " + y["node_title"] + " I found :")
        print(y["node_title"])
        print(y["sents"])
        for x in y["sents"]:
          dispatcher.utter_message(text=f""+x)
        GeneralMethods.linkErstellen(dispatcher, y["node_title"])
    else: 
      dispatcher.utter_message(text=f"I'm sorry but I don't have a answer for your question. Maybe the mistake is that the entity is missing.")
      dispatcher.utter_message(text=f"Shall I tell you how to create the entity?")