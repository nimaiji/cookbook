from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import recipe_generator

# define global variable to store ingredient list
ingredients = []


class ActionUtterGoodbye(Action):
    def name(self) -> Text:
        return "utter_goodbye"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_goodbye")
        return []


class ActionUtterIamabot(Action):
    def name(self) -> Text:
        return "utter_iamabot"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_iamabot")
        return []


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_default")
        return []



class HandleInputMethod(Action):
    def name(self) -> Text:
        return "action_handle_input_method"

    def check_input(self, arr, input_method):
        for item in arr:
            if item in input_method:
                return True
        return False

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global ingredients  # Declare the variable as global

        # Get the value of the input_method slot
        input_method = tracker.get_slot("input_method")

        if input_method:
            input_method = input_method.lower()  # Convert to lowercase for case-insensitive matching

            if self.check_input(['typing', 'text', 'chat'], input_method):
                dispatcher.utter_message(text="Okay, I'm ready to receive your input through text. Please type the ingredients.")
            elif self.check_input(['camera', 'image', 'visual'], input_method):
                dispatcher.utter_message(text="Sure, you can use your camera to capture the ingredients. Please take a photo.")
            else:
                dispatcher.utter_message(text="I'm sorry, I didn't understand how you'd like to provide the ingredients.")

        return []


class ExtractIngredients(Action):
    def name(self) -> Text:
        return "action_extract_ingredients"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global ingredients  # Declare the variable as global
        dish = tracker.get_slot("dish")
        print("This is the dish {}".format(dish))
        # Get the user's message
        message = tracker.latest_message.get("text", "")
        tmp = message.split(":")
        print(tmp)
        if len(tmp) > 1:
            ingredients = [x.strip() for x in tmp[1].split(",")]
        else:
            ingredients = [x.strip() for x in tmp[0].split(",")]

        print(f"Current List of ingredients: {ingredients}")
        if len(ingredients) > 0:
            dispatcher.utter_message(text=f"Received ingredients: {', '.join(ingredients)}\nWould you like to change any ingredients?")
        else:
            dispatcher.utter_message(text="No ingredients found.")

        return []

class HandleIngredientChangeConfirmation(Action):

    def name(self) -> Text:
        return "confirm_ingredient_change"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global ingredients  # Declare the variable as global
        # Get the user's message
        message = tracker.latest_message.get("text", "")

        if 'no' in message.lower():
            dispatcher.utter_message(text="Okay, let's proceed with the current list of ingredients.")
        else:
            dispatcher.utter_message(text="Please provide the ingredient change request in the format '<old> to <new>'.")

        return []


class HandleIngredientChange(Action):
    def name(self) -> Text:
        return "action_handle_ingredient_change"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global ingredients  # Declare the variable as global
        # Get the user's message
        message = tracker.latest_message.get("text", "")
        
        item1 = tracker.get_slot("item1")
        item2 = tracker.get_slot("item2")
        print("Item1: ", item1)
        print("Item2: ", item2)

        # Extract the ingredient change request
        ingredient_change = self.extract_ingredient_change(message)

        if ingredient_change:
            # Apply the ingredient change to the global variable or any other appropriate data structure
            # global ingredients
            ingredients = self.apply_ingredient_change(ingredient_change, ingredients)
            # Inform the user about the successful ingredient change
            print(f"Current List of ingredients: {ingredients}")
            print(f"Current List of ingredients: {ingredient_change}")

            dispatcher.utter_message(text=f"The ingredient change was successfully applied. Your current ingredients are: {', '.join(ingredients)}\nWould you like to make other changes?")
        else:
            dispatcher.utter_message(text="No ingredient change was detected.")

        return []

    def extract_ingredient_change(self, message: Text) -> Dict[Text, Text]:

        pattern = r"(change|switch|replace) (.+?) (for|with) (.+)"
        match = re.search(pattern, message.lower())
        if match:
            old_ingredient = match.group(2).strip().replace("the ", "")
            return {"old_ingredient": old_ingredient, "new_ingredient": match.group(4).strip()}
        else:
            return {}

    def apply_ingredient_change(self, ingredient_change: Dict[Text, Text], ingredients: List[Text]) -> List[Text]:
        # Implement logic to apply the ingredient change to the ingredients list
        old_ingredient = ingredient_change.get("old_ingredient")
        new_ingredient = ingredient_change.get("new_ingredient")
        if old_ingredient in ingredients:
            ingredients.remove(old_ingredient)
            ingredients.append(new_ingredient)
        return ingredients


class ActionGenerateRecipe(Action):
    def name(self) -> Text:
        return "action_generate_recipe"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global ingredients # Specifies the extracted ingredients
        dish = tracker.get_slot("dish") # Specifies the extracted dish
        print(f'ingredients: {ingredients}')
        result = recipe_generator.suggest_recipe(ingredients)[0][1]
        print('RESULT:')
        print(result)
        response_message = """
        This recipe is the closest match to the ingredients provided.
        
        Name: {name}
        
        Ingredients: {original_ingrd}
        {instruction}
        
        """
        final_text = response_message.format(instruction=result['instructions'], name=result['recipe_name'], original_ingrd=result['ingredients'])
        print(final_text)

        dispatcher.utter_message(text=final_text)
        return []
