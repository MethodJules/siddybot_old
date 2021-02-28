from rasa_sdk.executor import CollectingDispatcher

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

  def linkErstellen(dispatcher: CollectingDispatcher, node_titel):
    """
    In dieser Methode wird mit Hilfe des node_title der Link zu der Seite der Person erstellt
    """
    node_titel = GeneralMethods.deleteMarks(node_titel)
    node = node_titel.split()
    link = ""
    while len(node) > 1:
      link = link + node[0] + "-"
      node.remove(node[0])
    link = link + node[0]
    dispatcher.utter_message(text=f"For more informations you can look here:")
    dispatcher.utter_message(text=f"https://www.jigsaw-navi.net/de/content/"+link)

  def deleteMarks(word) -> str:
    """
    Methode zum entfernen von Satzzeichen
    """
    word = word.replace(".","")
    word = word.replace(",","")
    word = word.replace("/","")
    return word