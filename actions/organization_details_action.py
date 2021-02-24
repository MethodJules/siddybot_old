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

class OrganizationDetailsAction(Action):
  app=Flask(__name__)
  def name(self) -> Text:
      return "action_organization_details"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_organization_details")
    organization = tracker.get_slot("ORG")
    print(organization)
    attribute = tracker.get_slot("attribute")
    print(attribute)
    organization_attributes = ["city_of_headquarter","employee_or_member_of", "top_members_employee", "schools_attended" ]
    if ((attribute is None) | (not(attribute in organization_attributes))):
        print("Hier sollte die semantische Suche durchgefuert werden")
        intent = tracker.latest_message["text"]
        print(intent)
        SemanticSearchAction.searchSemanticSearch(SemanticSearchAction, dispatcher, intent)
    else:
        self.searchSepcificDetailsToOrganization(dispatcher, organization, attribute)

  def searchSepcificDetailsToOrganization(self, dispatcher: CollectingDispatcher, name, attribute):
      results = DbCall.searchForEntityRelationship(DbCall, name, "ORGANIZATION")
      entities = results["entities_relations"]
      if(attribute == "city_of_headquarter"):
          self.utter_city_of_headquarter(dispatcher, name, entities)
      elif(attribute == "employee_or_member_of"):
          self.utter_employee_or_member_of(dispatcher, name, entities, name, attribute)
      elif(attribute == "top_members_employee"):
          self.utter_top_members_employee(dispatcher, name, entities, name, attribute)
      else: 
        for x in entities:
          if(x["rel"] == attribute):
            dispatcher.utter_message(text=f""+x["ent2_text"])

  def utter_city_of_headquarter(self, dispatcher: CollectingDispatcher, name, entities):
    checked = False
    for x in entities:
        if(x["rel"] == "city_of_headquarter"):
          dispatcher.utter_message(text=f"The headquarter is in "+x["ent2_text"])
          checked = True
          break
    if checked == False:
        SemanticSearchAction.searchSemanticSearch(dispatcher, name, "city_of_headquarter")

  def utter_employee_or_member_of(self, dispatcher: CollectingDispatcher, name, entities):
    checked = False
    for x in entities:
        dispatcher.utter_message(text=f"These employees or members were by " + name)
        if(x["rel"] == "employee_or_member_of"):
          dispatcher.utter_message(text=f"T"+x["ent2_text"]) #TODO: hier noch die Aufzählund einbauen
          checked = True
          break
    if checked == False:
        SemanticSearchAction.searchSemanticSearch(dispatcher, name, "employee_or_member_of")

  def utter_top_members_employee(self, dispatcher: CollectingDispatcher, name, entities):
    checked = False
    for x in entities:
        dispatcher.utter_message(text=f"These top-members or -employees of " + name + " were:")
        if(x["rel"] == "top_members_employee"):
          dispatcher.utter_message(text=f""+x["ent2_text"]) #TODO: hier noch die Aufzählund einbauen
          checked = True
          break
    if checked == False:
        SemanticSearchAction.searchSemanticSearch(dispatcher, name, "top_members_employee")