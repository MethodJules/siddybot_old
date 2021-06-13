from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.constants import Constants
from rasa_sdk.events import SlotSet, EventType
#import base64,cv2

# Action zur Ausgabe ob ein Anwender schonmal mit einem Bot gesprochen hat
class UtterUserSpeakedWithChatbotAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_utter_user_speaked_with_chatbot"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
        """
        Methode für die Auswahl der Antwort, ob ein Anwender schonmal mit einem Bot gesprochen hat.
        Bezieht seine Antwort aus den zuvor getätigten Eingaben
        """
        print(tracker.get_slot("user_speaked_with_chatbot"))
        if (tracker.get_slot("user_speaked_with_chatbot") == True):
            dispatcher.utter_message(template="utter_user_speaked_with_bot_before")
        elif (tracker.get_slot("user_speaked_with_chatbot") == False):
            dispatcher.utter_message(template="utter_user_donot_speaked_with_bot_before")
        else: 
            dispatcher.utter_message(template="utter_do_not_know_the_answer")