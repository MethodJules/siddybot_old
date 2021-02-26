from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from actions.semantic_search_action import SemanticSearchAction
from actions.db_call import DbCall
#import base64,cv2

class CountObjectTypeAction(Action):
  app=Flask(__name__)
  def name(self) -> Text:
      return "action_count_object_type"


  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    print("start action_count_object_type")
    object_type = tracker.get_slot("object_type")
    print(object_type)
    if (not(object_type is None)):
      answer = DbCall.searchNodeCount(object_type)
      count = answer[0]
      dispatcher.utter_message(text=f""+str(count["node_count"]))
    else: 
      dispatcher.utter_message(text=f"Please tell me from which Object you want to know the count. Here are some examples:")
      dispatcher.utter_message(text=f"City, Person, Religion, organizations, title...")
