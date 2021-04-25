from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

# Action zum setzen wie hoch ein Anwender sein Wissen ueber das Thema der Webseite einschaetzt
class SetUserToldWithChatbotAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_set_user_told_with_chatbot"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      """
      Setzt den Slot fuer den Wert des Expertenwissens des Anwenders
      """
      print("action_set_user_told_with_chatbot")
      intent = tracker.get_intent_of_latest_message()
      print(intent)
      if (intent == "agree"):
           return [SlotSet("user_speaked_with_chatbot", True)]
      elif (intent == "denied"):
           return [SlotSet("user_speaked_with_chatbot", False)]