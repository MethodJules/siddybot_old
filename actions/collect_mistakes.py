from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from actions.constants import Constants
#import base64,cv2

# Action zu Setzen des Slots fuer das Alter des Anwenders
class CollectMistakesAction(Action):

  def name(self) -> Text:
      """
      Name der Action
      """
      return "action_collect_mistakes"

  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[EventType]:
      """
        Methode zu sammeln aller erkannten Intents, welche als nicht hilfreich 
        eingestuft wurden.
        Sie speichert diese in dem Slot "mistaktes"
      """
      print("action_collect_mistakes")
      mistake = tracker.get_slot("latest_question")
      print(tracker.get_slot("latest_question"))
      mistakes = tracker.get_slot("mistakes") + mistake + " ,"
      print(mistakes)
      return [SlotSet("mistakes",mistakes)]