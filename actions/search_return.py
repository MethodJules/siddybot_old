from typing import Any, Text, Dict, List
#

class Search_return:
    successfull = False
    events = []

    def __init__(self, successfull:bool, events=[]) -> Any:
      self.successfull = successfull
      self.events = events
      return self

    def set_successfull(self, successfull:bool):
      self.successfull = successfull

    def set_events(self, events):
      self.events = events