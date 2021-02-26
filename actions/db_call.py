from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from actions.semantic_search_action import SemanticSearchAction
#import base64,cv2

class DbCall():

  app=Flask(__name__)
  @app.route("/get-entities", methods=['POST'])
  def searchForEntitiy(self, object_type) -> Dict[Text, Any]:
      answer = requests.get('https://semanticsearch.x-navi.de/get-entities')
      answer = json.loads(answer.text,encoding="utf-8")
      answer = answer["result"]
      answer = answer["types"]
      return answer

  @app.route("/get-entities-relations-by-entity", methods=['POST'])
  def searchForEntityRelationship(self, name, object_type) -> Dict[Text, Any]:
      query = '{"ent_text":"'+name+'","ent_ner":"'+object_type+'"}'
      search_request = json.loads(query, encoding="utf-8")
      answer = requests.post('https://semanticsearch.x-navi.de/get-entities-relations-by-entity',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      results = answer["result"]
      return results

  @app.route("/get-nodes-count", methods=['POST'])
  def searchNodeCount(object_type) -> Dict[Text, Any]:
      query = '{"content_type":"'+object_type+'"}'
      search_request = json.loads(query, encoding="utf-8")
      answer = requests.post('https://semanticsearch.x-navi.de/get-nodes-count',search_request)
      answer = json.loads(answer.text,encoding="utf-8")
      results = answer["result"]
      return results

