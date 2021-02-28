from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.general_methods import GeneralMethods
from actions.db_call import DbCall
#import base64,cv2

class PersonDetailAction(Action):
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

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      print("action_person_detail")
      entity_person = None
      abfrage_attribute = None
      entity_person = tracker.get_slot('PERSON')
      abfrage_attribute = tracker.get_slot('attribute')
      print(entity_person)
      print(abfrage_attribute)
      if ( (entity_person is None) | (abfrage_attribute is None) | (not(abfrage_attribute in self.person_attributes))):
          intent = tracker.get_intent_of_latest_message()
          SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
          return
      personExist = DbCall.validationPerson(entity_person)
      if (personExist == True):
          print("Ja, die Person existiert")
          self.searchForEntity(dispatcher, tracker, entity_person, abfrage_attribute)
      else: 
          if (abfrage_attribute is None):
            intent = tracker.get_intent_of_latest_message()
            SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
          else:
            SemanticSearch.searchSemanticSearchAttribute(dispatcher, entity_person, abfrage_attribute)

      #TODO: Bevor die Methode genutzt werden kann, muss hier der richtige Node gefunden werden
      #GeneralMethods.linkErstellen(dispatcher, entity_person)

  def searchForEntity(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, attribute):
      answer = DbCall.searchForEntityRelationship(name, "PERSON")
      entities = answer["entities_relations"]
      return_ok = False
      if(attribute == "date_of_birth"):
          return_ok = self.utter_birthday(dispatcher, name, entities)
      elif(attribute == "birthplace"):
          return_ok = self.utter_birthplace(dispatcher, name, entities)
      elif(attribute == "city_of_birth"):
          return_ok = self.utter_city_of_birth(dispatcher, name, entities)
      elif(attribute == "country_of_birth"):
          return_ok = self.utter_country_of_birth(dispatcher, name, entities)
      elif(attribute == "country_of_death"):
          return_ok = self.utter_country_of_death(dispatcher, name, entities)
      elif(attribute == "city_of_death"):
          return_ok = self.utter_city_of_death(dispatcher, name, entities)
      elif(attribute == "death_place"):
          return_ok = self.utter_deathplace(dispatcher, name, entities)
      elif(attribute == "date_of_death"):
          return_ok = self.utter_deathday(dispatcher, name, entities)
      elif(attribute == "cause_of_death"):
          return_ok = self.utter_cause_of_death(dispatcher, name, entities)
      elif(attribute == "cities_of_residence"):
          return_ok = self.utter_cities_of_residence(dispatcher, name, entities)
      elif(attribute == "countries_of_residence"):
          return_ok = self.utter_countries_of_residence(dispatcher, name, entities)
      elif(attribute == "residences"):
          return_ok = self.utter_residence(dispatcher, name, entities)
      elif(attribute == "siblings"):
          return_ok = self.utter_siblings(dispatcher, name, entities)
      elif(attribute == "children"):
          return_ok = self.utter_children(dispatcher, name, entities)
      elif(attribute == "spouse"):
          return_ok = self.utter_spouse(dispatcher, name, entities)
      elif(attribute == "other_family"):
          return_ok = self.utter_other_family(dispatcher, name, entities)
      elif(attribute == "parents"):
          return_ok = self.utter_parents(dispatcher, name, entities)
      elif(attribute == "family"):
          return_ok = self.utter_family(dispatcher, name, entities)
      elif(attribute == "title"):
          return_ok = self.utter_title(dispatcher, name, entities)
      elif(attribute == "origin"):
          return_ok = self.utter_origin(dispatcher, name, entities)
      elif(attribute == "member"):
          return_ok = self.utter_member(dispatcher, name, entities)
      elif(attribute == "employee_or_member_of"):
          return_ok = self.utter_members_employees(dispatcher, name, entities)
      elif(attribute == "top_members_employees"):
          return_ok = self.utter_top_member(dispatcher, name, entities)
      elif(attribute == "alternate_name"):
          return_ok = self.utter_alternate_name(dispatcher, name, entities)
      elif(attribute == "schools_attended"):
          return_ok = self.utter_schools_attended(dispatcher, name, entities)
      else: 
        for x in entities:
          if(x["rel"] == attribute):
            dispatcher.utter_message(text=f""+x["ent2_text"])
        return_ok =  True
      print(return_ok)
      if (return_ok == False):
          if (attribute is None):
            intent = tracker.get_intent_of_latest_message()
            SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
          else:
            SemanticSearch.searchSemanticSearchAttribute(dispatcher, entity_person, abfrage_attribute)

      #self.findNote(dispatcher, name)

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

  def utter_birthplace(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      print("utter_birthplace")
      checked = False
      country = None
      city = None
      for x in entities:
          if(x["rel"] == "city_of_birth"):
              city = x["ent2_text"]
              print(city)
              checked = True
          elif (x["rel"] == "country_of_birth"):
              country = x["ent2_text"]
              print(country)
              checked = True
      if checked == True:
          if ((not(city is None)) & (not(country is None))):
              dispatcher.utter_message(text=f""+city + "("+country+")")
          elif (not(country is None)):
              dispatcher.utter_message(text=f""+country)
          elif (not(city is None)):
              dispatcher.utter_message(text=f""+city)
      return checked

  def utter_city_of_birth(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "city_of_birth"):
              city = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " was born in " + city)
              break
      return checked

  def utter_country_of_birth(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "country_of_birth"):
              country = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " was born in " + country)
              break
      return checked

  def utter_country_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "country_of_death"):
              country = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " died in " + country)
              break
      return checked
          
  def utter_city_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if(x["rel"] == "city_of_death"):
              country = x["ent2_text"]
              checked = True
              dispatcher.utter_message(text=f""+ entityPerson + " died in " + country)
              break
      return checked

  def utter_deathplace(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
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

  def utter_deathday(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "date_of_death"):
          dispatcher.utter_message(text=f"The date of death were on the "+x["ent2_text"])
          checked = True
          break
    return checked

  def utter_cause_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "cause_of_death"):
          dispatcher.utter_message(text=f""+name+" died because of "+x["ent2_text"])
          checked = True
          break
    return checked

  def utter_cities_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    cities = []
    for x in entities:
        if(x["rel"] == "cities_of_residence"):
          cities.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(cities))
    return checked

  def utter_countries_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    countries = []
    for x in entities:
        if(x["rel"] == "countries_of_residence"):
          countries.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(countries))
    return checked

  def utter_stateorprovince_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    stateorprovince = []
    for x in entities:
        if(x["rel"] == "stateorprovince_of_residence"):
          stateorprovince.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(stateorprovince))
    return checked

  def utter_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    residences = []
    for x in entities:
        if(x["rel"] in self.residence):
          residences.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(residences))
    return checked
      
  def utter_family(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
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
            dispatcher.utter_message(text=f"Parents: " + GeneralMethods.liste_ausgeben(parents))
        elif (len(siblings) > 0) :
            dispatcher.utter_message(text=f"Siblings: " + GeneralMethods.liste_ausgeben(siblings))
        elif (len(spouses) > 0) :
            dispatcher.utter_message(text=f"Spouse: " + GeneralMethods.liste_ausgeben(spouses))
        elif (len(children) > 0) :
            if (len(children)  == 1):
              dispatcher.utter_message(text=f"Child: " + GeneralMethods.liste_ausgeben(children))
            else: 
              dispatcher.utter_message(text=f"Children: " + GeneralMethods.liste_ausgeben(children))
        elif (len(other_family) > 0) :
            dispatcher.utter_message(text=f"Other family members: " + GeneralMethods.liste_ausgeben(other_family))
    return checked

  def utter_parents(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    parents = []
    for x in entities:
        if(x["rel"] == "parents"):
          parents.append(x["ent2_text"])
          checked = True
    if (checked == True):
      if (len(parents) == 1):
        dispatcher.utter_message(text=f"" + parents[0] + " was a parent of " + name)
      else: 
        dispatcher.utter_message(text=f"The parents of "+ name + " were: " + GeneralMethods.liste_ausgeben(children))

  def utter_children(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    children = []
    for x in entities:
        if(x["rel"] == "children"):
          children.append(x["ent2_text"])
          checked = True
    if (checked == True):
      if (len(children == 1)):
        dispatcher.utter_message(text=f""+ name + " had one child named " + GeneralMethods.liste_ausgeben(children))
      else: 
        dispatcher.utter_message(text=f"The children of "+ name + " were: " + GeneralMethods.liste_ausgeben(children))
    return checked

  def utter_siblings(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    siblings = []
    for x in entities:
        if(x["rel"] == "siblings"):
          siblings.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Siblings: " + GeneralMethods.liste_ausgeben(siblings))
    return checked

  def utter_other_family(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    other = []
    for x in entities:
        if(x["rel"] == "other_family"):
          other.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Other familymembers: " + GeneralMethods.liste_ausgeben(other))
    return checked

  def utter_spouse(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    spouse = []
    for x in entities:
        if(x["rel"] == "spouse"):
          spouse.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Spouses: " + GeneralMethods.liste_ausgeben(spouse))
    return checked

  def utter_title(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    title = []
    for x in entities:
        if(x["rel"] == "title"):
          title.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Titles: " + GeneralMethods.liste_ausgeben(title))
    return checked

  def utter_alternate_name(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    alternate_names = []
    for x in entities:
        if(x["rel"] == "alternate_name"):
          alternate_names.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Alternative Names of "+name+": " + GeneralMethods.liste_ausgeben(alternate_names))
    return checked

  def utter_origin(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
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

  def utter_member(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    organizations = None
    for x in entities:
        if(x["rel"] in self.member):
          organizations = x["ent2_text"]
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f""+ name + " was a member of: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_top_member(self, dispatcher: CollectingDispatcher, name, entities, abfrage_attribute) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if(x["rel"] == "top_members_employees"):
          organizations.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was top member of: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_members_employees(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if(x["rel"] == "employee_or_member_of"):
          organizations.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was member of these organizations: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_schools_attended(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if(x["rel"] == "schools_attended"):
          organizations.append(x["ent2_text"])
          checked = True
    if (checked == True):
      if (len(organizations) > 1):
        dispatcher.utter_message(text=f""+name+ " visit " + organizations[0] + " as a student")
      else: 
        dispatcher.utter_message(text=f""+name+ " visit theses schools: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

