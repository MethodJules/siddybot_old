from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import types
from actions.db_call import DbCall
from actions.general_methods import GeneralMethods
from actions.constants import Constants

#import base64,cv2

# Funktionen zum Aufruf der semantischen Ausgabe. Hier werden die Daten dann auch ausgegeben
class SemanticSearch():

  def searchSemanticSearchAttribute(dispatcher: CollectingDispatcher, name, attribute, object_type = None) -> bool:
    """
    Fuehrt eine semantische Suche mit den Eingaben attribute und name des Objektes durch
    """
    searchquery = '{"search_query":"'+name+' ' + attribute+'"}'
    print(searchquery)
    searchquery = json.loads(searchquery, encoding="utf-8")
    try:
      result = DbCall.semanticSearch(searchquery)
      call_successful = SemanticSearch.readSemanticSearchResult(dispatcher, result, name)
      return call_successful
    except: 
      dispatcher.utter_message(templeate="utter_ask_rephrase")

  def searchSemanticSearchIntent(dispatcher: CollectingDispatcher, intent, object_type = None)  -> bool:
    """
    Fuehrt eine semantische Suche mit der letzten Eingabe des Users durch
    """
    searchquery = '{"search_query":"'+intent+'"}'
    print(searchquery)
    searchquery = json.loads(searchquery, encoding="utf-8")
    call_successful = False
    try:
      result = DbCall.semanticSearch(searchquery)
      call_successful = SemanticSearch.readSemanticSearchResult(dispatcher, result)
      return call_successful
    except: 
      dispatcher.utter_message(templeate="utter_ask_rephrase")

  def searchSemanticSearchListOfEntities(dispatcher: CollectingDispatcher, entities, tracker: Tracker)  -> bool:
    """
    Fuehrt eine semantische Suche mit den gespeicherten Slots der letzten Eingabe durch
    """
    try:
      search = ""
      for x in entities:
        entity = tracker.get_slot[x]
        search = search + " " + x
      searchquery = '{"search_query":"'+search+'"}'
      print(searchquery)
      searchquery = json.loads(searchquery, encoding="utf-8")
      call_successful = False
      result = DbCall.semanticSearch(searchquery)
      call_successful = SemanticSearch.readSemanticSearchResult(dispatcher, result)
      return call_successful
    except: 
      dispatcher.utter_message(templeate="utter_ask_rephrase")

  def readSemanticSearchResult(dispatcher: CollectingDispatcher, result, name= None, object_type = None) -> bool:
    """
    Verarbeitung und Ausgabe des Ergebnisses der semantischen Suche 
    """
    print(result)
    print(name)
    max_results = 15
    if (len(result) > 0):
      node_equal_name = None
      for y in result:
        if (max_results == 0):
          dispatcher.utter_message(text=f"...")
          dispatcher.utter_message(text=f"I found some more results. If you don't find the right information here, please use the search at the website.")
          return True
        max_results = max_results - 1
        if ((object_type == Constants.person) & (not(name is None))):
            node_equal_name = GeneralMethods.findeRichtigenKnoten(name, y[Constants.node_title])
            if (node_equal_name == True):
              dispatcher.utter_message(text=f"I have found these results for your question:")
              SemanticSearch.ausgabeNode(dispatcher, y)
              return True
        else:
          dispatcher.utter_message(text=f"I have found these results for your question:")
          for y in result:
            print(y)
            SemanticSearch.ausgabeNode(dispatcher, y)
          return True
    else: 
      return False
 
  def ausgabeNode(dispatcher:CollectingDispatcher, node_result):
    dispatcher.utter_message(text=f"For " + node_result[Constants.node_title] + " I found:")
    if (isinstance(node_result[Constants.sents], List)):
      for x in node_result[Constants.sents]:
        dispatcher.utter_message(text=f""+x)
    else:
      dispatcher.utter_message(text=f""+node_result[Constants.sents])
    link = GeneralMethods.linkErstellen(dispatcher, node_result[Constants.node_title])
    dispatcher.utter_message(text=f"For more informations you can look here:")
    dispatcher.utter_message(text=f"https://www.jigsaw-navi.net/de/content/"+link)

      
  def returnPersonNotExist(dispatcher: CollectingDispatcher, tracker: Tracker) -> List[EventType]:
    call_successfull = False
    if (tracker.get_slot(Constants.slot_attribute) is None):
      entities = tracker.latest_message["entities"]
      call_successfull = SemanticSearch.searchSemanticSearchListOfEntities(entities, tracker)
    else:
      call_successfull = SemanticSearch.searchSemanticSearchAttribute(dispatcher, tracker.get_slot(Constants.slot_person), tracker.get_slot(Constants.slot_attribute), Constants.person)
    print(call_successfull)
    if (call_successfull == False):
      dispatcher.utter_message(template="utter_data_not_found")
    explained_add_person = tracker.get_slot(Constants.slot_explained_add_person) 
    if ((explained_add_person is None) | (explained_add_person  == False)):
      dispatcher.utter_message(template="utter_shall_explain_add_person")
    return[SlotSet(Constants.slot_shall_explain_add_person, True)]