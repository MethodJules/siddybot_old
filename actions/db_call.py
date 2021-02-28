from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json

#import base64,cv2

# Klasse mit allen Aufrufen zur Datenbank ueber Flask
class DbCall():

  app=Flask(__name__)
  @app.route("/get-entities", methods=['POST'])
  def searchForEntitiy(object_type) -> Dict[Text, Any]:
      """
      Verwendet Flask um alle Entitaeten der Datenbank zu ermitteln.
      """
      answer = requests.get('https://semanticsearch.x-navi.de/get-entities')
      answer = json.loads(answer.text,encoding="utf-8")
      answer = answer["result"]
      answer = answer["types"]
      return answer

  @app.route("/get-entities-relations-by-entity", methods=['POST'])
  def searchForEntityRelationship(name, object_type) -> Dict[Text, Any]:
      """
      Verwendet Flask um zu einer bestimmten Entitaet alle relationships zu ermitteln.
      name = Name der Entitaete (bei einer Person z.B. der Name von dieser
      object_type = passender Objekttyp des Objektes
      """
      query = '{"ent_text":"'+name+'","ent_ner":"'+object_type+'"}'
      search_request = json.loads(query, encoding="utf-8")
      answer = requests.post('https://semanticsearch.x-navi.de/get-entities-relations-by-entity',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      results = answer["result"]
      return results

  @app.route("/get-nodes-count", methods=['POST'])
  def searchNodeCount(object_type) -> Dict[Text, Any]:
      """
      Verwendet Flask um die Anzahl der Knoten eines bestimmten Objekttyps zu ermitteln
      """
      query = '{"content_type":"'+object_type+'"}'
      search_request = json.loads(query, encoding="utf-8")
      answer = requests.post('https://semanticsearch.x-navi.de/get-nodes-count',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      results = answer["result"]
      return results

  @app.route("/semantic-search", methods=['POST'])
  def semanticSearch(searchquery) -> Dict[Text, Any]:
    """
    Verwendet Flask um eine semantische Suche durchzufuehren
    searchquery = Eingabe fuer die semantische Suche,
                  sollte folgenden Aufbaue haben: {"searchquery":" .... "}
    """
    print("Start der semantischen Suche in DB-CALL")
    answer = requests.post('https://semanticsearch.x-navi.de/semantic-search',searchquery)
    answer = json.loads(answer.text,encoding="utf-8")
    results = answer["result"]
    return results

  @app.route("/check-entity-exists", methods=['POST'])
  def validationPerson(name) -> bool:
    """
    Verwendet Flask um zu pruefen ob zu einem mitgegebenem Namen eine bestimmte Entitaet vorhanden ist.
    """
    entity = '{"entity":"'+name+'"}'
    entity_request = json.loads(entity, encoding="utf-8")
    answer = requests.post('https://semanticsearch.x-navi.de/check-entity-exists',entity_request)
    answer = json.loads(answer.text,encoding="utf-8")
    if (answer["result"] == "true"):
      return True
    return False

  @app.route("/get-nodes-by-filter", methods=['POST'])
  def findNote(dispatcher: CollectingDispatcher, name):
    """
    Verwendet Flask um einen Knoten ueber einen mitgegeben Filter zu ermitteln
    """
    searchquery = '{"filter":"'+name+'"}'
    search_request = json.loads(searchquery, encoding="utf-8")
    answer = requests.post('https://semanticsearch.x-navi.de/get-nodes-by-filter', search_request)
    print(answer.text)


