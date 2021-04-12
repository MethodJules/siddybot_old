from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.db_call import DbCall
from actions.semantic_search import SemanticSearch
from actions.general_methods import GeneralMethods
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType
from actions.search_return import Search_return

# Action zum Suchen von Details zu Organisationen
class OrganizationDetailsAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_organization_details"  

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
    print("start action_organization_details")
    # Auslesen von allen benoetigten Informationen
    organization = tracker.get_slot(Constants.slot_org)
    attribute = tracker.get_slot(Constants.slot_attribute)
    # Wenn keine Organisation gefunden werden konnte, 
    # dann wir mit allen gefundenen Entitaeten eine semantische Suche durchgefuehrt
    if ((organization is None)):
      entities = tracker.latest_message[Constants.entities] 
      return SemanticSearch.searchSemanticSearchListOfEntities(dispatcher, entities, tracker).events
    else:
      # Wenn kein Attribut gefunden wurde oder wenn das gefundene Attribut 
      # nicht zu den Attributen fuer Organisationen gehoert, dann wird eine 
      # semantische Suche mit dem Text der Eingabe durchgefuhert
      if ((attribute is None) | (not(attribute in Constants.organization_attributes))):
        intent = tracker.latest_message["text"]
        return_search = Search_return.__init__(Search_return, False)
        return_search = SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent)
        # Konnte mit dem Text der Eingabe keine Daten ermittelt werden, 
        # dann wird darum gebeten die Frage neu zu stellen
        if (return_search.successfull == False):
          dispatcher.utter_message(template="utter_ask_rephrase")
        return return_search.events      
      else:
        # Wenn eine Organisation und ein Attribut gefunden wurden, 
        # dann werdem die Daten und die passende Ausgabemethode fuer das Attribut gesucht
        return self.searchSepcificDetailsToOrganization(tracker, dispatcher, organization, attribute)

  def searchSepcificDetailsToOrganization(self, tracker: Tracker, dispatcher: CollectingDispatcher, name, attribute) -> List[EventType]:
      """
      Mappt das ermittelte Attribute zu der passenden Ausgabemethode. 
      Wird keine passende Ausgabemethode ermittelt, werden die Attribute aus der Datenbank ohne besondere Methode ausgegeben.
      Wird nichts ausgegeben, weil z.B. kein Attribute aus den Daten ermittelt werden kann, wird die semantische Suche aufgerufen.

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      attribute = Attribut zu welchem Informationen ausgegeben werden sollen
      """
      # Sucht nach allen Beziehungen von der Graphdatenbank
      results = DbCall.searchForEntityRelationship(name, Constants.organization)
      entities = results[Constants.entities_relation]
      checked = False
      # Auswahl der Methode zur Ausgabe des gewuenschten Attributes
      if(attribute == Constants.city_of_headquarter):
          checked = self.utter_city_of_headquarter(dispatcher, name, entities)
      elif(attribute == Constants.employee_or_member):
          checked = self.utter_employee_or_member_of(dispatcher, name, entities)
      elif(attribute == Constants.top_employee_member):
          checked = self.utter_top_members_employee(dispatcher, name, entities)
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
        # Wenn keine passende Methode zur Ausgabe des Attributs gefunden wurde, dann wird
        # so nach dem Attribut in den Daten der Graphdatenbank gesucht und das Ergebnis
        # ohne weiteren Text ausgegeben
        for x in entities:
          if(x[Constants.relationship] == attribute):
            dispatcher.utter_message(text=f""+x[Constants.ent2_text])
            checked = True
      # Wenn keine Daten zu dem gewuenschten Attribut gefunden wurden, 
      # dann wird eine semantische Suche mit dem gewuenschten Attribut und dem Namen der
      if (checked == False):
        return_search = Search_return.__init__(Search_return, False)
        return_search = SemanticSearch.searchSemanticSearchAttribute(dispatcher, tracker, name, attribute, Constants.organization)
        print(return_search.successfull)
        if (return_search.successfull == False):
          dispatcher.utter_message(template="utter_ask_rephrase")
        return return_search.events
      else: 
        return [SlotSet(Constants.slot_semantic_search_result, False)]

  def utter_biographie(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode der "Biographie" einer Organisation
    Dazu gehoeren die Attribute Hauptsitz, Mitglieder, politische/religioese Zugehoerigkeit
    und Gruendungsinformationen

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked_headquarter = self.utter_headquarters(dispatcher, name, entities)
    checked_member = self.utter_member(dispatcher, name, entities)
    checked_affiliation = self.utter_political_religiouse_affiliation(dispatcher, name, entities)
    checked_founded = self.utter_founded(dispatcher, name, entities)
    return (checked_headquarter | checked_member | checked_affiliation | checked_founded)

  def utter_city_of_headquarter(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode wenn nach der Stadt des Hauptsitzes gefragt wird

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche nach einer Relationship mit dem Namen "city_of_headquarter"
    for x in entities:
        if(x[Constants.relationship] == Constants.city_of_headquarter):
          # Ausgabe der Daten
          dispatcher.utter_message(text=f"The headquarter is in "+x[Constants.ent2_text])
          checked = True
          break
    return checked    

  def utter_employee_or_member_of(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode der Mitglieder einer Organisation

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    members = []
    # Suche nach allen Entitaeten zu mit einer Relationship mit dem Namen "employee_or_member_of"
    # mit der Organisation verbunden sind
    for x in entities:
        if(x[Constants.relationship] == Constants.employee_or_member):
          members.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der Daten
    if (checked == True):
      dispatcher.utter_message(text=f"These employees or members were by " + name +":")
      dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(members))
    return checked

  def utter_member(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode der Mitglieder unabhaengig der Art einer Organisation

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    top_members = []
    students = []
    members = []
    # Suche nach allen Entitaeten zu mit einer Relationship mit dem Namen "top_members_employees" oder "employee_or_member_of"
    # mit der Organisation verbunden sind
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
    # Ausgabe der Daten
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
    Ausgabemethode der Hauptmitglieder einer Organisation

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    top_members = []
    # Suche nach allen Entitaeten zu mit einer Relationship mit dem Namen "top_members_employees"
    # mit der Organisation verbunden sind
    for x in entities:
        if(x[Constants.relationship] == Constants.top_employee_member):
          top_members.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der Daten
    if (checked == True):
      dispatcher.utter_message(text=f"These top-members or -employees of " + name + " were:")
      dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(top_members))
    return checked

  def utter_schools_attended(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode wenn nach den Studenten/Schuelern einer Organisation gefragt wird

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    students = []
    # Suche nach allen Entitaeten zu mit einer Relationship mit dem Namen "schools_attended"
    # mit der Organisation verbunden sind
    for x in entities:
        if(x[Constants.relationship] == Constants.schools_attended):
          students.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der Daten
    if (checked == True):
        dispatcher.utter_message(text=f"These students visit the " + name + ":")
        dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(students))
    return checked

  def utter_country_of_headquarter(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode wenn nach dem Land des Hauptsitzes gefragt wird

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche nach der Relationship mit dem Namen country_of_headquarters 
    for x in entities:
        if(x[Constants.relationship] == Constants.country_of_headquarter):
          # Ausgabe der Daten
          dispatcher.utter_message(text=f"The headquarter is in "+x[Constants.ent2_text])
          checked = True
          break
    return checked  

  def utter_stateorprovinces_of_headquarters(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode wenn nach dem Staat oder der Provinz des Hauptsitzes gefragt wird

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche nach der Relationship mit dem Namen stateorprovinces_of_headquarters 
    for x in entities:
        if(x[Constants.relationship] == Constants.stateorprovince_of_headquarter):
          # Ausgabe der Daten
          dispatcher.utter_message(text=f"The headquarter is in "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_headquarters(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode für den Hauptsitz einer Organisation
    Beinhaltet dass die Attribute stateorprovinces_of_headquarters, country_of_headquarters und city_of_headquarters abgefragt werden.

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    headquarter_city = None
    headquarter_country = None
    headquarter_state_province = None
    # Suche nach den Realtionships mit dem Namen "stateorprovinces_of_headquarters", "country_of_headquarters"
    # und/oder "city_of_headquarters"
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
    # Ausgabe der Daten
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
    Ausgabemethode fuer das Gruendungsdatum einer Organisation

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche nach den Realtionships mit dem Namen "date_founded"
    for x in entities:
        if(x[Constants.relationship] == Constants.date_founded):
          # Ausgabe der Daten
          dispatcher.utter_message(text=f"" + name + "was founded in "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_founded_by(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode fuer den Gruender einer Organisation

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche nach den Realtionships mit dem Namen "founded_by"
    for x in entities:
        if(x[Constants.relationship] == Constants.founded_by):
          # Ausgabe der gefundenen Daten
          dispatcher.utter_message(text=f""+ x[Constants.ent2_text] + " has founded "+ name)
          checked = True
          break
    return checked

  def utter_founded(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabemethode fuer Details zur Gruendung der Organisation
    Sucht nach dem Gruender und dem Gruendungsdatum

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    date = None
    founder = None
    # Suche nach den Relationships mit dem Namen "founder_by" und "date_founded"
    for x in entities:
        if(x[Constants.relationship] == Constants.founded_by):
          founder = x[Constants.ent2_text]
          checked = True
        elif(x[Constants.relationship] == Constants.date_founded):
          date = x[Constants.ent2_text]
          checked = True
    # Ausgabe der gefundenen Daten
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
    Ausgabemethode fuer die politische und/oder politische Zugehoerigkeit

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    affiliation = []
    # Suche nach Relationships mit dem Namen political_religiouse_affiliation
    for x in entities:
        if(x[Constants.relationship] == Constants.political_religious_affiliation):
          affiliation.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der gefundenen Daten
    if (checked == True):
        if (len(affiliation) > 1):
          dispatcher.utter_message(text=f"" + name +  " has these affiliations: ")
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(affiliation))
        else:
          dispatcher.utter_message(text=f"The affiliation of " + name +  " is " + affiliation[0])
    return checked

  def utter_subsidiares(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe der Tochterorganisationen einer Organisation

    dispatcher = Disatcher
    name = Name der Organisation zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    subsidiares = []
    # Suche einer Relationship mit den Namen "subsidiares"
    for x in entities:
        if(x[Constants.relationship] == Constants.subsidiares):
          subsidiares.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der gefundenen Daten
    if (checked == True):
        if (len(affiliation) > 1):
          dispatcher.utter_message(text=f"These companiese are subsidiares of " + name +  ": ")
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(subsidiares))
        else:
          dispatcher.utter_message(text=f"" + subsidiares + "is the subsidiares " + name)
    return checked