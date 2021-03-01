from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.db_call import DbCall
#import base64,cv2

class ListOfObjecttype(Action):

  def name(self) -> Text:
      return "action_list_of"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_list_of")
    object_type = tracker.get_slot("object_type")
    print(object_type)
    attribute = tracker.get_slot("attribute")
    if (object_type == "ORG"):
      self.searchOrganizations(dispatcher, tracker)
    else: 
      if ((attribute is None) & (not(object_type is None))):
        answer =  DbCall.searchForEntitiy(object_type)
        for x in answer[object_type]:
            dispatcher.utter_message(x)
      else: 
        intent = tracker.latest_message["text"]
        SemanticSearch.searchSemanticSearchIntent(dispatcher, intent)

  def searchOrganizations(self, dispatcher: CollectingDispatcher, tracker: Tracker):
      """
      Sucht alle Organisationen die in dem System gespeichert sind.
      Wenn der Anwender in dem Intent eine Person, eine Stadt oder ein Land mitgibt, dann werden nur die Organisationen zurueck gegeben,
      die auf irgendeine Art und Weise mit der Person, der Stadt oder dem Land verbunden sind.
      """
      answer = DbCall.searchForEntitiy("ORGANIZATION")
      person = tracker.get_slot("PERSON")
      gpe = tracker.get_slot("GPE")
      ausgabe_entities = []
      if ((not(person is None)) | (not(gpe is None))):
        for x in answer["ORGANIZATION"]:
          entities = DbCall.searchForEntityRelationship(x, "ORGANIZATION")
          entities = entities["entities_relations"]
          for y in entities:
              if (y["ent_text"] == x):
                if ((not(person is None)) & (y["ent2_ner"] == "PERSON") & (y["ent2_text"] == person)):
                  ausgabe_entities.append(x)
                elif ((not(person is None)) & ((y["ent2_ner"] == "COUNTRY")|(y["ent2_ner"] == "CITY")) & ((y["ent2_text"] == gpe)|(y["ent2_text"] == gpe))):
                  ausgabe_entities.append(x)
      else: 
          ausgabe_entities = answer["ORGANIZATION"]
      print(ausgabe_entities)
      for x in ausgabe_entities:
          dispatcher.utter_message(text=f""+x)

