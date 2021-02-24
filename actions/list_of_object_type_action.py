from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from actions.semantic_search_action import SemanticSearchAction
from actions.db_call import DbCall
#import base64,cv2

class ListOfObjecttype(Action):
  app=Flask(__name__)
  def name(self) -> Text:
      return "action_list_of"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_list_of")
    object_type = tracker.get_slot("object_type")
    attribute = tracker.get_slot("attribute")
    organization = tracker.get_slot("ORGANIZATION")
    self.searchOrganizations(dispatcher, tracker)

  def searchOrganizations(self, dispatcher: CollectingDispatcher, tracker: Tracker):
      """
      Sucht alle Organisationen die in dem System gespeichert sind.
      Wenn der Anwender in dem Intent eine Person, eine Stadt oder ein Land mitgibt, dann werden nur die Organisationen zurueck gegeben,
      die auf irgendeine Art und Weise mit der Person, der Stadt oder dem Land verbunden sind.
      """
      answer = DbCall.searchForEntitiy(DbCall, "ORGANIZATION")
      city = tracker.get_slot("CITY")
      country = tracker.get_slot("COUNTRY")
      person = tracker.get_slot("PERSON")
      gpe = tracker.get_slot("GPE")
      ausgabe_entities = []
      if ((not(city is None)) | (not(country is None)) | (not(person is None)) | (not(gpe is None))):
        for x in answer["ORGANIZATION"]:
          entities = DbCall.searchForEntityRelationship(DbCall, x, "ORGANIZATION")
          entities = entities["entities_relations"]
          for y in entities:
              if (y["ent_text"] == x):
                if ((not(city is None)) & (y["ent2_ner"] == "CITY") & (y["ent2_text"] == city)):
                  ausgabe_entities.append(x)
                elif ((not(country is None)) & (y["ent2_ner"] == "COUNTRY") & (y["ent2_text"] == country)):
                  ausgabe_entities.append(x)
                elif ((not(person is None)) & (y["ent2_ner"] == "PERSON") & (y["ent2_text"] == person)):
                  ausgabe_entities.append(x)
                elif ((not(person is None)) & ((y["ent2_ner"] == "COUNTRY")|(y["ent2_ner"] == "CITY")) & ((y["ent2_text"] == gpe)|(y["ent2_text"] == gpe))):
                  ausgabe_entities.append(x)
      else: 
          ausgabe_entities = answer["ORGANIZATION"]
      print(ausgabe_entities)
      for x in ausgabe_entities:
          dispatcher.utter_message(text=f""+x)

