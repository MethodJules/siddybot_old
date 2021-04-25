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

# Action fuer die Abfrage von Details zu einer Person
class PersonDetailAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_person_detail"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      print("Start action_person_detail")
      entity_person = None
      abfrage_attribute = None
      # Ermittlung der Daten aus den Slots Person und Attribut
      entity_person = tracker.get_slot(Constants.slot_person)
      abfrage_attribute = tracker.get_slot(Constants.slot_attribute)
      # Initialisierung von Suchergebnis
      return_search = Search_return.__init__(Search_return, False)
      events = [SlotSet(Constants.slot_attribute), SlotSet(Constants.slot_object_type), SlotSet("latest_question",  tracker.latest_message["text"])]
      # Pruefung ob eine Person in der Eingabe gefunden werden konnte
      if ((entity_person is None)):
          # Wenn keine Person gefunden wurde, dann wir mit allen Entitaeten der letzten Nachricht eine semantische Suche durchgefuehrt
          entities = tracker.latest_message[Constants.entities] 
          events.extend(SemanticSearch.searchSemanticSearchListOfEntities(dispatcher, entities, tracker).events)
      else:
        # Pruefung ob die gefundene Person in den Daten vorhanden ist
        personExist = DbCall.validationPerson(entity_person)
        if (personExist == True):
          # Pruefung ob kein Attribut gefunden werden konnte und ob es sich dabei nicht um ein Attribut zu einer Person handelt
          if ((abfrage_attribute is None) | (not(abfrage_attribute in Constants.person_attributes))):
            # Pruefung ob ein Objekttyp in der Eingabe des Anwender erkannt werden konnte
            if (not(tracker.get_slot(Constants.slot_object_type) is None)):
              # Wenn kein Attribut aber ein Objekttyp identifiziert werden konnte, dann werden alle Entitaeten mit dem gewuenschten Objekttyp gesucht und ausgegeben
              events.extend(self.searchForEntityWithObjecttype(dispatcher, tracker, entity_person, tracker.get_slot(Constants.slot_object_type)))
            else:
              # Konnte kein Attribut oder Objekttyp gefunden werden, 
              # dann wird mit dem gesamten Text der Eingabe eine semantische Suche durchgefuehrt um moegliche Verbindungen zu finden
              intent = tracker.latest_message["text"]
              return_search = SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent, Constants.person)
              events.extend(return_search.events)
          else:
            # Da ein Attribut identifiziert werden konnte, wird zu diesem Attribut das die Entitaet gesucht
            events.extend(self.searchForEntityWithAttribut(dispatcher, tracker, entity_person, abfrage_attribute))
            events.append(SlotSet(Constants.slot_shall_explain_add_person, False))
        else:
          # Wenn keine konkrete Entitaet fuer die Person vorhanden ist, dann wird eine semantische Suche durchgefuehrt, 
          # ob der Name in den Steckbriefen der anderen Personen gefunden werden kann.
          # Ausserdem werden die Slots attribute und object_type zurueckgesetzt
          # In der Methode SemanticSearch.returnPersonNotExist wird ausserdem der Slot shall_explain_add_person auf true gesetzt, 
          # damit danach im Anschluss erklaert wird, wie die Person angelegt werden kann
         events.extend(SemanticSearch.returnPersonNotExist(dispatcher, tracker))
      # Rueckgabe aller gesammelten Events dieser Action
      print(events)
      return events


  def searchForEntityWithObjecttype(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, object_type) -> List[EventType]:
    """
    Methode zum suchen aller Entitaeten eines gewuenschten Objekttyps zu einer konkreten Person
    dispatcher = Disatcher
    tracker = Tracker
    name = Name der Person zu der Daten erfragt werden sollen
    object_type = Objekttyp der Entitaeten die ermittelt werden sollen
    """
    # Aufruf der Methode zum Suchen aller Beziehungen zu einer Entitaet
    answer = DbCall.searchForEntityRelationship(name, Constants.person)
    checked = False
    # Ermittlung der Wurzelknoten zu den Daten die gefunden wurden
    root_nodes = answer[Constants.root_nodes]
    node_title = ""
    objects = []
    # Ermittlung des richtigen Wurzelknoten fuer die gewuenschte Person
    for x in root_nodes: 
      node_checked = GeneralMethods.findeRichtigenKnoten(name, x[Constants.node_title])
      if (node_checked == True):
        # Wenn der richtige Knoten gefunden werden konnte, 
        # dann werden alle Entitaeten des Knotens gelesen
        entities = DbCall.searchForEntitesFromTheNode(x[Constants.node_id])
        # Sammeln aller Entitaeten mit dem gewuenschten Objekttyp
        for x in entities:
            if (x[Constants.ent_ner] == object_type):
                objects.append(x[Constants.ent_text])
        break
    # Wenn keine Objekte gefunden wurden, 
    # dann wir eine semantische Suche mit dem Text des Intents durchgefuehrt
    # Ausserdem soll darauf aufmerksam gemacht werden, dass eine Enitaet fehlt und das erklaert werden soll
    # wie diese angelegt werden kann
    if (len(objects) == 0):
        intent = tracker.latest_message["text"]
        search_return = SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent, Constants.person)
        dispatcher.utter_message(text=f"The correct answer is missing in the graph. Maybe you could add the entity.")
        if (tracker.get_slot(Constants.slot_explained_add_entity) == True):
          return[SlotSet(Constants.slot_shall_explain_add_entity, False)].extend(search_return.events)
        else: 
          return[SlotSet(Constants.slot_shall_explain_add_entity, True)].extend(search_return.events)
    else:
       # Wenn Objekte gefunden wurden, dann sollen die Ergebnisse mit einem passenden Text zu dem Objekttyp
       # ausgegeben werden.
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
          # Wenn ein Objekttyp nicht explizit beruecksichtigt wurde, dann wird die Liste an Objekten einfach so ausgegeben
          dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(objects))
       return [SlotSet(Constants.slot_semantic_search_result, False), SlotSet(Constants.slot_shall_explain_add_entity, False), SlotSet(Constants.slot_object_type)]

  def searchForEntityWithAttribut(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, attribute) -> List[EventType]:
      """
      Funktion um die Entitaet eines gewuenschten Attributes zu einer Person auszugeben
      dispatcher = Disatcher
      tracker = Tracker
      name = Name der Person zu der Daten erfragt werden sollen
      attribute = Name des gesuchten Attributes
      """
      # Auslesen aller Relationships zu einer Person aus der Graphdatenbank
      answer = DbCall.searchForEntityRelationship(name, Constants.slot_person)
      entities = answer[Constants.entities_relation]
      return_ok = False
      # Aufruf der passenden Antwortmethode zu dem gefundenen Attribut
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
        # Wenn keine passende Methode zum beantworten der Frage gefunden werden konnte, 
        # wird trotzdem nach dem passenden Attribut in den Ergebnissen gesucht
        # Die Entitaet wird dann ohne weiteren Text ausgegeben
        output = []  
        for x in entities:
          if((x[Constants.relationship] == attribute) & (x[Constants.ent_text] == name)):
            output.append(x[Constants.ent2_text])
            return_ok =  True
        for x in output:
          dispatcher.utter_message(text=f""+x)
      # Wenn kein passendes Attribut gefunden werden konnte, 
      # dann wird eine semantische Suche mit dem Attribut und der Person ausgefuehrt
      return_events = []
      if (return_ok == False):
        return_search = SemanticSearch.searchSemanticSearchAttribute(dispatcher, tracker, name, attribute, Constants.person)
        # Wenn das Attribut nicht Biographie ist, dann wird zusaetzlich gesagt, dass das Attribut im Graphen fehlt
        # und der Slot wird gesetzt, dass erklaert werden soll, wie eine Entitaet hinzugefuegt werden soll
        if (attribute != Constants.biographie):
          dispatcher.utter_message(template="utter_entity_is_missing")
          if (tracker.get_slot(Constants.slot_explained_add_entity) == True):
            return_events.append(SlotSet(Constants.slot_shall_explain_add_entity, False))
          else: 
            return_events.append(SlotSet(Constants.slot_shall_explain_add_entity, True))
        else:
          return_events.append(SlotSet(Constants.slot_shall_explain_add_entity, False))
        return_events.extend(return_search.events)
      else:
        # Wenn alle Daten gefunden werden, werden die Slots zum erklaeren der Entitaet und 
        # zur Frage ob die Ergebnisse hilfreich waren vorsichtshalber auf False gesetzt
        shall_explain_add_entity = SlotSet(Constants.slot_shall_explain_add_entity, False)
        semantic_search_result = SlotSet(Constants.slot_semantic_search_result, False)
        # Damit der Anwender nach weiteren Daten auf der Webseite der Person schauen kann, 
        # wird zusaetzlich zur Ausgabe des Ergebnisses auf der Link zur Webseite der Person ausgegeben
        node_title = answer[Constants.root_nodes]
        node = ""
        for x in node_title:
          node_title = x[Constants.node_title]
          correct_node = GeneralMethods.findeRichtigenKnoten(name, node_title)
          if (correct_node == True):
            node = node_title
            break
        link = GeneralMethods.linkErstellen(dispatcher, node)
        return_events = GeneralMethods.linkAusgeben(dispatcher, tracker, link)
        return_events.extend([shall_explain_add_entity, semantic_search_result])
      print(return_events)
      return return_events

  def utter_birth(self, dispatcher: CollectingDispatcher, tracker: Tracker, name, entities) -> bool:
      """
      Funktion zur Suche von Details zu der Geburt einer Person
      Die Rueckgabe erfolgt abhaenigig von dem in der Nachricht gefundenen Objekttyps.
      Wenn kein Objekttyp gefunden wurde, dann werden alle im Graph vorhandenen 
      Details zur Geburt einer Person ausgegeben

      dispatcher = Disatcher
      tracker = Tracker
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      object_type = tracker.get_slot("object_type")
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
      """
      Funktion zur Suche von Details zu dem Tod einer Person
      Die Rueckgabe erfolgt abhaenigig von dem in der Nachricht gefundenen Objekttyps.
      Wenn kein Objekttyp gefunden wurde, dann werden alle im Graph vorhandenen 
      Details zum Tod einer Person ausgegeben

      dispatcher = Disatcher
      tracker = Tracker
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
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
    """
    Funktion mit der der Geburtstags einer Person ausgegeben wird

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche der Relationship mit dem Namen "date_of_birth"
    for x in entities:
        if((x[Constants.relationship] == Constants.date_of_birth) & (x[Constants.ent_text] == name)):
          # Ausgabe der Daten
          dispatcher.utter_message(text=f"The birthday were on the "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_birthplace(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      """
      Funktion mit der der Geburtsort (Stadt und/oder Land) einer Person ausgegeben wird

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      checked = False
      country = None
      city = None
      # Suche nach den Relationships mit dem Namen "city_of_birth"  und "country_of_birth"
      for x in entities:
          if((x[Constants.relationship] == Constants.city_of_birth) & (x[Constants.ent_text] == name)):
              city = x[Constants.ent2_text]
              print(city)
              checked = True
          elif ((x[Constants.relationship] == Constants.country_of_birth) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              print(country)
              checked = True
      # Ausgabe der Daten
      if checked == True:
          if ((not(city is None)) & (not(country is None))):
              dispatcher.utter_message(text=f""+city + "("+country+")")
          elif (not(country is None)):
              dispatcher.utter_message(text=f""+country)
          elif (not(city is None)):
              dispatcher.utter_message(text=f""+city)
      return checked

  def utter_city_of_birth(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      """
      Funktion mit der die Stadt in dem eine Person geboren ist ausgegeben wird

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      checked = False
      # Suche nach der Relationship mit dem Namen "city_of_birth"
      for x in entities:
          if((x[Constants.relationship] == Constants.city_of_birth) & (x[Constants.ent_text] == name)):
              city = x[Constants.ent2_text]
              checked = True
              # Ausgabe der Daten
              dispatcher.utter_message(text=f""+ name + " was born in " + city)
              break
      return checked

  def utter_religion(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      """
      Funktion mit der die Religion einer Person ausgegeben wird

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      checked = False
      for x in entities:
          # Suche einer Relationship mit dem Namen "religion"
          if((x[Constants.relationship] == Constants.religion) & (x[Constants.ent_text] == name)):
              religion = x[Constants.ent2_text]
              checked = True
              # Ausgabe der Daten
              dispatcher.utter_message(text=f"The religion of "+ name + " was " + religion)
              break
      return checked

  def utter_country_of_birth(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      """
      Funktion mit der das Land in dem eine Person geboren ist ausgegeben wird

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      checked = False
      # Suche nach der Relationship mit dem Namen "country_of_birth" 
      for x in entities:
          if((x[Constants.relationship] == Constants.country_of_birth) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              checked = True
              # Ausgabe der Daten
              dispatcher.utter_message(text=f""+ name + " was born in " + country)
              break
      return checked

  def utter_country_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      """
      Funktion mit der das Land in dem eine Person gestorben ist ausgegeben wird

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      checked = False
      # Suche nach der Relationship mit dem Namen "country_of_death"
      for x in entities:
          if((x[Constants.relationship] == Constants.country_of_death) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              checked = True
              # Ausgabe der Daten
              dispatcher.utter_message(text=f""+ name + " died in " + country)
              break
      return checked
          
  def utter_city_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      """
      Funktion mit der die Stadt in dem eine Person gestorben ist ausgegeben wird

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

      Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      checked = False
      # Suche nach der Relationship mit dem Namen "city_of_death"
      for x in entities:
          if((x[Constants.relationship] == Constants.city_of_death) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              checked = True
              # Ausgabe der Daten
              dispatcher.utter_message(text=f""+ name + " died in " + country)
              break
      return checked

  def utter_deathplace(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
      """
      Funktion mit der der Ort des Todes einer Person ausgegeben wird

      dispatcher = Disatcher
      name = Name der Person zu der Daten erfragt werden sollen
      entities = Daten aus der Graphdatenbank

        Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
      """
      checked = False
      country = None
      city = None
      # Suche der Daten (Stadt, Land) fuer den Ort des Todes einer Person 
      for x in entities:
          if((x[Constants.relationship] == Constants.city_of_death) & (x[Constants.ent_text] == name)):
              city = x[Constants.ent2_text]
              checked = True
          elif ((x[Constants.relationship] == Constants.country_of_death) & (x[Constants.ent_text] == name)):
              country = x[Constants.ent2_text]
              checked = True
      # Ausgabe der Daten
      if checked == True:
          if ((not(city is None)) & (not(country is None))):
              dispatcher.utter_message(text=f""+city + "("+country+")")
          elif (not(country is None)):
              dispatcher.utter_message(text=f""+country)
          elif (not(city is None)):
              dispatcher.utter_message(text=f""+city)
      return checked

  def utter_deathday(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Funktion mit der der Todestag einer Person ausgegeben wird

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche der Relationship mit dem Namen "date_of_death" zu einer Person
    for x in entities:
        if((x[Constants.relationship] == "date_of_death") & (x[Constants.ent_text] == name)):
          # Ausgabe der Daten
          dispatcher.utter_message(text=f"The date of death were on the "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_cause_of_death(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Funktion mit der der Grund des Todes einer Person ausgegeben wird

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    # Suche nach dem Grund des Todes einer Person
    for x in entities:
        if((x[Constants.relationship] == Constants.cause_of_death) & (x[Constants.ent_text] == name)):
          # Ausgabe des gefundenen Todesgrund
          dispatcher.utter_message(text=f""+name+" died because of "+x[Constants.ent2_text])
          checked = True
          break
    return checked

  def utter_cities_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Aufenthaltsorten die ueber die Relationship cities_of_residences
    mit der Person Verbunden sind

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    cities = []
    # Suche von allen Aufenthaltsorten mit dem Relationship-Namen cities_of_residences
    for x in entities:
        if((x[Constants.relationship] == Constants.cities_of_residence) & (x[Constants.ent_text] == name)):
          cities.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(cities))
    return checked

  def utter_countries_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Aufenthaltsorten die ueber die Relationship countries_of_residences
    mit der Person Verbunden sind

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    countries = []
    # Suche von allen Aufenthaltsorten mit dem Relationship-Namen countries_of_residences
    for x in entities:
        if((x[Constants.relationship] == Constants.countries_of_residence) & (x[Constants.ent_text] == name)):
          countries.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(countries))
    return checked

  def utter_stateorprovince_of_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Aufenthaltsorten die ueber die Relationship stateOrProvince_of_residences
    mit der Person Verbunden sind

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    stateorprovince = []
    # Suche von allen Aufenthaltsorten mit dem Relationship-Namen stateOrProvince_of_residences
    for x in entities:
        if((x[Constants.relationship] == Constants.stateorprovince_of_residence) & (x[Constants.ent_text] == name)):
          stateorprovince.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(stateorprovince))
    return checked

  def utter_residence(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Aufenthaltsorten ohne den Objekttyp zu beruecksichtigen

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    residences = []
    # Suche von allen Aufenthaltsorten unabhaengig des Objekttyps die ueber ein Relationship 
    # des Themenbereiches "residences" mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] in Constants.residence_attribute) & (x[Constants.ent_text] == name)):
          residences.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
        dispatcher.utter_message(text=f""+name+ " lived in:" + GeneralMethods.liste_ausgeben(residences))
    return checked
      
  def utter_family(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Attributen des Themenbereiches Familie zu einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    parents = []
    siblings = []
    spouses = []
    children = []
    other_family = []
    # Suche von allen Entitaeten die ueber eine Relationship die dem Themenbereich Familie zugeordnet werden kann 
    # mit der Person verbunden sind
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
    # Ausgabe aller gefundenen Daten
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
    """
    Ausgabe von den Eltern einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    parents = []
    # Suche von allen Entitaeten die ueber die Relationship "parents" mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] == Constants.parents) & (x[Constants.ent_text] == name)):
          parents.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
      if (len(parents) == 1):
        dispatcher.utter_message(text=f"" + parents[0] + " was a parent of " + name)
      else: 
        dispatcher.utter_message(text=f"The parents of "+ name + " were: " + GeneralMethods.liste_ausgeben(children))
    return checked

  def utter_children(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Kindern einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    children = []
    # Suche von allen Entitaeten die ueber die Relationship "children" mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] == Constants.children) & (x[Constants.ent_text] == name)):
          children.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
      if (len(children == 1)):
        dispatcher.utter_message(text=f""+ name + " had one child named " + GeneralMethods.liste_ausgeben(children))
      else: 
        dispatcher.utter_message(text=f"The children of "+ name + " were: " + GeneralMethods.liste_ausgeben(children))
    return checked

  def utter_siblings(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Geschwistern einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    siblings = []
    # Suche von allen Entitaeten die ueber die Relationship "siblings" mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] == Constants.sibling) & (x[Constants.ent_text] == name)):
          siblings.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
      if (len(siblings) > 1):  
        dispatcher.utter_message(text=f"The siblings of " + name + " were: " + GeneralMethods.liste_ausgeben(siblings))
      else: 
        dispatcher.utter_message(text=f"" + siblings[0] + " was the sibling of " + name)
    return checked

  def utter_other_family(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Familienmitglieder die ueber die Relationship mit dem Namen "other_family" mit 
    einer Person verbunden sind

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    other = []
    # Suche aller Entitaeten die ueber die Relationship "other_family" mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] == Constants.other_family) & (x[Constants.ent_text] == name)):
          other.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
      dispatcher.utter_message(text=f"Other familymembers: " + GeneralMethods.liste_ausgeben(other))
    return checked

  def utter_spouse(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Ehepartnern einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    spouse = []
    # Suche von allen Relationships mit dem Namen "spouse" einer Person
    for x in entities:
        if((x[Constants.relationship] == Constants.spouse) & (x[Constants.ent_text] == name)):
          spouse.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller gefundenen Daten
    if (checked == True):
      if (len(spouse) < 2):
        dispatcher.utter_message(text=f""+spouse[0] + " was the spouse of " + name)
      else:
        dispatcher.utter_message(text=f"" + name + " was married with: " + GeneralMethods.liste_ausgeben(spouse))
    return checked

  def utter_title(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von allen Jobs einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    title = []
    # Sammeln aller Jobs die zu der Person gefunden werden konnten (alle Beziehungen mit dem Titel "title")
    for x in entities:
        if((x[Constants.relationship] == Constants.title) & (x[Constants.ent_text] == name)):
          title.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe aller Jobs
    if (checked == True):
      dispatcher.utter_message(text=f"" + GeneralMethods.liste_ausgeben(title))
    return checked

  def utter_alternate_name(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe von alternativen Namen einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    alternate_names = []
    # Suche von allen "alternate_name"-Beziehungen in dem Graph
    for x in entities:
        if((x[Constants.relationship] == Constants.alternate_name) & (x[Constants.ent_text] == name)):
          alternate_names.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der Daten
    if (checked == True):
      dispatcher.utter_message(text=f"Alternative Names of "+name+": " + GeneralMethods.liste_ausgeben(alternate_names))
    return checked

  def utter_origin(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe des Ursprungs einer Person

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    origin = None
    # Suche nach dem Attribut "origin" in den Daten zu einer Person
    for x in entities:
        if((x[Constants.relationship] == Constants.origin) & (x[Constants.ent_text] == name)):
          origin = x[Constants.ent2_text]
          checked = True
          break
    # Ausgabe des Ursprungs
    if (not(origin is None)):
      dispatcher.utter_message(text=f""+ origin + " is the origin of "+name)
    return checked

  def utter_member(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe bei welchen Organisationen eine Person ein Mitglied jeglicher Art war

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    organizations = None
    # Sammeln aller Organisationen die mit Attributen fuer Mitglieder mit der Person verbunden sind
    for x in entities:
      if((x[Constants.relationship] in Constants.members) & (x[Constants.ent_text] == name)):
        organizations = x[Constants.ent2_text]
        checked = True
    # Ausgabe der Organisationen
    if (checked == True):
      dispatcher.utter_message(text=f""+ name + " was a member of: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_top_member(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe bei welchen Organisationen eine Person ein Hauptmitglied war

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    organizations = []
    # Sammeln aller Organisationen die mit dem gewuenschten Attribut mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] == Constants.top_employee_member) & (x[Constants.ent_text] == name)):
          organizations.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der Organisationen
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was top member of: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_members_employees(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe bei welchen Organisationen eine Person ein Mitglied war

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    organizations = []
    # Sammeln aller Organisationen die mit dem gewuenschten Attribut mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] == Constants.employee_or_member) & (x[Constants.ent_text] == name)):
          organizations.append(x[Constants.ent2_text])
          checked = True
    # Ausgabe der Organisationen
    if (checked == True):
      dispatcher.utter_message(text=f""+name+ " was member of these organizations: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

  def utter_schools_attended(self, dispatcher: CollectingDispatcher, name, entities) -> bool:
    """
    Ausgabe welche Schulen/Universitaeten eine Person besucht hat

    dispatcher = Disatcher
    name = Name der Person zu der Daten erfragt werden sollen
    entities = Daten aus der Graphdatenbank

    Rueckgabe kennzeichnet ob das gewuenschte Attribut gefunden wurde oder nicht
    """
    checked = False
    organizations = []
    # Sammeln aller Organisationen die mit dem Attribut "schools_attended" mit der Person verbunden sind
    for x in entities:
        if((x[Constants.relationship] == Constants.schools_attended) & (x[Constants.ent_text] == name)):
          organizations.append(x[Constants.ent2_text])
          checked = True
    # Wenn Organisationen gefunden werden konnten, 
    # dann werden diese ausgegeben
    if (checked == True):
      if (len(organizations) > 1):
        dispatcher.utter_message(text=f""+name+ " visit " + organizations[0] + " as a student")
      else: 
        dispatcher.utter_message(text=f""+name+ " visit theses schools: " + GeneralMethods.liste_ausgeben(organizations))
    return checked

