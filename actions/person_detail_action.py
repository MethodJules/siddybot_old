from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.general_methods import GeneralMethods
from actions.db_call import DbCall
from actions.constants import Constants
from actions.search_return import Search_return
#import base64,cv2

class PersonDetailAction(Action):

  def name(self) -> Text:
      return "action_person_detail"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      print("Start action_person_detail")
      entity_person = None
      abfrage_attribute = None
      entity_person = tracker.get_slot(Constants.slot_person)
      abfrage_attribute = tracker.get_slot(Constants.slot_attribute)
      print(entity_person)
      print(abfrage_attribute)
      print(tracker.get_slot(Constants.slot_object_type))
      return_search = Search_return.__init__(Search_return, False)
      if ((entity_person is None)):
          entities = tracker.latest_message[Constants.entities] 
          return SemanticSearch.searchSemanticSearchListOfEntities(dispatcher, entities, tracker).events
      else:
        personExist = DbCall.validationPerson(entity_person)
        if (personExist == True):
          if ((abfrage_attribute is None) | (not(abfrage_attribute in Constants.person_attributes))):
            if (not(tracker.get_slot(Constants.slot_object_type) is None)):
              self.searchForEntityWithObjecttype(dispatcher, tracker, entity_person, tracker.get_slot(Constants.slot_object_type))
              return [SlotSet(Constants.slot_object_type, "")]
            else:
              intent = tracker.latest_message["text"]
              return_search = SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent, Constants.person)
              print(return_search.successfull)
              return return_search.events
          return self.searchForEntityWithAttribut(dispatcher, tracker, entity_person, abfrage_attribute) + [SlotSet(Constants.slot_shall_explain_add_person, False), SlotSet(Constants.slot_attribute, "")]
        else: 
          return SemanticSearch.returnPersonNotExist(dispatcher, tracker) + [SlotSet(Constants.slot_attribute, ""), SlotSet(Constants.slot_object_type, "")]


  def searchForEntityWithObjecttype(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, object_type) -> List[EventType]:
    """
    Hier werden die Entiaeten eines bestimmten Objekttyps zu einer gegebenen Peron zurueck gegeben
    """
    answer = DbCall.searchForEntityRelationship(name, Constants.person)
    checked = False
    root_nodes = answer[Constants.root_nodes]
    node_title = ""
    objects = []
    print(name)
    print(object_type)
    for x in root_nodes: 
      print(x)
      node_checked = GeneralMethods.findeRichtigenKnoten(name, x[Constants.node_title])
      if (node_checked == True):
        entities = DbCall.searchForEntitesFromTheNode(x[Constants.node_id])
        print(entities)
        for x in entities:
            print(x)
            print(x[Constants.ent_ner] == object_type)
            if (x[Constants.ent_ner] == object_type):
                objects.append(x[Constants.ent_text])
        break
    print(len(objects))
    if (len(objects) == 0):
        intent = tracker.latest_message["text"]
        search_return = SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent, Constants.person)
        if (search_return.successfull == True):
          dispatcher.utter_message(text=f"I hope the result helps you further.")
        dispatcher.utter_message(text=f"The correct answer is missing in the graph. Maybe you could add the entity.")
        entity_explained = tracker.get_slot(Constants.slot_explained_add_entity)
        if ((entity_explained is None)):
          dispatcher.utter_message(template="utter_shall_how_add_entity")
          return[SlotSet(Constants.slot_shall_explain_add_entity, True), SlotSet(Constants.slot_explained_add_entity, False)] + search_return.events
        return[SlotSet(Constants.slot_shall_explain_add_entity, False)] + search_return.events
    else:
       if (object_type == Constants.person):
           if (len(objects) == 1):
              dispatcher.utter_message(text=f"I only found " + objects[0] + " with a connection to " + name)
           else: 
              dispatcher.utter_message(text=f"I found these persons who had a connection to " + name + " :")
              dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(objects))
       elif (object_type == Constants.organization):
           if (len(objects) == 1):
              dispatcher.utter_message(text=f"I only the organization " + objects[0] + " with a connection to " + name)
           else: 
              dispatcher.utter_message(text=f"I found these organizations who had a connection to " + name + " :")
              dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(objects))
       else: 
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(objects))

  def searchForEntityWithAttribut(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, attribute) -> List[EventType]:
      answer = DbCall.searchForEntityRelationship(name, Constants.slot_person)
      entities = answer[Constants.entities_relation]
      print(answer)
      return_ok = False
      if(attribute == Constants.date_of_birth):
          return_ok = self.utter_birthday(dispatcher, name, entities)
      elif(attribute == Constants.birthplace):
          return_ok = self.utter_birthplace(dispatcher, name, entities)
      elif(attribute == Constants.city_of_birth):
          return_ok = self.utter_city_of_birth(dispatcher, name, entities)
      elif(attribute == Constants.country_of_birth):
          return_ok = self.utter_country_of_birth(dispatcher, name, entities)
      elif(attribute == Constants.country_of_death):
          return_ok = self.utter_country_of_death(dispatcher, name, entities)
      elif(attribute == Constants.city_of_death):
          return_ok = self.utter_city_of_death(dispatcher, name, entities)
      elif(attribute == Constants.deathplace):
          return_ok = self.utter_deathplace(dispatcher, name, entities)
      elif(attribute == Constants.date_of_death):
          return_ok = self.utter_deathday(dispatcher, name, entities)
      elif(attribute == Constants.cause_of_death):
          return_ok = self.utter_cause_of_death(dispatcher, name, entities)
      elif(attribute == Constants.cities_of_residence):
          return_ok = self.utter_cities_of_residence(dispatcher, name, entities)
      elif(attribute == Constants.countries_of_residence):
          return_ok = self.utter_countries_of_residence(dispatcher, name, entities)
      elif(attribute == Constants.residences):
          return_ok = self.utter_residence(dispatcher, name, entities)
      elif(attribute == Constants.sibling):
          return_ok = self.utter_siblings(dispatcher, name, entities)
      elif(attribute == Constants.children):
          return_ok = self.utter_children(dispatcher, name, entities)
      elif(attribute == Constants.spouse):
          return_ok = self.utter_spouse(dispatcher, name, entities)
      elif(attribute == Constants.other_family):
          return_ok = self.utter_other_family(dispatcher, name, entities)
      elif(attribute == Constants.parents):
          return_ok = self.utter_parents(dispatcher, name, entities)
      elif(attribute == Constants.family):
          return_ok = self.utter_family(dispatcher, name, entities)
      elif(attribute == Constants.title):
          return_ok = self.utter_title(dispatcher, name, entities)
      elif(attribute == Constants.origin):
          return_ok = self.utter_origin(dispatcher, name, entities)
      elif(attribute == Constants.members):
          return_ok = self.utter_member(dispatcher, name, entities)
      elif(attribute == Constants.employee_or_member):
          return_ok = self.utter_members_employees(dispatcher, name, entities)
      elif(attribute == Constants.top_employee_member):
          return_ok = self.utter_top_member(dispatcher, name, entities)
      elif(attribute == Constants.alternate_name):
          return_ok = self.utter_alternate_name(dispatcher, name, entities)
      elif(attribute == Constants.schools_attended):
          return_ok = self.utter_schools_attended(dispatcher, name, entities)
      elif(attribute == Constants.birth):
          return_ok = self.utter_birth(dispatcher, tracker, name, entities)
      elif(attribute == Constants.death):
          return_ok = self.utter_death(dispatcher, tracker, name, entities)
      else:
        output = []  
        for x in entities:
          if((x[Constants.relationship] == attribute) & (x[Constants.ent_text] == name)):
            output.append(x[Constants.ent2_text])
            return_ok =  True
        for x in output:
          dispatcher.utter_message(text=f""+x)
      print(return_ok)
      if (return_ok == False):
        return_search = SemanticSearch.searchSemanticSearchAttribute(dispatcher, tracker, name, attribute, Constants.person)
        print(return_search.events)
        if ((return_search.successfull == True) & (attribute != Constants.biographie)):
          dispatcher.utter_message(text=f"I hope the result helps you further.")
          dispatcher.utter_message(text=f"The correct answer is missing in the graph. Maybe you could add the entity.")
          entity_explained = tracker.get_slot(Constants.slot_explained_add_entity)
          if ((entity_explained is None)):
            dispatcher.utter_message(template="utter_shall_how_add_entity")
            return_events = [SlotSet(Constants.slot_shall_explain_add_entity, True), SlotSet(Constants.slot_explained_add_entity, False)] + return_search.events
            return return_events
        return_events =  [SlotSet(Constants.slot_shall_explain_add_entity, False)] + return_search.events
        print(return_events)
        return return_events
      else:
        shall_explain_add_entity = SlotSet(Constants.slot_shall_explain_add_entity, False)
        node_title = answer[Constants.root_nodes]
        node = ""
        for x in node_title:
          node_title = x[Constants.node_title]
          correct_node = GeneralMethods.findeRichtigenKnoten(name, node_title)
          if (correct_node == True):
            node = node_title
            break
        link = GeneralMethods.linkErstellen(dispatcher, node)
        print(tracker.get_slot(Constants.slot_last_link))
        return [shall_explain_add_entity] + GeneralMethods.linkAusgeben(dispatcher, tracker, link)

  def utter_birth(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, entities) -> bool:
      object_type = tracker.get_slot("object_type")
      print(object_type)
      if (object_type == Constants.city):
        return self.utter_city_of_birth(dispatcher, name, entities)
      elif (object_type == Constants.country):
        return self.utter_country_of_birth(dispatcher, name, entities)
      elif (object_type == Constants.place):
        return self.utter_birthplace(dispatcher, name, entities)
      elif (object_type == Constants.date):
        return self.utter_birthday(dispatcher, name, entities)
      else: 
        birthday = self.utter_birthday(dispatcher, name, entities)
        birthplace = self.utter_birthplace(dispatcher, name, entities)
        return (birthday | birthplace)


  def utter_death(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, entities) -> bool:
      object_type = tracker.get_slot("object_type")
      print(object_type)
      if (object_type == Constants.city):
        return self.utter_city_of_death(dispatcher, name, entities)
      elif (object_type == Constants.country):
        return self.utter_country_of_death(dispatcher, name, entities)
      elif (object_type == Constants.place):
        return self.utter_deathplace(dispatcher, name, entities)
      elif (object_type == Constants.date):
        return self.utter_deathday(dispatcher, name, entities)
      elif (object_type == Constants.cause):
        return self.utter_cause_of_death(dispatcher, name, entities)
      else: 
        deathday = self.utter_deathday(dispatcher, name, entities)
        deathplace = self.utter_deathplace(dispatcher, name, entities)
        deathcause = self.utter_cause_of_death(dispatcher, name, entities)
        return (deathday | deathplace | deathcause)

  def utter_birthday(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if((x[Constants.relationship] == Constants.date_of_birth) & (x[Constants.ent_text] == name)):
          dispatcher.utter_message(text=f"The birthday were on the "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_birthplace(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      print("utter_birthplace")
      checked = False
      country = None
      city = None
      for x in entities:
          if((x[Constants.relationship] == Constants.city_of_birth) & (x[Constants.ent_text] == name)):
              city = x[Constants.ent2_text]
              print(city)
              checked = True
          elif ((x[Constants.relationship] == Constants.country_of_birth) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
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
          if((x[Constants.relationship] == Constants.city_of_birth) & (x[Constants.ent_text] == name)):
              city = x[Constants.ent2_text]
              checked = True
              dispatcher.utter_message(text=f""+ name + " was born in " + city)
              break
      return checked

  def utter_religion(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if((x[Constants.relationship] == Constants.religion) & (x[Constants.ent_text] == name)):
              religion = x[Constants.ent2_text]
              checked = True
              dispatcher.utter_message(text=f"The religion of "+ name + " was " + religion)
              break
      return checked

  def utter_country_of_birth(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if((x[Constants.relationship] == Constants.country_of_birth) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              checked = True
              dispatcher.utter_message(text=f""+ name + " was born in " + country)
              break
      return checked

  def utter_country_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if((x[Constants.relationship] == Constants.country_of_death) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              checked = True
              dispatcher.utter_message(text=f""+ name + " died in " + country)
              break
      return checked
          
  def utter_city_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      for x in entities:
          if((x[Constants.relationship] == Constants.city_of_death) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              checked = True
              dispatcher.utter_message(text=f""+ name + " died in " + country)
              break
      return checked

  def utter_deathplace(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      checked = False
      country = None
      city = None
      for x in entities:
          if((x[Constants.relationship] == Constants.city_of_death) & (x[Constants.ent_text] == name)):
              city = x[Constants.ent2_text]
              checked = True
          elif ((x[Constants.relationship] == Constants.country_of_death) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
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
        if((x[Constants.relationship] == "date_of_death") & (x[Constants.ent_text] == name)):
          dispatcher.utter_message(text=f"The date of death were on the "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_cause_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if((x[Constants.relationship] == Constants.cause_of_death) & (x[Constants.ent_text] == name)):
          dispatcher.utter_message(text=f""+name+" died because of "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_cities_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    cities = []
    for x in entities:
        if((x[Constants.relationship] == Constants.cities_of_residence) & (x[Constants.ent_text] == name)):
          cities.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(cities))
    return checked

  def utter_countries_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    countries = []
    for x in entities:
        if((x[Constants.relationship] == Constants.countries_of_residence) & (x[Constants.ent_text] == name)):
          countries.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(countries))
    return checked

  def utter_stateorprovince_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    stateorprovince = []
    for x in entities:
        if((x[Constants.relationship] == Constants.stateorprovince_of_residence) & (x[Constants.ent_text] == name)):
          stateorprovince.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(stateorprovince))
    return checked

  def utter_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    residences = []
    for x in entities:
        if((x[Constants.relationship] in Constants.residence_attribute) & (x[Constants.ent_text] == name)):
          residences.append(x[Constants.ent2_text])
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
        if((x[Constants.relationship] == Constants.spouse) & (x[Constants.ent_text] == name)):
          spouses.append(x[Constants.ent2_text])
          checked = True
        elif((x[Constants.relationship] == Constants.parents) & (x[Constants.ent_text] == name)):
          parents.append(x[Constants.ent2_text])
          checked = True
        elif((x[Constants.relationship] == Constants.sibling) & (x[Constants.ent_text] == name)):
          siblings.append(x[Constants.ent2_text])
          checked = True
        elif((x[Constants.relationship] == Constants.children) & (x[Constants.ent_text] == name)):
          children.append(x[Constants.ent2_text])
          checked = True
        elif((x[Constants.relationship] == Constants.other_family) & (x[Constants.ent_text] == name)):
          other_family.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f"I found these family members of" + name +":")
        if (len(parents) > 0):
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
        if((x[Constants.relationship] == Constants.parents) & (x[Constants.ent_text] == name)):
          parents.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      if (len(parents) == 1):
        dispatcher.utter_message(text=f"" + parents[0] + " was a parent of " + name)
      else: 
        dispatcher.utter_message(text=f"The parents of "+ name + " were: " + GeneralMethods.liste_ausgeben(children))
    return checked

  def utter_children(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    children = []
    for x in entities:
        if((x[Constants.relationship] == Constants.children) & (x[Constants.ent_text] == name)):
          children.append(x[Constants.ent2_text])
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
        if((x[Constants.relationship] == Constants.sibling) & (x[Constants.ent_text] == name)):
          siblings.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      if (len(siblings) > 1):  
        dispatcher.utter_message(text=f"The siblings of " + name + " were: " + GeneralMethods.liste_ausgeben(siblings))
      else: 
        dispatcher.utter_message(text=f"" + siblings[0] + " was the sibling of " + name)
    return checked

  def utter_other_family(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    other = []
    for x in entities:
        if((x[Constants.relationship] == Constants.other_family) & (x[Constants.ent_text] == name)):
          other.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Other familymembers: " + GeneralMethods.liste_ausgeben(other))
    return checked

  def utter_spouse(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    spouse = []
    for x in entities:
        if((x[Constants.relationship] == Constants.spouse) & (x[Constants.ent_text] == name)):
          spouse.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      if (len(spouse) < 2):
        dispatcher.utter_message(text=f""+spouse[0] + " was the spouse of " + name)
      else:
        dispatcher.utter_message(text=f"" + name + " was married with: " + GeneralMethods.liste_ausgeben(spouse))
    return checked

  def utter_title(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    title = []
    for x in entities:
        if((x[Constants.relationship] == Constants.title) & (x[Constants.ent_text] == name)):
          title.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"" + GeneralMethods.liste_ausgeben(title))
    return checked

  def utter_alternate_name(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    alternate_names = []
    for x in entities:
        if((x[Constants.relationship] == Constants.alternate_name) & (x[Constants.ent_text] == name)):
          alternate_names.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"Alternative Names of "+name+": " + GeneralMethods.liste_ausgeben(alternate_names))
    return checked

  def utter_origin(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    origin = None
    for x in entities:
        if((x[Constants.relationship] == Constants.origin) & (x[Constants.ent_text] == name)):
          origin = x[Constants.ent2_text]
          checked = True
          break
    if (not(origin is None)):
      dispatcher.utter_message(text=f""+ origin + " is the origin of "+name)
    return checked

  def utter_member(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    organizations = None
    for x in entities:
        if((x[Constants.relationship] in self.member) & (x[Constants.ent_text] == name)):
          organizations = x[Constants.ent2_text]
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f""+ name + " was a member of: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_top_member(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if((x[Constants.relationship] == Constants.top_employee_member) & (x[Constants.ent_text] == name)):
          organizations.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was top member of: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_members_employees(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if((x[Constants.relationship] == Constants.employee_or_member) & (x[Constants.ent_text] == name)):
          organizations.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was member of these organizations: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_schools_attended(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    organizations = []
    for x in entities:
        if((x[Constants.relationship] == Constants.schools_attended) & (x[Constants.ent_text] == name)):
          organizations.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      if (len(organizations) > 1):
        dispatcher.utter_message(text=f""+name+ " visit " + organizations[0] + " as a student")
      else: 
        dispatcher.utter_message(text=f""+name+ " visit theses schools: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

