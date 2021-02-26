from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from actions.semantic_search_action import SemanticSearchAction
#import base64,cv2

class PersonDetailAction(Action):
  app=Flask(__name__)
  def name(self) -> Text:
      return "action_person_detail"

  @app.route("/check-entity-exists", methods=['POST'])
  def validationPerson(self, name) -> bool:
    print("Start Validation")
    entity = '{"entity":"'+name+'"}'
    entity_request = json.loads(entity, encoding="utf-8")
    answer = requests.post('https://semanticsearch.x-navi.de/check-entity-exists',entity_request)
    answer = json.loads(answer.text,encoding="utf-8")
    print(answer)
    return answer["result"]  

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      print("start der action")
      entity_person = None
      abfrage_attribute = None
      entity_person = tracker.get_slot('PERSON')
      #dispatcher.utter_message(text=f"Abfrage zu "+ entity_person)
      abfrage_attribute = tracker.get_slot('attribute')
      #dispatcher.utter_message(text=f"Abzufragenes Attribute " + abfrage_attribute)
      if ( (entity_person is None) | (abfrage_attribute is None)):
          intent = tracker.get_intent_of_latest_message()
          SemanticSearchAction.searchSemanticSearchIntent(SemanticSearchAction, dispatcher, intent)
          return
      personExist = self.validationPerson(entity_person)
      print(personExist)
      if (personExist == "true"):
          print("Ja, die Person existiert")
          self.searchForEntity(dispatcher, entity_person, abfrage_attribute)
      else: 
          SemanticSearchAction.searchSemanticSearchAttribute(SemanticSearchAction, dispatcher, entity_person, abfrage_attribute)

      #TODO: Bevor die Methode genutzt werden kann, muss hier der richtige Node gefunden werden
      #self.linkErstellen(dispatcher, entity_person)

  @app.route("/get-entities-relations-by-entity", methods=['POST'])
  def searchForEntity(self, dispatcher: CollectingDispatcher, name, attribute):
      query = '{"ent_text":"'+name+'","ent_ner":"PERSON"}'
      search_request = json.loads(query, encoding="utf-8")
      answer = requests.post('https://semanticsearch.x-navi.de/get-entities-relations-by-entity',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      print(answer["result"])
      results = answer["result"]
      entities = results["entities_relations"]
      if(attribute == "date_of_birth"):
          self.utter_birthday(dispatcher, name, entities)
      elif(attribute == "birth_place"):
          utter_birthplace(dispatcher, name, entities, name, attribute)
      else: 
        for x in entities:
          if(x["rel"] == attribute):
            dispatcher.utter_message(text=f""+x["ent2_text"])
      self.findNote(dispatcher, name)

  @app.route("/get-nodes-by-filter", methods=['POST'])
  def findNote(self, dispatcher: CollectingDispatcher, name):
      searchquery = '{"filter":"'+name+'"}'
      search_request = json.loads(searchquery, encoding="utf-8")
      answer = requests.post('https://semanticsearch.x-navi.de/get-nodes-by-filter', search_request)
      print(answer.text)

  def searchForEntitesFromTheNode(self, nodeID):
      query1 = '{"node_id": "nodeID"}'
      search_request1 = json.loads(query1, encoding="utf-8")
      answer1 = requests.post('https://semanticsearch.x-navi.de/get-entities-by-id', search_request1)
      print(answer1.text)

  def utter_birthday(self, dispatcher: CollectingDispatcher, name, entities):
    checked = False
    for x in entities:
        if(x["rel"] == "date_of_birth"):
          dispatcher.utter_message(text=f"The birthday were on the "+x["ent2_text"])
          checked = True
          break
    if checked == False:
        SemanticSearchAction.searchSemanticSearch(SemanticSearchAction, dispatcher, name, "date_of_birth")
        #dispatcher.utter_message(text=f"I found these Dates to this person. Could you tell me if one of it is the birthday?")
        #for x in entities:
        #    if ent_ner ?

  def utter_birthplace(self, dispatcher: CollectingDispatcher, entities , entityPerson, abfrage_attribute):
      checked = False
      country = None
      city = None
      for x in entities:
          if(x["rel"] == "city_of_birth"):
              city = x["ent2_text"]
              checked = True
              dispatcher.utter_message(city)
          elif (x["rel"] == "country_of_birth"):
              country = x["ent2_text"]
              dispatcher.utter_message(country)
              checked = True
      if checked == False:
          SemanticSearchAction.searchSemanticSearchAttribute(SemanticSearchAction, dispatcher, entityPerson, abfrage_attribute)
      