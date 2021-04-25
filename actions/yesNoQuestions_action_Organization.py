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

# Action zur Beantwortung von Ja oder Nein Fragen zu Organisationen
class YesNoQuestionsOrganizationAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_yes_no_questions_organization"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
    print("start action_yes_no_questions_organization")
    # Auslesen der benoetigten Daten
    intent = tracker.get_intent_of_latest_message()
    attribute = tracker.get_slot(Constants.slot_attribute)
    organization = tracker.get_slot(Constants.slot_org)
    checked_bool = False
    # Funktion wenn geprueft werden soll ob ein spezifisches Attribut im Graph vorhanden ist
    if (intent == "questionsYesNoOrganization_attributes") :
      if ((not(attribute is None)) & (attribute in Constants.organization_attributes)):
        # Liest alle Beziehungen zu einem Objekt aus den Graphdatenbank
        answer = DbCall.searchForEntityRelationship(organization, Constants.organization)
        # Prueft ob das gewuenschte Attribut in den Daten des Objektes 
        # gefunden werden kann
        for x in answer[Constants.entities_relation]:
            if (x[Constants.relationship] == attribute):
                checked_bool = True
                break
      else:
        # Wenn die noetigen Informationen nicht gefunden werden koennen, 
        # dann wird eine semantische Suche mit den gefundenen Eingaben durchgefuehrt
        intent = tracker.latest_message["text"]
        return SemanticSearch.searchSemanticSearchIntent(dispatcher, tracker, intent).events.append(SlotSet("latest_question",  tracker.latest_message["text"]))
    # Funktionen wenn spezifische Objekte gesucht werden in dem Graph des Objektes
    # Dabei kann es sich entweder um Orte oder Religionen handeln
    # Personen werden hier nicht beruecksichtigt, 
    # weil dafuer die Action yesNoQuestions_action_Person verwendet werden soll
    # Der Aufbau ist bei allen gleich:
    # Zunaechst wird der benoetigte Slot ausgelesen
    # Wenn ein Attribut gefunden wurde, dann wird geprueft ob es sich dabei um ein Attribut zu Organisationen handelt
    # Trifft dies zu, dann wird geprueft ob zu dem Objekt die gewuenschte Entitaet an dem spezifischen Attribut vorhanden ist
    # Kann kein Attribut gefunden werden, dann wird nur geprueft ob die Entitaet zu dem Objekt gefunden werden kann
    elif (intent == "questionsYesNoOrganization_connection_to_GPE"):
      value_gpe = tracker.get_slot[Constants.slot_place]
      if ((not(attribute is None))):
        checked_bool = GeneralMethods.checkAttributeAndEntity(organization, Constants.organization, attribute, value_gpe)
      else:
        checked_bool = GeneralMethods.checkEntity(organization, Constants.organization, value_gpe)
    elif (intent == "questionsYesNoOrganization_connection_to_RELIGION"):
      if ((not(attribute is None))):
        checked_bool = GeneralMethods.checkAttributeAndEntity(organization, Constants.organization, attribute, value_religion)
      else:
        checked_bool = GeneralMethods.checkEntity(organization, Constants.organization, value_religion)
    else: 
        dispatcher.utter_message(template="utter_ask_rephrase")
        return
    # Ausgabe ob die gewuenschte Entitaet am Objekt vorhanden ist oder nicht
    if (checked_bool == True):
      dispatcher.utter_message(text=f"Yes")
    else: 
      dispatcher.utter_message(text=f"No")