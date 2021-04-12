from typing import Any, Text, Dict, List
#
# Objekt fuer die Rueckgabe von Suchergebnissen
class Search_return:
    # Kennzeichen ob die Suche erfolgreich war
    successfull = False
    # Liste an Events die aus einer Suche resultieren
    events = []

    def __init__(self, successfull:bool, events=[]) -> Any:
      """
      Initialisierung des Objektes
      """
      self.successfull = successfull
      self.events = events
      return self

    def set_successfull(self, successfull:bool):
      """
      Funktion zum setzen des Kennzeichens ob die Suche erfolgreich war
      """
      self.successfull = successfull

    def set_events(self, events):
      """
      Funktion zum setzen von Events 
      """
      self.events = events