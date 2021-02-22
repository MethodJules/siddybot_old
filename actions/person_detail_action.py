from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
#import base64,cv2

class PersoDetailAction(Action):

#  def __init__(self):
#  graph_database = GraphDatabase()

#    def run(self, dispatcher: CollectingDispatcher,
#        tracker: Tracker,
#        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#        dispatcher.utter_message(
#            text=f"person_detail_action"

 #       )
 #       return[]


  def name(self) -> Text:
      return "action_person_detail"

  app=Flask(__name__)
  output=[]#("message stark","hi")]
  @app.route("/get-entities-relations-by-entity", methods=['POST'])
  def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      print("start der action")
      entity_person = tracker.get_slot('person')
      dispatcher.utter_message(text=f"Abfrage zu "+ entity_person)
      abfrage_attribute = tracker.get_slot('attribute')
    #  try:
      dispatcher.utter_message(text=f"Abzufragenes Attribute " + abfrage_attribute)
      query = '{"ent_text":"'+entity_person+'","ent_ner":"PERSON"}'
#      query1 = '{"filter":[{"node_type":"'+entity_person+'"}]}'
#      search_request1 = json.loads(query1, encoding="utf-8")
#      answer1 = requests.post('http://semanticsearch.x-navi.de/get-nodes-by-filter', search_request1)
#      print(answer1.text)
      search_request = json.loads(query, encoding="utf-8")
      answer = requests.post('http://semanticsearch.x-navi.de/get-entities-relations-by-entity',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      print(answer["result"])
      results = answer["result"]
      print(results)
      entities = results["entities_relations"]
      print(entities)
      for x in entities:
        print(x)
        if(x["rel"] == abfrage_attribute):
          dispatcher.utter_message(text=f""+x["ent2_text"])
          break
 #     except: 
 #         dispatcher.utter_message(text=f"Das war wohl nicht so gut")
 # @app.route('/get-entities',methods=["GET"])
 # @app.route("/get-entities-relations-by-entity", methods=['POST'])
 # def run(self, dispatcher: CollectingDispatcher,
 #       tracker: Tracker,
 #       domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
 #     print("hier wir sind in der Abfrage Action")
 #     result=list(request.form.values())[0]
 #     entity_person = tracker.get_slot('person')
 #     dispatcher.utter_message(text=f"" + entity_person)
 #     entity_attribute = tracker.get_slot('attribute')
 #     dispatcher.utter_message(text=f"" + entity_attribute)
 #     node = '{"content_type":"PERSON"}'
 #     node = '{"ent_text":"Ruth Barak","ent_ner":"PERSON"}'
 #     json_dict = json.loads(node, encoding="utf-8")
 #     answer = requests.post('http://semanticsearch.x-navi.de/get-nodes-count',json_dict)
 #     answer = requests.get('http://semanticsearch.x-navi.de/')
 #     answer = requests.post('http://semanticsearch.x-navi.de/get-entities-relations-by-entity',json_dict)
 #     response = answer.text
 #     print(response)
 #     dispatcher.utter_message(text=f"lol ")
 # if __name__ == '__main__':
 #   app.run(debug = True)
#      if request.method=="GET":
#          print("Hi hier wird eine Abfrage versucht")
 #     try:
 #         r = requests.get('http://semanticsearch.x-navi.de', json={"message": result})
 #         print(r.json())
 #     except:
 #         print("hierist leider etwas schief gegangen")