from rasa_sdk.executor import CollectingDispatcher
from actions.db_call import DbCall
from actions.constants import Constants


class GeneralMethods():

  def liste_ausgeben(liste) -> str:
    """
    Methode zum ausgeben einer Liste in einer Zeile
    """
    list_str = ""
    while len(liste) > 1:
        value = liste[0]
        list_str = list_str + value + ", "
        liste.remove(value)
    list_str = list_str + liste[0]
    return list_str

  def linkErstellen(dispatcher: CollectingDispatcher, node_titel) -> str:
    """
    In dieser Methode wird mit Hilfe des node_title der Link zu der Seite der Person erstellt
    """
    node_titel = GeneralMethods.deleteMarks(node_titel)
    node = node_titel.split()
    link = ""
    if (len(node) == 0):
      return link
    while len(node) > 1:
      link = link + node[0] + "-"
      node.remove(node[0])
    link = link + node[0]
    return link

  def deleteMarks(word) -> str:
    """
    Methode zum entfernen von Satzzeichen
    """
    word = word.replace(".","")
    word = word.replace(",","")
    word = word.replace("/","")
    return word

  def checkAttributeAndEntity(object, object_type, attribute_to_check, entity_to_check) -> bool:
      """
      Prueft ob zu einem mitgegebenem Attribut eine mitgegebenem Entitaet vorhanden an dem Objekt vorhanden ist
      """
      answer = DbCall.searchForEntityRelationship(object, object_type)
      for x in answer[Constants.entities_relation]:
        if (attribute_to_check == Constants.headquarter):
            if (x[Constants.relationship] in Constants.headquarter_attribute):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        elif (attribute_to_check == Constants.member):
            if (x[Constants.relationship] in Constants.members):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        elif (attribute_to_check == Constants.residences):
            if (x[Constants.relationship] in Constants.residence_attribute):
              if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
                return true
        else:
          if (x[Constants.relationship] == attribute_to_check):
            if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
              return True
      return False

  def checkEntity(object, object_type, entity_to_check) -> bool:
    """
    Prueft ob zu einem mitgegebenem Objekt eine bestimmte Entitaet vorhanden ist
    """
    answer = DbCall.searchForEntityRelationship(object, object_type)
    checked = False
    if (object_type == Constants.person):
      root_nodes = answer[Constants.root_nodes]
      node_title = ""
      for x in root_nodes: 
        node_checked = GeneralMethods.findeRichtigenKnoten(object, x[Constants.node_title])
        if (node_checked == True):
            entities = DbCall.searchForEntitesFromTheNode(x[Constants.node_id])
            for x in entities:
                if (x[Constants.ent_text] == entity_to_check):
                    return True
    if (checked == False):
      for x in answer[Constants.entities_relation]:
        if((x[Constants.ent_text] == entity_to_check) | (x[Constants.ent2_text] == entity_to_check)):
          return True
    return False

  def findeRichtigenKnoten(name, node_title) -> bool:
      substrings = name.split()
      for x in substrings:
        if (not(x in node_title)):
          return False
      return True

