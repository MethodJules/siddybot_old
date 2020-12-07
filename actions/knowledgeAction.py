from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk import utils

class MyKnowledgeBaseAction(ActionQueryKnowledgeBase):
    def __init__(self):
        knowledge_base = InMemoryKnowledgeBase("data_person.json")

        # overwrite the representation function of the hotel object
        # by default the representation function is just the name of the object
#        knowledge_base.set_representation_function_of_object(
#            "hotel", lambda obj: obj["name"] + " (" + obj["city"] + ")"
#        )
        knowledge_base.set_representation_function_of_object(
            "person", lambda obj: obj["title"] + " " + obj["name"] + " (" + obj["date_of_birth"] + " - " + obj["date_of_death"] + ")"
        )

        #knowledge_base.set_representation_function_of_object(
        #    "domicile", lambda obj: obj["place"] + " (" + obj["start"] +  " - " + obj["end"] + ")"
        #)


        super().__init__(knowledge_base)

    async def utter_objects(self, dispatcher, object_type, objects):
        """
        Utters a response to the user that lists all found objects.
        Args:
            dispatcher: the dispatcher
            object_type: the object type
            objects: the list of objects
        """
        if objects:
            dispatcher.utter_message(
                text=f"The following '{object_type}' I have in my list:"
            )

            repr_function = await utils.call_potential_coroutine(
                self.knowledge_base.get_representation_function_of_object(object_type)
            )

            for i, obj in enumerate(objects, 1):
                dispatcher.utter_message(text=f"{i}: {repr_function(obj)}")
        else:
            dispatcher.utter_message(
                text=f"I could not find any {object_type}."
            )

    async def utter_attribute_value(self, dispatcher, object_name, attribute_name, attribute_value):
        """
        Utters a response that informs the user about the attribute value of the
        attribute of interest.
        Args:
            dispatcher: the dispatcher
            object_name: the name of the object
            attribute_name: the name of the attribute
            attribute_value: the value of the attribute
        """
        if attribute_value:

            if (attribute_name == "domicile"):
                dispatcher.utter_message(
                    text=f"The domicile of {object_name} were {attribute_value}."
                )
            elif (attribute_name == "biographie"):
                 dispatcher.utter_message(
                    text=f"{attribute_value}"
                )
            else:
                dispatcher.utter_message(
                    text=f"'{object_name}' has the value '{attribute_value}' for attribute '{attribute_name}'."
                )
        else:
            dispatcher.utter_message(
                text=f"Did not find a valid value for attribute '{attribute_name}' for object '{object_name}'."
            )
