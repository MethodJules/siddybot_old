from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
import requests
import json
import types
from actions.db_call import DbCall
from actions.general_methods import GeneralMethods
from actions.constants import Constants
from actions.search_return import Search_return

# Funktionen zum Aufruf der semantischen Ausgabe. Hier werden die Daten dann auch ausgegeben
class SemanticSearch():

  def searchSemanticSearchAttribute(dispatcher: CollectingDispatcher, tracker: Tracker, name, attribute, object_type = None, checkForExplicitPerson=False) -> Search_return:
    """
    Fuehrt eine semantische Suche mit den Eingaben attribute und name des Objektes durch

    dispatcher = Dispatcher
    tracker = Tracker
    name = Name des gesuchten Objektes
    attribut = Name des gesuchten Attributes
    objekt_type = Typ des gesuchten Objektes
    checkForExplicitPerson = Boolean ob die Rueckgabe speziell zu einer Person sein soll
    """
    # Aufbau der Suchanfrage
    searchquery = '{"search_query":"'+name+' ' + attribute+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    return_search = Search_return.__init__(Search_return, False)
    try:
      # Aufruf der Funktion zu semantischen Suche
      result = DbCall.semanticSearch(searchquery)
      # Ausgabe der Ergebnisse der semantischen Suche
      search_return = SemanticSearch.readSemanticSearchResult(dispatcher, tracker, result, name, object_type, checkForExplicitPerson)
      return return_search
    except: 
      # Wenn aus einem Grund die Suche abgebrochen ist, dann wird der Anwender darum gebeten die Frage nochmal neu zu formulieren
      dispatcher.utter_message(templeate="utter_ask_rephrase")
      return return_search

  def searchSemanticSearchIntent(dispatcher: CollectingDispatcher, tracker: Tracker, intent, object_type = None) -> Search_return:
    """
    Fuehrt eine semantische Suche mit der letzten Eingabe des Users durch

    dispatcher = Dispatcher
    tracker = Tracker
    intent = Eingabe des Anwenders
    objekt_type = Typ des gesuchten Objektes
    """
    # Aufbau der Suchanfrage
    searchquery = '{"search_query":"'+intent+'"}'
    searchquery = json.loads(searchquery, encoding="utf-8")
    return_search = Search_return.__init__(Search_return, False)
    try:
      # Aufruf der Funktion zu semantischen Suche
      result = DbCall.semanticSearch(searchquery)
      # Ausgabe der Ergebnisse der semantischen Suche
      return_search = SemanticSearch.readSemanticSearchResult(dispatcher, tracker, result, None, object_type)
      return return_search
    except: 
      # Wenn aus einem Grund die Suche abgebrochen ist, dann wird der Anwender darum gebeten die Frage nochmal neu zu formulieren
      dispatcher.utter_message(templeate="utter_ask_rephrase")
      return return_search

  def searchSemanticSearchListOfEntities(dispatcher: CollectingDispatcher, entities, tracker: Tracker, checkForExplicitPerson=False) -> Search_return:
    """
    Fuehrt eine semantische Suche mit den gespeicherten Slots der letzten Eingabe durch

    dispatcher = Dispatcher
    entities = Entitaeten die in der Nachricht gefunden wurden
    tracker = Tracker
    checkForExplicitPerson = Boolean ob die Rueckgabe speziell zu einer Person sein soll
    """
    search_return = Search_return.__init__(Search_return, False)
    try:
      # Aufbau der Suchanfrage
      search = ""
      name = None
      object_type = None
      # Auslesen der benoetigten Daten fuer den Suchstring
      # und zusammensetzen der einzelnen Worte
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
      # Ausfuehren der semantischen Suche auf der Datenbank
      result = DbCall.semanticSearch(searchquery)
      # Ausgabe der gefundenen Daten
      search_return = SemanticSearch.readSemanticSearchResult(dispatcher, tracker, result, name, object_type, checkForExplicitPerson)
      return search_return
    except: 
      # Wenn aus einem Grund die Suche abgebrochen ist, dann wird der Anwender darum gebeten die Frage nochmal neu zu formulieren
      dispatcher.utter_message(templeate="utter_ask_rephrase")
      return search_return

  def readSemanticSearchResult(dispatcher: CollectingDispatcher, tracker: Tracker, result, name= None, object_type = None, checkForExplicitPerson=False) -> Search_return:
    """
    Verarbeitung und Ausgabe des Ergebnisses der semantischen Suche 

    dispatcher = Dispatcher
    tracker = Tracker
    result = Ergebnis der semantischen Suche
    name = Name des gewuenschten Objektes (wenn bekannt)
    object_type = Objekttyp des gewuenschten Objektes (wenn bekannt)
    checkForExplicitPerson = Boolean ob die Rueckgabe speziell zu einer Person sein soll
    """
    # Maximale Anzahl an Ergebnissen die ausgegeben werden sollen
    max_results = 10
    return_search = Search_return.__init__(Search_return, False)
    # Pruefung ob ein Ergebnis vorhanden war
    if (len(result) > 0):
      node_equal_name = None
      # Funktion wenn zu einer spezifischen Person Ergebnisse ausgegeben werden sollen
      if ((checkForExplicitPerson == True) & (object_type == Constants.person) & (not(name is None))):
        for y in result:
          # Prueft ob der gefundene Knoten zu dem Namen des gewuenschten Objektes passt
          node_equal_name = GeneralMethods.findeRichtigenKnoten(name, y[Constants.node_title])
          # Wenn der Knoten dem Namen enspricht, dann werden die Daten dazu ausgegeben
          if (node_equal_name == True):
            dispatcher.utter_message(text=f"I have found these results for your question:")
            Search_return.set_events(return_search, SemanticSearch.ausgabeNode(dispatcher, tracker, y))
            Search_return.set_successfull(return_search, True)
      else:
        for y in result:
          # Wenn Bereits 10 Ergebnisse ausgegeben werden, dann wird die Schleife unterbrochen und ausgegeben, dass noch mehr Ergebnisse vorhanden sind
          # aber der Anwender die semantische die Suche der Webseite nutzen soll
          if (max_results == 0):
            dispatcher.utter_message(text=f"...")
            dispatcher.utter_message(text=f"I found some more results. If you don't find the right information here, please use the search at the website.")
            break
          max_results = max_results - 1
          # Ausgabe der der gefundenen Daten und setzen des Slots, dass die Daten aus der semantischen Suche stammen, damit dementsprechend die Frage 
          # gestellt werden kann, ob die Ergebnisse hilfreich waren
          Search_return.set_events(return_search, SemanticSearch.ausgabeNode(dispatcher, tracker, y) + [SlotSet(Constants.slot_semantic_search_result, True)])
        Search_return.set_successfull(return_search, True)
    else: 
        Search_return.set_events(return_search, [SlotSet(Constants.slot_semantic_search_result, False)])
    return return_search
 
  def ausgabeNode(dispatcher:CollectingDispatcher, tracker: Tracker, node_result) -> List[EventType]:
    """
    Gibt die Ergebnisse zu einem gefundenem Knoten aus

    dispatcher = Dispatcher
    tracker = tracker
    node_result = Ergebnisse zu einem Knoten
    """
    dispatcher.utter_message(text=f"For " + node_result[Constants.node_title] + " I found:")
    # Ausgabe der Ergebnisse:
    for x in node_result[Constants.sents]:
      dispatcher.utter_message(text=f""+x)
    # Erstellen des Links zu der Seite der Person um mehr Informationen lesen zu koennen
    link = GeneralMethods.linkErstellen(dispatcher, node_result[Constants.node_title])
    result = GeneralMethods.linkAusgeben(dispatcher, tracker, link)
    return result
  
  def returnPersonNotExist(dispatcher: CollectingDispatcher, tracker: Tracker) -> List[EventType]:
    """
    Funktion zum Umgang mit Personen die nicht in der Graphdatenbank gefunden werden konnten
    Es wird immer eine semantische Suche durchgefuehrt um die Daten zu der Person noch in den 
    gespeicherten Steckbriefen zu finden

    dispatcher = Dispatcher
    tracker = Tracker
    """
    call_successfull = False
    if (tracker.get_slot(Constants.slot_attribute) is None):
      # Wenn kein Attribut gefunden werden konnte, dann werden alle 
      # gefundenen Entitaeten ausgelesen und damit eine semantische Suche durchgefuehrt
      entities = tracker.latest_message["entities"]
      call_successfull = SemanticSearch.searchSemanticSearchListOfEntities(dispatcher, entities, tracker)
    else:
      # konnte ein Attribut gefunden werden, dann wird mit dem Attribut und der Person eine semantische Suche durchgefuehrt
      call_successfull = SemanticSearch.searchSemanticSearchAttribute(dispatcher, tracker.get_slot(Constants.slot_person), tracker.get_slot(Constants.slot_attribute), Constants.person)
    # Wenn keine Daten ueber die semantische Suche gefunden werden konnten
    if (call_successfull == False):
      dispatcher.utter_message(template="utter_data_not_found")
    # Ausgabe, dass die Person nicht gefunden werden konnte 
    dispatcher.utter_message(template="utter_person_is_missing")
    # Ausgabe, dass erklaert werden sollte, wie eine Person angelegt wird
    if (tracker.get_slot(Constants.slot_explained_add_person) == True):
      return[SlotSet(Constants.slot_shall_explain_add_person, False)]
    else: 
      return[SlotSet(Constants.slot_shall_explain_add_person, True)]