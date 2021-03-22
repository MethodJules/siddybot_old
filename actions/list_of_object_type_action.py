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
#import base64,cv2

class ListOfObjecttype(Action):

  def name(self) -> Text:
      return "action_list_of"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
    print("start action_list_of")
    object_type = tracker.get_slot(Constants.slot_object_type)
    print(object_type)
    number = tracker.get_slot(Constants.slot_cardinal)
    print(number)
    attribute = tracker.get_slot(Constants.slot_attribute)
    return_search = Search_return.__init__(Search_return, False)
    if (object_type == Constants.organization):
      self.searchOrganizations(dispatcher, tracker)
    else: 
      if (not(object_type is None)):
        answer =  DbCall.searchForEntitiy(object_type)
        objects = []
        objects = answer[object_type]
        self.utter_objects(dispatcher, tracker, objects)
      else: 
        intent = tracker.latest_message["text"]
        return_search = SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent)
    return [SlotSet(Constants.slot_cardinal, None)] + return_search.events

  def searchOrganizations(self, dispatcher: CollectingDispatcher, tracker: Tracker):
      """
      Sucht alle Organisationen die in dem System gespeichert sind.
      Wenn der Anwender in dem Intent eine Person, eine Stadt oder ein Land mitgibt, dann werden nur die Organisationen zurueck gegeben,
      die auf irgendeine Art und Weise mit der Person, der Stadt oder dem Land verbunden sind.
      """
      answer = DbCall.searchForEntitiy(Constants.organization)
      person = tracker.get_slot(Constants.slot_person)
      gpe = tracker.get_slot(Constants.slot_place)
      ausgabe_entities = []
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
      ausgabe_entities = answer[Constants.organization]
      print(ausgabe_entities)
      self.utter_objects(dispatcher, tracker, ausgabe_entities)


  def utter_objects(self, dispatcher: CollectingDispatcher, tracker: Tracker, objects):
      """ 
      Gibt Objekte aus der gelesenen Liste aus. 
      Wenn aus dem Slot "CARDINAL" eine Zahl ermittelt werden kann, dann wird nur diese Anzahl ausgegeben
      """
      count = tracker.get_slot(Constants.slot_cardinal)
      if (count is None):
        for x in objects:
          dispatcher.utter_message(text=f""+x)
      else:
        try:   
          count = int(count)
          print(count)
          while int(count) > 0:
            dispatcher.utter_message(text=f""+objects[0])
            objects.remove(objects[0])
            count = count - 1
        except ValueError: 
            dispatcher.utter_message(text=f"I can't handle the text-version of the number. Please write it in a numeric version.")

