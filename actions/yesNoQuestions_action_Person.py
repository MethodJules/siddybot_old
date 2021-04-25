from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
from actions.semantic_search import SemanticSearch
from actions.db_call import DbCall
from actions.general_methods import GeneralMethods
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType
#import base64,cv2

# Action  fuer die Abfrage von Informationen
# Als Antwort wird hier immer nur Ja oder Nein zurueck gegeben
class YesNoQuestionsPersonAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_yes_no_questions_person"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
    print("start action_yes_no_questions")
    # Auslesen von notwendigen Daten wie Name der Person,
    # Attribut und Name des erkannten Intents
    person = tracker.get_slot(Constants.slot_person)
    attribute = tracker.get_slot(Constants.slot_attribute)
    intent = tracker.get_intent_of_latest_message()
    # Pruefung ob eine Entitaet zu der Person existiert
    person_exist = DbCall.validationPerson(person)
    events = []
    checked_bool = False
    if (person_exist == False):
      # Wenn keine passende Entitaet zu einer Person gefunden wurde, 
      # dann wird eine semantische Suche mit den gefundenden Daten aus der Eingabe
      # durchgefuehrt
      return SemanticSearch.returnPersonNotExist(dispatcher, tracker).appned(SlotSet("latest_question",  tracker.latest_message["text"]))
    # Wenn eine Entitaet zu der Person gefunden werden konnte, 
    # dann wird abhaengig von dem gefundenen Intent die weiter fortgefahren
    if (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_attributes"):
      # Handling wenn konkret gefragt wird, ob zu einer Person ein Attribut vorhanden ist
      # Als erstes wird geprueft ob es sich bei dem Attribut um ein Attribut zu einer Person handelt
      # und hab ein Attribut gefunden werden konnte
      if ((not(attribute is None)) & (attribute in Constants.person_attributes)): 
        # Im zweiten Schritt werden alle Relationships zu der Person gelesen
        answer = DbCall.searchForEntityRelationship(person, Constants.person)
        # Im letzten Schritt wird geprueft ob das Attribut in den gefundenen Daten vorhanden ist
        # Wenn das Attribut gefunden werden konnte, wird checked_bool auf True gesetzt
        # und der Slot mit den Attributen wird auf None gesetzt
        for x in answer[Constants.entities_relation]:
            if (x[Constants.relationship] == attribute):
                checked_bool = True
                break
        events.append(SlotSet(Constants.slot_attribute, None))
      else:
        # Konnte kein Attribut oder kein fuer Personen relevantes Attribut in der Nachricht identifiziert werden
        # dann wird eine semantische Suche mit der ganzen Nachricht durchgefuehrt
        return SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, tracker.latest_message["text"]).events.append(SlotSet("latest_question",  tracker.latest_message["text"]))    
    # In den folgenden elif-Bloecken wird jeweils geprueft ob ein konkretes Objekt
    # in dem Graphen der Person vorhanden ist
    # Dafuer wird abhaengig ob ein Attribut in der Eingabe gefunden wurde geprueft ob die Entitaet mit
    # dem jeweiligen Attribut im Graph vor kommt oder ob nur die Entitaet vor kommt
    # Nach dem Suchen der Daten werden die Daten aus den Slots der jeweiligen Objekte und dem Attribut 
    # auf None zurueckgesetzt
    #
    # Umgang mit einem spezifischen Ort in der Eingabe
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_GPE"):
        value_gpe = tracker.get_slot(Constants.slot_place)
        if ((not(attribute is None))):
          checked_bool = GeneralMethods.checkAttributeAndEntity(person,  Constants.person, attribute, value_gpe)
          events.append(SlotSet(Constants.slot_attribute, None))
        else:
          checked_bool = GeneralMethods.checkEntity(person,  Constants.person, value_gpe)
        events.append(SlotSet(Constants.slot_place, None))
    #
    # Umgang mit einer spezifischen Organisation in der Eingabe
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_ORG"):
        value_org = tracker.get_slot(Constants.slot_org)
        if ((not(attribute is None))):
          checked_bool = GeneralMethods.checkAttributeAndEntity(person,  Constants.person, attribute, value_org)
          events.append(SlotSet(Constants.slot_attribute, None))
        else:
          checked_bool = GeneralMethods.checkEntity(person,  Constants.person, value_org)
        events.append(SlotSet(Constants.slot_org, None))
    #
    # Umgang mit einer spezifischen Religion in der Eingabe
    elif (tracker.get_intent_of_latest_message() == "questionsYesNoPerson_connection_to_RELIGION"):
        value_rel = tracker.get_slot(Constants.slot_religion)
        if ((not(attribute is None))):
          checked_bool = GeneralMethods.checkAttributeAndEntity(person,  Constants.person, attribute, value_rel)
          events.append(SlotSet(Constants.slot_attribute, None))
        else:
          checked_bool = GeneralMethods.checkEntity(person,  Constants.person, value_rel)
        events.append(SlotSet(Constants.slot_religion, None))
    # Wenn kein passender Intent identifiziert werden konnte, 
    # dann wird gefragt ob der Anwender seine Frage nochmal wiederholen koennte
    else: 
        dispatcher.utter_message(template="utter_ask_rephrase")
        return
    # Abhaengig ob die gewuenschten Daten gefunden werden konnten wird checked_bool
    # in den Funktionen auf True gesetzt. 
    # Konnten die Daten gefunden werden, dann gibt der Chatbot Yes zurueck
    # Ansonsten No
    if (checked_bool == True):
      dispatcher.utter_message(text=f"Yes")
    else: 
      dispatcher.utter_message(text=f"No")
    return events.append(SlotSet("latest_question",  tracker.latest_message["text"]))