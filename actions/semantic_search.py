from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
#from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import types
from actions.db_call import DbCall
from actions.general_methods import GeneralMethods
from actions.constants import Constants
from actions.search_return import Search_return

#import base64,cv2

# Funktionen zum Aufruf der semantischen Ausgabe. Hier werden die Daten dann auch ausgegeben
class SemanticSearch():

  def searchSemanticSearchAttribute(dispatcher: CollectingDispatcher, tracker: Tracker, name, attribute, object_type = None, checkForExplicitPerson=False) -> Search_return:
    """
    Fuehrt eine semantische Suche mit den Eingaben attribute und name des Objektes durch
    """
    searchquery = '{"search_query":"'+name+' ' + attribute+'"}'
    print(searchquery)
    searchquery = json.loads(searchquery, encoding="utf-8")
    return_search = Search_return.__init__(Search_return, False)
    try:
      result = DbCall.semanticSearch(searchquery)
      search_return = SemanticSearch.readSemanticSearchResult(dispatcher, tracker, result, name, object_type, checkForExplicitPerson)
      return return_search
    except: 
      dispatcher.utter_message(templeate="utter_ask_rephrase")
      return return_search

  def searchSemanticSearchIntent(dispatcher: CollectingDispatcher, tracker: Tracker, intent, object_type = None) -> Search_return:
    """
    Fuehrt eine semantische Suche mit der letzten Eingabe des Users durch
    """
    searchquery = '{"search_query":"'+intent+'"}'
    print(searchquery)
    searchquery = json.loads(searchquery, encoding="utf-8")
    return_search = Search_return.__init__(Search_return, False)
    try:
      result = DbCall.semanticSearch(searchquery)
      return_search = SemanticSearch.readSemanticSearchResult(dispatcher, tracker, result, None, object_type)
      print(return_search.successfull)
      print(return_search.events)
      return return_search
    except: 
      dispatcher.utter_message(templeate="utter_ask_rephrase")
      return return_search

  def searchSemanticSearchListOfEntities(dispatcher: CollectingDispatcher, entities, tracker: Tracker, checkForExplicitPerson=False) -> Search_return:
    """
    Fuehrt eine semantische Suche mit den gespeicherten Slots der letzten Eingabe durch
    """
    search_return = Search_return.__init__(Search_return, False)
    try:
      search = ""
      name = None
      object_type = None
      for x in entities:
        entity = tracker.get_slot[x["entity"]]
        if ((checkForExplicitPerson == True) & (x["entity"] == Constants.person)):
            object_type = Constants.person
            name = entity
        search = search + " " + entity
      searchquery = '{"search_query":"'+search+'"}'
      print(searchquery)
      searchquery = json.loads(searchquery, encoding="utf-8")
      call_successful = False
      result = DbCall.semanticSearch(searchquery)
      search_return = SemanticSearch.readSemanticSearchResult(dispatcher, tracker, result, name, object_type, checkForExplicitPerson)
      return search_return
    except: 
      dispatcher.utter_message(templeate="utter_ask_rephrase")
      return search_return

  def readSemanticSearchResult(dispatcher: CollectingDispatcher, tracker: Tracker, result, name= None, object_type = None, checkForExplicitPerson=False) -> Search_return:
    """
    Verarbeitung und Ausgabe des Ergebnisses der semantischen Suche 
    """
    print("Ausgabe semantische Suche")
    print(result)
    print(name)
    max_results = 10
    return_search = Search_return.__init__(Search_return, False)
    print(len(result))
    if (len(result) > 0):
      node_equal_name = None
      print(name)
      print(object_type)
      if ((checkForExplicitPerson == True) & (object_type == Constants.person) & (not(name is None))):
        for y in result:
          node_equal_name = GeneralMethods.findeRichtigenKnoten(name, y[Constants.node_title])
          print(node_equal_name)
          if (node_equal_name == True):
            dispatcher.utter_message(text=f"I have found these results for your question:")
            Search_return.set_events(return_search, SemanticSearch.ausgabeNode(dispatcher, tracker, y))
            Search_return.set_successfull(return_search, True)
      else:
        print("Hier sollte dann was ausgegeben werden")
        for y in result:
          if (max_results == 0):
            dispatcher.utter_message(text=f"...")
            dispatcher.utter_message(text=f"I found some more results. If you don't find the right information here, please use the search at the website.")
            Search_return.set_successfull(return_search, True)
          max_results = max_results - 1
          dispatcher.utter_message(text=f"I have found these results for your question:")
          print(y)
          Search_return.set_events(return_search, SemanticSearch.ausgabeNode(dispatcher, tracker, y))
          print(return_search.events)
        Search_return.set_successfull(return_search, True)
    print(return_search.events)
    print(return_search.successfull)
    return return_search
 
  def ausgabeNode(dispatcher:CollectingDispatcher, tracker: Tracker, node_result) -> List[EventType]:
    dispatcher.utter_message(text=f"For " + node_result[Constants.node_title] + " I found:")
    if (isinstance(node_result[Constants.sents], List)):
      for x in node_result[Constants.sents]:
        dispatcher.utter_message(text=f""+x)
    else:
      dispatcher.utter_message(text=f""+node_result[Constants.sents])
    link = GeneralMethods.linkErstellen(dispatcher, node_result[Constants.node_title])
    print(link)
    result = GeneralMethods.linkAusgeben(dispatcher, tracker, link)
    print(result)
    return result

      
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

