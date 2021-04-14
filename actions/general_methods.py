from rasa_sdk.executor import CollectingDispatcher
from actions.db_call import DbCall
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker

# Klasse in denen Methoden gesammelt werden, die an verschiednenen Stellen genutzt werden
class GeneralMethods():

  def liste_ausgeben(liste) -> str:
    """
    Methode zum ausgeben einer Liste in einer Zeile
    Dabei werden zusaetzlich Kommata zwischen den einzelnen Objekten gesetzt

    liste = die auszugebene Liste
    """
    list_str = ""
    while len(liste) > 1:
        value = liste[0]
        list_str = list_str + value + ", "
        liste.remove(value)
    list_str = list_str + liste[0]
    return list_str

  def linkErstellen(dispatcher: CollectingDispatcher, node_titel) -> str:
    """
    In dieser Methode wird mit Hilfe des node_title der Link zu der Seite der Person erstellt

    dispatcher = Dispatcher
    node_title = Titel des auszugebenen Knoten
    """
    # Entfernen von Zeichen im String
    node_titel = GeneralMethods.deleteMarks(node_titel)
    # Unterteilung des node_title in einzelne Objekte
    node = node_titel.split()
    link = ""
    if (len(node) == 0):
      return link
    # Zusammensetzen des Strings solange
    # Objekte in der Liste vorhanden sind
    while len(node) > 1:
      link = link + node[0] + "-"
      node.remove(node[0])
    link = link + node[0]
    return link

  def deleteMarks(word) -> str:
    """
    Methode zum entfernen von Satzzeichen
    Folgende Satzzeichen werden entfernt:
    Punkt, Komma, Slash, Klammern

    word = String aus dem die Satzzeichen entfernt werden sollen
    """
    word = word.replace(".","")
    word = word.replace(",","")
    word = word.replace("/","")
    word = word.replace("(","")
    word = word.replace(")","")
    return word

  def checkAttributeAndEntity(object, object_type, attribute_to_check, entity_to_check) -> bool:
      """
      Prueft ob zu einem Objekt eine mitgegebene Entitaet vorhanden ist,
      jedoch muss dieses Objekt mit einem spezifischen Attribut vorhanden sein

      object = Objekt zu dem die Entitaet vorhanden sein soll
      object_type = Objekttyp des Objektes
      attribute_to_check = Name der Relationship an dem die Entitaet vorhanden sein soll
      entity_to_check = Entitaet die gesucht wird
      """
      # Liest alle Beziehungen zu dem gewuenschten Objekt
      answer = DbCall.searchForEntityRelationship(object, object_type)
      # Prueft fuer jede gefundene Beziehung ob es sich bei dieser um die gewuenschte Handelt
      # Dafuer werden als erstes die verbundenen Attribute durchgegangen, bei denen es sich nicht 
      # um die genauen Namen aus der Jigsaw-Datenbank handelt
      # Handelt es sich nicht um ein verbundenes Attribut, wird nur geprueft ob der gewuenschte 
      # Name gleich dem Namen der Datenbank ist
      for x in answer[Constants.entities_relation]:
        if (attribute_to_check == Constants.headquarter):
            if (x[Constants.relationship] in Constants.headquarter_attribute):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        elif (attribute_to_check == Constants.member):
            if (x[Constants.relationship] in Constants.members):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        elif (attribute_to_check == Constants.residences):
            if (x[Constants.relationship] in Constants.residence_attribute):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        elif (attribute_to_check == Constants.birthplace):
            if ((x[Constants.relationship] == Constants.city_of_birth) | (x[Constants.relationship] == Constants.country_of_birth)):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        elif (attribute_to_check == Constants.deathplace):
            if ((x[Constants.relationship] == Constants.city_of_death) | (x[Constants.relationship] == Constants.country_of_death)):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        elif (attribute_to_check == Constants.family):
            if (x[Constants.relationship] in Constants.family_attribute):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        else:
          if (x[Constants.relationship] == attribute_to_check):
            if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
              return True
      return False

  def checkEntity(object, object_type, entity_to_check) -> bool:
    """
    Prueft ob zu einem mitgegebenem Objekt eine bestimmte Entitaet vorhanden ist
    
    object = Objekt zu dem die Entitaet vorhanden sein soll
    object_type = Objekttyp des Objektes
    entity_to_check = Entitaet die gesucht wird
    """
    # Lesen aller Beziehungen zu einem Objekt
    answer = DbCall.searchForEntityRelationship(object, object_type)
    checked = False
    # Bei Personen werden alle Daten des Wurzelknotens gelesen 
    if (object_type == Constants.person):
      root_nodes = answer[Constants.root_nodes]
      node_title = ""
      # Als erstes wird geprueft ob der Wurzelknoten fuer die gewuenschte Person in der Rueckgabe 
      # gefunden werden konnte
      for x in root_nodes: 
        node_checked = GeneralMethods.findeRichtigenKnoten(object, x[Constants.node_title])
        # Wenn der richtige Knoten gefunden werden konnte, 
        # dann werden mit der ID des Knotens alle Entitaeten die mit dem Knoten verbunden sind gelesen
        if (node_checked == True):
            entities = DbCall.searchForEntitesFromTheNode(x[Constants.node_id])
            # Fuer die einzelnen Entitaeten wird dann geprueft ob die 
            # gesuchte Entitaet vorhanden ist
            for x in entities:
                if (x[Constants.ent_text] == entity_to_check):
                    return True
    # Wenn es sich um ein anderen Objekt als eine Person handelt oder wenn zu der Person
    # kein Wurzelknoten gefunden werden konnte oder wenn die Entitaet nicht gefunden wurde
    # dann werden alle gefundenen Beziehungen durchgegangen und geprueft ob die Entitaet so
    # gefunden werden kann
    if (checked == False):
      for x in answer[Constants.entities_relation]:
        if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
          return True
    return False

  def findeRichtigenKnoten(name, node_title) -> bool:
      """
      Methode zum vergleich ob es sich bei einem node_titel
      um den Wurzelknoten des gewuenschten Namen handelt
      """
      # Pruefung ob die einzelnen Woerter im node_titel vorkommen
      substrings = name.split()
      for x in substrings:
        if (not(x in node_title)):
          return False
      return True

  def linkAusgeben(dispatcher: CollectingDispatcher, tracker: Tracker, link) -> List[EventType]:
    """
    Gibt den Link aus, wenn es sich nicht um den Gleichen wie der davor handelt

    dispatcher = Dispatcher
    tracker = Tracker
    link = Link der ausgegeben werden soll
    """
    # Pruefung ob der Link laenger als 0 ist 
    # und ob es sich nicht um den gleichen wie davor handelt
    if ((len(link) > 0) & (not(link == tracker.get_slot(Constants.slot_last_link)))):
      # Ausgabe des Links
      dispatcher.utter_message(text=f"For more informations you can look here:")
      dispatcher.utter_message(text=f"https://www.jigsaw-navi.net/de/content/"+link)
    # Speichern des Links im dafuer vorgesehendem Slot
    set_slot_link = [SlotSet(Constants.slot_last_link, link)]
    return set_slot_link
