from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.db_call import DbCall
from actions.semantic_search import SemanticSearch
from actions.general_methods import GeneralMethods
from actions.constants import Constants

class OrganizationDetailsAction(Action):

  def name(self) -> Text:
      return "action_organization_details"  

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_organization_details")
    organization = tracker.get_slot(Constants.slot_org)
    print(organization)
    attribute = tracker.get_slot(Constants.slot_attribute)
    print(attribute)
    if ((attribute is None) | (not(attribute in Constants.organization_attributes))):
        print("Hier sollte die semantische Suche durchgefuert werden")
        intent = tracker.latest_message["text"]
        print(intent)
        successful = SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
        if (successful == False):
          dispatcher.utter_message(template="utter_ask_rephrase")
    else:
        self.searchSepcificDetailsToOrganization(dispatcher, organization, attribute)

  def searchSepcificDetailsToOrganization(self, dispatcher: CollectingDispatcher, name, attribute):
      """
      Mappt das ermittelte Attribute zu der passenden Ausgabemethode. 
      Wird keine passende Ausgabemethode ermittelt, werden die Attribute aus der Datenbank ohne besondere Methode ausgegeben.
      Wird nichts ausgegeben, weil z.B. kein Attribute aus den Daten ermittelt werden kann, wird die semantische Suche aufgerufen.
      """
      results = DbCall.searchForEntityRelationship(name, Constants.organization)
      entities = results[Constants.entities_relation]
      checked = False
      if(attribute == Constants.city_of_headquarter):
          checked = self.utter_city_of_headquarter(dispatcher, name, entities)
      elif(attribute == Constants.employee_or_member):
          checked = self.utter_employee_or_member_of(dispatcher, name, entities)
      elif(attribute == Constants.top_employee_member):
          checked = self.utter_employee_or_member_of(dispatcher, name, entities)
      elif(attribute == Constants.member):
          checked = self.utter_member(dispatcher, name, entities)
      elif(attribute == Constants.schools_attended):
          checked = self.utter_schools_attended(dispatcher, name, entities)
      elif(attribute == Constants.country_of_headquarter):
          checked = self.utter_country_of_headquarter(dispatcher, name, entities)
      elif(attribute == Constants.stateorprovince_of_headquarter):
          checked = self.utter_stateorprovinces_of_headquarters(dispatcher, name, entities)
      elif(attribute == Constants.headquarter):
          checked = self.utter_headquarters(dispatcher, name, entities)
      elif(attribute == Constants.founded):
          checked = self.utter_founded(dispatcher, name, entities)
      elif(attribute == Constants.founded_by):
          checked = self.utter_founded_by(dispatcher, name, entities)
      elif(attribute == Constants.date_founded):
          checked = self.utter_date_founded(dispatcher, name, entities)
      elif(attribute == Constants.subsidiares):
          checked = self.utterutter_subsidiares(dispatcher, name, entities)
      elif(attribute == Constants.political_religious_affiliation):
          checked = self.utter_political_religiouse_affiliation(dispatcher, name, entities)
      elif(attribute == Constants.biographie):
          checked = self.utter_biographie(dispatcher, name, entities)
      else: 
        for x in entities:
          if(x[Constants.relationship] == attribute):
            dispatcher.utter_message(text=f""+x[Constants.ent2_text])
            checked = True
      if (checked == False):
        print("Daten nicht gefunden")
        successful = SemanticSearch.searchSemanticSearchAttribute(dispatcher, name, attribute, Constants.organization)
        print(successful)
        if (successful == False):
          dispatcher.utter_message(template="utter_ask_rephrase")

  def utter_biographie(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von headquarter, members und affiliaton
    """
    checked_headquarter = self.utter_headquarters(dispatcher, name, entities)
    checked_member = self.utter_member(dispatcher, name, entities)
    checked_affiliation = self.utter_political_religiouse_affiliation(dispatcher, name, entities)
    checked_founded = self.utter_founded(dispatcher, name, entities)
    return (checked_headquarter | checked_member | checked_affiliation | checked_founded)

  def utter_city_of_headquarter(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut city_of_headquarters
    """
    checked = False
    for x in entities:
        if(x[Constants.relationship] == Constants.city_of_headquarter):
          dispatcher.utter_message(text=f"The headquarter is in "+x[Constants.ent2_text])
          checked = True
          break
    return checked    

  def utter_employee_or_member_of(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut employee_or_member
    """
    checked = False
    members = []
    for x in entities:
        if(x[Constants.relationship] == Constants.employee_or_member):
          members.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"These employees or members were by " + name +":")
      dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(members))
    return checked

  def utter_member(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut employee_or_member
    """
    checked = False
    top_members = []
    students = []
    members = []
    for x in entities:
        if(x[Constants.relationship] == Constants.employee_or_member):
          members.append(x[Constants.ent2_text])
          checked = True
        elif(x[Constants.relationship] == Constants.top_employee_member):
          top_members.append(x[Constants.ent2_text])
          checked = True
        elif(x[Constants.relationship] == Constants.schools_attended):
          students.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      if (len(members) > 0):
        dispatcher.utter_message(text=f"These employees or members were: " + GeneralMethods.liste_ausgeben(members))
      if (len(top_members) > 0):
        dispatcher.utter_message(text=f""+ name + " had these top employees/members: " + GeneralMethods.liste_ausgeben(members))
      if (len(students) > 0):
        dispatcher.utter_message(text=f"These students were at " + name + ": " + GeneralMethods.liste_ausgeben(members))
    return checked

  def utter_top_members_employee(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut top_members_employee
    """
    checked = False
    top_members = []
    for x in entities:
        if(x[Constants.relationship] == Constants.top_employee_member):
          top_members.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"These top-members or -employees of " + name + " were:")
      dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(top_members))
    return checked

  def utter_schools_attended(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut schools_attended
    """
    checked = False
    students = []
    for x in entities:
        if(x[Constants.relationship] == Constants.schools_attended):
          students.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f"These students visit the " + name + ":")
        dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(students))
    return checked

  def utter_country_of_headquarter(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut country_of_headquarters
    """
    checked = False
    for x in entities:
        if(x[Constants.relationship] == Constants.country_of_headquarter):
          dispatcher.utter_message(text=f"The headquarter is in "+x[Constants.ent2_text])
          checked = True
          break
    return checked  

  def utter_stateorprovinces_of_headquarters(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut stateorprovince_of_headquarters
    """
    checked = False
    for x in entities:
        if(x[Constants.relationship] == Constants.stateorprovince_of_headquarter):
          dispatcher.utter_message(text=f"The headquarter is in "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_headquarters(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut headquarters
    Beinhaltet dass die Attribute stateorprovinces_of_headquarters, country_of_headquarters und city_of_headquarters abgefragt werden.
    """
    checked = False
    headquarter_city = None
    headquarter_country = None
    headquarter_state_province = None
    for x in entities:
        if(x[Constants.relationship] == Constants.stateorprovince_of_headquarter):
          headquarter_state_province = x[Constants.ent2_text]
          checked = True
        elif(x[Constants.relationship] == Constants.country_of_headquarter):
          headquarter_country = x[Constants.ent2_text]
          checked = True
        elif(x[Constants.relationship] == Constants.city_of_headquarter):
          headquarter_city = x[Constants.ent2_text]
          checked = True
    if (checked == True):
        if ((not(headquarter_state_province is None)) & (not(headquarter_country is None)) & (not(headquarter_city is None))):
            dispatcher.utter_message("The headquarter of " + name + " was in " + headquarter_city + "-" + headquarter_state_province + " (" + headquarter_country + ")")
        elif ((not(headquarter_country is None)) & (not(headquarter_city is None))):
            dispatcher.utter_message("The headquarter of " + name + " was in " + headquarter_city + " (" + headquarter_country + ")")
        elif ((not(headquarter_state_province is None)) & (not(headquarter_country is None))):
            dispatcher.utter_message("The headquarter of " + name + " was in " + headquarter_state_province + " (" + headquarter_country + ")")
        elif ((not(headquarter_state_province is None)) & (not(headquarter_city is None))):
            dispatcher.utter_message("The headquarter of " + name + " was in " + headquarter_city + "-" + headquarter_state_province)
        elif (not(headquarter_state_province is None)):
            dispatcher.utter_message("The headquarter of " + name + " was in " + headquarter_state_province)
        elif (not(headquarter_country is None)):
            dispatcher.utter_message("The headquarter of " + name + " was in " + headquarter_country)
        elif (not(headquarter_city is None)):
            dispatcher.utter_message("The headquarter of " + name + " was in " + headquarter_city) 
    return checked

  def utter_date_founded(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut date_founded
    """
    checked = False
    for x in entities:
        if(x[Constants.relationship] == Constants.date_founded):
          dispatcher.utter_message(text=f"" + name + "was founded in "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_founded_by(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut founded_by
    """
    checked = False
    for x in entities:
        if(x[Constants.relationship] == Constants.founded_by):
          dispatcher.utter_message(text=f""+ x[Constants.ent2_text] + " has founded "+ name)
          checked = True
          break
    return checked

  def utter_founded(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut founded
    """
    checked = False
    date = None
    founder = None
    for x in entities:
        if(x[Constants.relationship] == Constants.founded_by):
          founder = x[Constants.ent2_text]
          checked = True
        elif(x[Constants.relationship] == Constants.date_founded):
          date = x[Constants.ent2_text]
          checked = True
    if (checked == True):
        if ((not(date is None)) & (not(founder is None))):
           dispatcher.utter_message(text=f""+ name + " was founded by " + founder + " in " + date)
        elif (not(date is None)):
          dispatcher.utter_message(text=f"" + name + "was founded in " + date)
        elif (not(founder is None)):
          dispatcher.utter_message(text=f""+ founder + " has founded "+ name)
    return checked

  def utter_political_religiouse_affiliation(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut political_religiouse_affiliation
    """
    checked = False
    affiliation = []
    for x in entities:
        if(x[Constants.relationship] == Constants.political_religious_affiliation):
          affiliation.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
        if (len(affiliation) > 1):
          dispatcher.utter_message(text=f"" + name +  " has these affiliations: ")
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(affiliation))
        else:
          dispatcher.utter_message(text=f"The affiliation of " + name +  " is " + affiliation[0])
    return checked

  def utter_subsidiares(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für das Attribut subsidiares
    """
    checked = False
    subsidiares = []
    for x in entities:
        if(x[Constants.relationship] == Constants.subsidiares):
          subsidiares.append(x[Constants.ent2_text])
          checked = True
    if (checked == True):
        if (len(affiliation) > 1):
          dispatcher.utter_message(text=f"These companiese are subsidiares of " + name +  ": ")
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(subsidiares))
        else:
          dispatcher.utter_message(text=f"" + subsidiares + "is the subsidiares " + name)
    return checked