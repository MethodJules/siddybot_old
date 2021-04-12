from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json
from actions.constants import Constants

#import base64,cv2

# Klasse mit allen Aufrufen auf die Datenbank
class DbCall():

  def searchForEntitiy() -> Dict[Text, Any]:
      """
      Methode zur Ermittlung aller Entitaeten der Jigsaw-Webseite
      """
      # Abfrage der Daten in der Graphdatenbank
      answer = requests.get('https://semanticsearch.x-navi.de/get-entities')
      answer = json.loads(answer.text,encoding="utf-8")
      # Gibt fuer alle Objekttypen alle Entitaeten zurueck ohne weitere Filterung
      answer = answer[Constants.result]
      answer = answer[Constants.types]
      return answer

  def searchForEntityRelationship(name, object_type) -> Dict[Text, Any]:
      """
      Methode zur Ermittlung von allen relationships zu einer spezifischen Entitaet
      name = Name der Entitaete (bei einer Person z.B. der Name von dieser)
      object_type = passender Objekttyp des Objektes
      """
      # Aufbau des Suchstrings
      query = '{"ent_text":"'+name+'","ent_ner":"'+object_type+'"}'
      search_request = json.loads(query, encoding="utf-8")
      # Abfrage der Daten in der Graphdatenbank
      answer = requests.post('https://semanticsearch.x-navi.de/get-entities-relations-by-entity',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      # Rueckgabe aller gefundenen relationships ohne weitere Filterung
      results = answer[Constants.result]
      return results

  def searchNodeCount(object_type) -> Dict[Text, Any]:
      """
      Methode zur Ermittlung der Anzahl von Entitaeten eines bestimmten Objekttyps
      object_type = relevanter Objekttyp 
      """
      # Aufbau des Suchstrings
      query = '{"content_type":"'+object_type+'"}'
      search_request = json.loads(query, encoding="utf-8")
      # Abfrage der Daten in der Graphdatenbank
      answer = requests.post('https://semanticsearch.x-navi.de/get-nodes-count',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      # Rueckgabe der Anzahl des gewuenschten Objekttyps
      results = answer[Constants.result]
      return results

  def semanticSearch(searchquery) -> Dict[Text, Any]:
    """
    Verwendet Flask um eine semantische Suche durchzufuehren
    Da die Suchstrings immer unterschiedlich aussehen koennen, muessen diese bereits in den Methoden zusammengestellt werden
    searchquery = Eingabe fuer die semantische Suche,
                  sollte folgenden Aufbaue haben: {"searchquery":" .... "}
    """
    # Abfrage der Daten in der Graphdatenbank
    answer = requests.post('https://semanticsearch.x-navi.de/semantic-search',searchquery)
    answer = json.loads(answer.text,encoding="utf-8")
    # Rueckgabe aller gefundenen Ergebnisse
    results = answer[Constants.result]
    return results

  def validationPerson(name) -> bool:
    """
    Methode zur Ermittlung ob zu einem bestimmten Name eine Entitaet vorhanden ist
    name = name des relevanten Objektes
    """
    # Aufbau des Suchstrings
    if (name == None): 
        return False
    entity = '{"entity":"'+name+'"}'
    entity_request = json.loads(entity, encoding="utf-8")
    # Abfrage der Daten in der Graphdatenbank
    answer = requests.post('https://semanticsearch.x-navi.de/check-entity-exists',entity_request)
    answer = json.loads(answer.text,encoding="utf-8")
    # Rueckgabe ob die Person vorhanden ist oder nicht mit True oder False
    if (answer["result"] == "true"):
      return True
    return False

  def searchForEntitesFromTheNode(nodeID) -> Dict[Text, Any]:
      """
      Methode mit der zu einem konkreten Knoten alle Entitaeten ermittelt werden
      nodeID = ID des relevanten Knoten
      """
      # Aufbau des Suchstrings
      query= '{"node_id": "'+nodeID+'"}'
      search_request = json.loads(query, encoding="utf-8")
      # Abfrage der Daten in der Graphdatenbank
      answer = requests.post('https://semanticsearch.x-navi.de/get-entities-by-id', search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      # Rueckgabe aller Ergebnisse die zu dem Knoten gefunden wurden
      results = answer[Constants.result]
      return results
