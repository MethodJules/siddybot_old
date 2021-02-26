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
  person_attributes = ["age", "alternate_name", "cause_of_death", "children", "cities_of_residence",
                       "city_of_birth", "city_of_death", "siblings", "countries_of_residence", "country_of_birth",
                       "country_of_death", "date_of_birth", "date_of_death", "employee_or_member_of", "spouse",
                       "founded_by", "origin", "other_family", "parents", "religion", "schools_attended", 
                       "stateorprovince_of_residence", "title", "top_members_employees", "birthplace", "residences",
                       "family", "member"]

  residence = ["stateorprovince_of_residence", "countries_of_residence", "cities_of_residence"]
  member = ["employee_or_member_of", "top_members_employees"]

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
      return_ok = False
      if(attribute == "date_of_birth"):
          return_ok = self.utter_birthday(dispatcher, name, entities, attribute)
      elif(attribute == "birth_place"):
          return_ok = self.utter_birthplace(dispatcher, name, entities, name, attribute)
      elif(attribute == "city_of_birth"):
          return_ok = self.utter_city_of_birth(dispatcher, name, entitites, attribute)
      elif(attribute == "country_of_birth"):
          return_ok = self.utter_country_of_birth(dispatcher, name, entitites, attribute)
      elif(attribute == "country_of_death"):
          return_ok = self.utter_country_of_death(dispatcher, name, entitites, attribute)
      elif(attribute == "city_of_death"):
          return_ok = self.utter_city_of_death(dispatcher, name, entitites, attribute)
      elif(attribute == "death_place"):
          return_ok = self.utter_deathplace(dispatcher, name, entitites, attribute)
      elif(attribute == "date_of_death"):
          return_ok = self.utter_deathday(dispatcher, name, entitites, attribute)
      elif(attribute == "cause_of_death"):
          return_ok == self.utter_cause_of_death(dispatcher, name, entitites, attribute)
      elif(attribute == "cities_of_residence"):
          return_ok == self.utter_cities_of_residence(dispatcher, name, entitites, attribute)
      elif(attribute == "countries_of_residence"):
          return_ok == self.utter_countries_of_residence(dispatcher, name, entitites, attribute)
      elif(attribute == "residence"):
          return_ok == self.utter_residence(dispatcher, name, entitites, attribute)
      elif(attribute == "siblings"):
          return_ok == self.utter_siblings(dispatcher, name, entitites, attribute)
      elif(attribute == "children"):
          return_ok == self.utter_children(dispatcher, name, entitites, attribute)
      elif(attribute == "spouse"):
          return_ok == self.utter_spouse(dispatcher, name, entitites, attribute)
      elif(attribute == "other_family"):
          return_ok == self.utter_other_family(dispatcher, name, entitites, attribute)
      elif(attribute == "family"):
          return_ok == self.utter_family(dispatcher, name, entitites, attribute)
      elif(attribute == "family"):
          return_ok == self.utter_family(dispatcher, name, entitites, attribute)
      elif(attribute == "title"):
          return_ok == self.utter_title(dispatcher, name, entitites, attribute)
      elif(attribute == "origin"):
          return_ok == self.utter_origin(dispatcher, name, entitites, attribute)
      elif(attribute == "member"):
          return_ok == self.utter_member(dispatcher, name, entitites, attribute)
      elif(attribute == "employee_or_member_of"):
          return_ok == self.utter_members_employees(dispatcher, name, entitites, attribute)
      elif(attribute == "top_members_employees"):
          return_ok == self.utter_top_member(dispatcher, name, entitites, attribute)
      elif(attribute == "alternate_name"):
          return_ok == self.utter_alternate_name(dispatcher, name, entitites, attribute)
      elif(attribute == "schools_attended"):
          return_ok == self.utter_schools_attended(dispatcher, name, entitites, attribute)
      else: 
        for x in entities:
          if(x["rel"] == attribute):
            dispatcher.utter_message(text=f""+x["ent2_text"])
        return_ok =  True
      if (return_ok == False):
          SemanticSearchAction.searchSemanticSearch(SemanticSearchAction, dispatcher, name, attribute)
      self.findNote(dispatcher, name)

  @app.route("/get-nodes-by-filter", methods=['POST'])
  def findNote(self, dispatcher: CollectingDispatcher, name):
      searchquery = '{"filter":"'+name+'"}'
      search_request = json.loads(searchquery, encoding="utf-8")
      answer = requests.post('https://semanticsearch.x-navi.de/get-nodes-by-filter', search_request)
      print(answer.text)

  def searchForEntitesFromTheNode(self, nodeID):
      query1 = '{"node_id": "'+nodeID+'"}'
      search_request1 = json.loads(query1, encoding="utf-8")
      answer1 = requests.post('https://semanticsearch.x-navi.de/get-entities-by-id', search_request1)
      print(answer1.text)

  def utter_birthday(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "date_of_birth"):
          dispatcher.utter_message(text=f"The birthday were on the "+x["ent2_text"])
          checked = True
          break
    return checked

  def utter_birthplace(self, dispatcher: CollectingDispatcher, entities , entityPerson, abfrage_attribute) -> bool:
      checked = False
      country = None
      city = None
      for x in entities:
          if(x["rel"] == "city_of_birth"):
              city = x["ent2_text"]
              checked = True
          elif (x["rel"] == "country_of_birth"):
              country = x["ent2_text"]
              checked = True
      if checked == True:
          if ((not(city is None)) & (not(country is None))):
              dispatcher.utter_message(text=f""+city + "("+country+")")
          elif (not(country is None)):
              dispatcher.utter_message(text=f""+country)
          elif (not(city is None)):
              dispatcher.utter_message(text=f""+city)
      return checked

  def utter_city_of_birth(self, dispatcher: CollectingDispatcher, entities , entityPerson, abfrage_attribute) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "city_of_birth"):
              city = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " was born in " + city)
              break
      return checked

  def utter_country_of_birth(self, dispatcher: CollectingDispatcher, entities , entityPerson, abfrage_attribute) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "country_of_birth"):
              country = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " was born in " + country)
              break
      return checked

  def utter_country_of_death(self, dispatcher: CollectingDispatcher, entities , entityPerson, abfrage_attribute) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "country_of_death"):
              country = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " died in " + country)
              break
      return checked
          
  def utter_city_of_death(self, dispatcher: CollectingDispatcher, entities , entityPerson, abfrage_attribute) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "city_of_death"):
              country = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " died in " + country)
              break
      return checked

  def utter_deathplace(self, dispatcher: CollectingDispatcher, entities , entityPerson, abfrage_attribute) -> bool:
      checked = False
      country = None
      city = None
      for x in entities:
          if(x["rel"] == "city_of_death"):
              city = x["ent2_text"]
              checked = True
          elif (x["rel"] == "country_of_death"):
              country = x["ent2_text"]
              checked = True
      if checked == True:
          if ((not(city is None)) & (not(country is None))):
              dispatcher.utter_message(text=f""+city + "("+country+")")
          elif (not(country is None)):
              dispatcher.utter_message(text=f""+country)
          elif (not(city is None)):
              dispatcher.utter_message(text=f""+city)
      return checked

  def utter_deathday(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "date_of_death"):
          dispatcher.utter_message(text=f"The date of death were on the "+x["ent2_text"])
          checked = True
          break
    return checked

  def utter_cause_of_death(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "date_of_death"):
          dispatcher.utter_message(text=f""+name+" died because of "+x["ent2_text"])
          checked = True
          break
    return checked

  def utter_cities_of_residence(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    cities = []
    for x in entities:
        if(x["rel"] == "cities_of_residence"):
          cities.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:")
        for x in cities:
            dispatcher.utter_message(text=f"" + x)
    return checked

  def utter_countries_of_residence(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    countries = []
    for x in entities:
        if(x["rel"] == "countries_of_residence"):
          countries.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:")
        for x in countries:
            dispatcher.utter_message(text=f"" + x)
    return checked

  def utter_stateorprovince_of_residence(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    stateorprovince = []
    for x in entities:
        if(x["rel"] == "stateorprovince_of_residence"):
          stateorprovince.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:")
        for x in stateorprovince:
            dispatcher.utter_message(text=f"" + x)
    return checked

  def utter_residence(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    residences = []
    for x in entities:
        if(x["rel"] in residence):
          residences.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:")
        for x in residences:
            dispatcher.utter_message(text=f"" + x)
    return checked
      
  def utter_family(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    parents = []
    siblings = []
    spouses = []
    children = []
    other_family = []
    for x in entities:
        if(x["rel"] == "spouse"):
          spouses.append(x["ent2_text"])
          checked = True
        elif(x["rel"] == "parents"):
          parents.append(x["ent2_text"])
          checked = True
        elif(x["rel"] == "siblings"):
          siblings.append(x["ent2_text"])
          checked = True
        elif(x["rel"] == "children"):
          children.append(x["ent2_text"])
          checked = True
        elif(x["rel"] == "other_family"):
          other_family.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f"I found these family members of" + name +":")
        if (len(partens) > 0):
            dispatcher.utter_message(text=f"Parents: " + parents)
        elif (len(siblings) > 0) :
            dispatcher.utter_message(text=f"Siblings: " + siblings)
        elif (len(spouses) > 0) :
            dispatcher.utter_message(text=f"Spouse: " + spouses)
        elif (len(children) > 0) :
            if (len(children == 1)):
              dispatcher.utter_message(text=f"Child: " + children)
            else: 
              dispatcher.utter_message(text=f"Children: " + children)
        elif (len(other_family) > 0) :
            dispatcher.utter_message(text=f"Other family members: " + other_family)
    return checked

  def utter_children(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    children = []
    for x in entities:
        if(x["rel"] == "children"):
          children.append(x["ent2_text"])
          checked = True
    if (checked == True):
      if (len(children == 1)):
        dispatcher.utter_message(text=f"Child: " + children)
      else: 
        dispatcher.utter_message(text=f"Children: " + children)
    return checked

  def utter_siblings(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    siblings = []
    for x in entities:
        if(x["rel"] == "siblings"):
          siblings.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Siblings: " + siblings)
    return checked

  def utter_other_family(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    other = []
    for x in entities:
        if(x["rel"] == "other_family"):
          other.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Siblings: " + other)
    return checked

  def utter_spouse(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    spouse = []
    for x in entities:
        if(x["rel"] == "spouse"):
          spouse.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Siblings: " + spouse)
    return checked

  def utter_title(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    title = []
    for x in entities:
        if(x["rel"] == "title"):
          title.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Titles: " + title)
    return checked

  def utter_alternate_name(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    alternate_names = []
    for x in entities:
        if(x["rel"] == "alternate_name"):
          alternate_names.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Alternative Names of "+name+": " + alternate_names)
    return checked

  def utter_origin(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    origin = None
    for x in entities:
        if(x["rel"] == "origin"):
          origin = x["ent2_text"]
          checked = True
          break
    if (not(origin is None)):
      dispatcher.utter_message(text=f""+ origin + " is the origin of "+name)
    return checked

  def utter_member(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if(x["rel"] in member):
          organizations.append(x["ent2_text"])
          checked = True
          break
    if (checked == True):
      dispatcher.utter_message(text=f""+ organizations + " is the origin of "+name)
    return checked

  def utter_top_member(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if(x["rel"] == "top_members_employees"):
          organizations.append(x["ent2_text"])
          checked = True
          break
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was top member of: " + organizations)
    return checked

  def utter_members_employees(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if(x["rel"] == "employee_or_member_of"):
          organizations.append(x["ent2_text"])
          checked = True
          break
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was member of these organizations: " + organizations)
    return checked

  def utter_schools_attended(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if(x["rel"] == "schools_attended"):
          organizations.append(x["ent2_text"])
          checked = True
          break
    if (checked == True):
      if (len(organizations) > 1):
        dispatcher.utter_message(text=f""+name+ " visit " + organizations + " as a student")
      else: 
        dispatcher.utter_message(text=f""+name+ " visit theses schools: " + organizations)
    return checked