from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.db_call import DbCall
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType
from actions.search_return import Search_return
from actions.general_methods import GeneralMethods
import random
#import base64,cv2

# Action zum Auflisten von Objekten eines bestimmten Objekttyps
class ListOfObjecttype(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_list_of"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
    print("start action_list_of")
    # Auslesen des Slot fuer den Objekttyp 
    object_type = tracker.get_slot(Constants.slot_object_type)
    # Initialisierung der Rueckgabe der Suche
    return_search = Search_return.__init__(Search_return, False)
    try:
      if (object_type == Constants.organization):
        # Da fuer einen Test bereits mehr Funktionen fuer Organisationen implementiert wurden,
        # gibt es hierfuer eine zusaetzliche Funktion
        # Diese werden doch aktuell nicht genutzt
        self.searchOrganizations(dispatcher, tracker)
      else: 
        # Zunaechst wird geprueft ob ein Objekttyp gefunden wurde und 
        # ob dieser ein Objekttyp der Webseite ist
        if (not(object_type is None) & (object_type in Constants.object_types)):
          # Suchen von allen Objekten der Jigsaw-Webseite
          answer =  DbCall.searchForEntitiy()
          objects = []
          # Filtern der Objekte auf den Objekttyp
          objects = answer[object_type]
          # Ausgabe der Objekte
          self.utter_objects(dispatcher, tracker, objects)
        else: 
          # Wenn kein passender Objekttyp gefunden wurde, 
          # dann wird mit dem gesamten Text eine semantische Suche durchgefuehrt
          intent = tracker.latest_message["text"]
          return_search = SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent)
    except:
      return_search.events.append(GeneralMethods.saveMistakes(tracker))    
    # Rueckgabe der Events aus der semantischen Suche und setzen des Slots Cardinal auf None
    return_events = return_search.events
    return_events.append(SlotSet(Constants.slot_cardinal))
    return return_events

  def searchOrganizations(self, dispatcher: CollectingDispatcher, tracker: Tracker):
      """
      Sucht alle Organisationen die in dem System gespeichert sind.

      Diese Funktion ist vorerst auskommentiert: 
      Wenn der Anwender in dem Intent eine Person, eine Stadt oder ein Land mitgibt, dann werden nur die Organisationen zurueck gegeben,
      die auf irgendeine Art und Weise mit der Person, der Stadt oder dem Land verbunden sind.
      """
      # Auslesen aller Objekte der Datenbank
      answer = DbCall.searchForEntitiy()
      ausgabe_entities = []
      #person = tracker.get_slot(Constants.slot_person)
      #gpe = tracker.get_slot(Constants.slot_place)
      #if ((not(person is None)) | (not(gpe is None))):
      #  for x in answer[Constants.organization]:
      #    entities = DbCall.searchForEntityRelationship(x, Constants.organization)
      #    entities = entities[Constants.entities_relation]
      #    for y in entities:
      #        if (y[Constants.ent_text] == x):
      #          if ((not(person is None)) & (y[Constants.ent2_ner] == Constants.slot_person) & (y[Constants.ent2_text] == person)):
      #            ausgabe_entities.append(x)
      #          elif ((not(person is None)) & ((y[Constants.ent2_ner] == Constants.slot_country)|(y[Constants.ent2_ner] == Constants.slot_city)) & ((y[Constants.ent2_text] == gpe)|(y[Constants.ent2_text] == gpe))):
      #            ausgabe_entities.append(x)
      #else: 
      # Filtern der Objekte auf die des Objekttyp Organisation
      ausgabe_entities = answer[Constants.organization]
      # Ausgabe der Daten
      self.utter_objects(dispatcher, tracker, ausgabe_entities)


  def utter_objects(self, dispatcher: CollectingDispatcher, tracker: Tracker, objects):
      """ 
      Gibt Objekte aus der gelesenen Liste aus. 
      Wenn aus dem Slot "CARDINAL" eine Zahl ermittelt werden kann, dann wird nur diese Anzahl ausgegeben

      dispatcher = Dispatcher
      tracker = Tracker
      objects = Alle Objekte von einem bestimmten Objekttyp
      """
      # Auslesen der Kardinalitaet
      count = tracker.get_slot(Constants.slot_cardinal)
      # Wenn keine Kardinaliaet gefunden wurde, 
      # dann werden alle Objekte ausgegeben
      if (count is None):
        dispatcher.utter_message(text=f""+ GeneralMethods.liste_ausgeben(objects))
        dispatcher.utter_message(template="utter_info_for_output_list_all")
      else:
        try:   
          # Es wird geprueft ob es sich bei der Kardinalitaet um eine Zahl handelt
          count = int(count)
          # Liste mit random Werten zum ausgeben
          output = []
          # Waehlt so lange random Elemente einer Liste aus, 
          # bis die vom Anwender gewuenschte Anzahl an Objekten erreicht ist
          while int(count) > 0:
            object = random.choice(objects)
            print(object)
            output.append(object)
            objects.remove(object)
            count = count - 1
          # Ausgabe der Objekte
          print(output)
          dispatcher.utter_message(text=f"" + GeneralMethods.liste_ausgeben(output))
          dispatcher.utter_message(template="utter_info_for_output_list_some")
        except ValueError: 
            # Wenn die gefundene Kardinalitaet nicht numerisch ist, 
            # dann wird gefragt ob der Anwender seine Anfrage wiederholen kann mit einer numerischen Version der Anzahl 
            dispatcher.utter_message(text=f"I can't handle the text-version of the number. Please repeate your question with the number in a numeric version.")

