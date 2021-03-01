from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.db_call import DbCall
from actions.semantic_search import SemanticSearch
from actions.general_methods import GeneralMethods

class OrganizationDetailsAction(Action):

  def name(self) -> Text:
      return "action_organization_details"

  headquarter_attribute = ["city_of_headquarters", "stateorprovince_of_headquarters", "country_of_headquarters"]

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_organization_details")
    organization = tracker.get_slot("ORG")
    print(organization)
    attribute = tracker.get_slot("attribute")
    print(attribute)
    organization_attributes = ["city_of_headquarters","employee_or_member_of", "top_members_employee", "schools_attended", "member", "country_of_headquarters",
                               "date_founded", "founded_by", "political_religious_affiliation", "stateorprovince_of_headquarters", "subsidiares", "headquarter", "founded"]
    if ((attribute is None) | (not(attribute in organization_attributes))):
        print("Hier sollte die semantische Suche durchgefuert werden")
        intent = tracker.latest_message["text"]
        print(intent)
        SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)
    else:
        self.searchSepcificDetailsToOrganization(dispatcher, organization, attribute)

  def searchSepcificDetailsToOrganization(self, dispatcher: CollectingDispatcher, name, attribute):
      results = DbCall.searchForEntityRelationship(name, "ORGANIZATION")
      entities = results["entities_relations"]
      checked = False
      if(attribute == "city_of_headquarters"):
          checked = self.utter_city_of_headquarter(dispatcher, name, entities)
      elif(attribute == "employee_or_member_of"):
          checked = self.utter_employee_or_member_of(dispatcher, name, entities)
      elif(attribute == "top_members_employee"):
          checked = self.utter_top_members_employee(dispatcher, name, entities)
      elif(attribute == "member"):
          checked = self.utter_employee_or_member_of(dispatcher, name, entities)
          checked = self.utter_top_members_employee(dispatcher, name, entities)
      elif(attribute == "schools_attended"):
          checked = self.utter_schools_attended(dispatcher, name, entities)
      elif(attribute == "country_of_headquarters"):
          checked = self.utter_country_of_headquarter(dispatcher, name, entities)
      elif(attribute == "stateorprovince_of_headquarters"):
          checked = self.utter_stateorprovinces_of_headquarters(dispatcher, name, entities)
      elif(attribute == "headquarter"):
          checked = self.utter_headquarters(dispatcher, name, entities)
      elif(attribute == "founded"):
          checked = self.utter_founded(dispatcher, name, entities)
      elif(attribute == "founded_by"):
          checked = self.utter_founded_by(dispatcher, name, entities)
      elif(attribute == "date_founded"):
          checked = self.utter_date_founded(dispatcher, name, entities)
      elif(attribute == "subsidiares"):
          checked = self.utterutter_subsidiares(dispatcher, name, entities)
      elif(attribute == "political_religious_affiliation"):
          checked = self.utter_political_religiouse_affiliation(dispatcher, name, entities)
      else: 
        for x in entities:
          if(x["rel"] == attribute):
            dispatcher.utter_message(text=f""+x["ent2_text"])
            checked = True
      if (checked == False):
        SemanticSearch.searchSemanticSearchAttribute(dispatcher, name, attribute)
      else: 
          return SlotSet("entity_not_found", False)

  def utter_city_of_headquarter(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "city_of_headquarters"):
          dispatcher.utter_message(text=f"The headquarter is in "+x["ent2_text"])
          checked = True
          break
    return checked    

  def utter_employee_or_member_of(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    members = []
    for x in entities:
        if(x["rel"] == "employee_or_member_of"):
          members.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"These employees or members were by " + name +":")
      dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(members))
    return checked

  def utter_top_members_employee(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    top_members = []
    for x in entities:
        if(x["rel"] == "top_members_employees"):
          top_members.append(x["ent2_text"])
          checked = True
    if (checked == True):
      dispatcher.utter_message(text=f"These top-members or -employees of " + name + " were:")
      dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(top_members))
    return checked

  def utter_schools_attended(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    students = []
    for x in entities:
        if(x["rel"] == "school_attended"):
          students.append(x["ent2_text"])
          checked = True
    if (checked == True):
        dispatcher.utter_message(text=f"These students visit the " + name + ":")
        dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(students))
    return checked

  def utter_country_of_headquarter(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "country_of_headquarters"):
          dispatcher.utter_message(text=f"The headquarter is in "+x["ent2_text"])
          checked = True
          break
    return checked  

  def utter_stateorprovinces_of_headquarters(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "stateorprovinces_of_headquarters"):
          dispatcher.utter_message(text=f"The headquarter is in "+x["ent2_text"])
          checked = True
          break
    return checked

  def utter_headquarters(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    headquarter_city = None
    headquarter_country = None
    headquarter_state_province = None
    for x in entities:
        if(x["rel"] == "stateorprovinces_of_headquarters"):
          headquarter_state_province = x["ent2_text"]
          checked = True
        elif(x["rel"] == "country_of_headquarters"):
          headquarter_country = x["ent2_text"]
          checked = True
        elif(x["rel"] == "city_of_headquarters"):
          headquarter_city = x["ent2_text"]
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
    checked = False
    for x in entities:
        if(x["rel"] == "date_founded"):
          dispatcher.utter_message(text=f"" + name + "was founded in "+x["ent2_text"])
          checked = True
          break
    return checked

  def utter_founded_by(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    for x in entities:
        if(x["rel"] == "founded_by"):
          dispatcher.utter_message(text=f""+ x["ent2_text"] + " has founded "+ name)
          checked = True
          break
    return checked

  def utter_founded(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    date = None
    founder = None
    for x in entities:
        if(x["rel"] == "founded_by"):
          founder = x["ent2_text"]
          checked = True
        elif(x["rel"] == "date_founded"):
          date = x["ent2_text"]
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
    checked = False
    affiliation = []
    for x in entities:
        if(x["rel"] == "political_religious_affiliation"):
          affiliation.append(x["ent2_text"])
          checked = True
    if (checked == True):
        if (len(affiliation) > 1):
          dispatcher.utter_message(text=f"" + name +  " has these affiliations: ")
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(affiliation))
        else:
          dispatcher.utter_message(text=f"The affiliation of " + name +  " is " + affiliation[0])
    return checked

  def utter_subsidiares(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    checked = False
    subsidiares = []
    for x in entities:
        if(x["rel"] == "subsidiares"):
          subsidiares.append(x["ent2_text"])
          checked = True
    if (checked == True):
        if (len(affiliation) > 1):
          dispatcher.utter_message(text=f"These companyse are subsidiares of " + name +  ": ")
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(subsidiares))
        else:
          dispatcher.utter_message(text=f"" + subsidiares + "is the subsidiares " + name)
    return checked