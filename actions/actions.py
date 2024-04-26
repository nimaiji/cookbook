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

# Deprecated
class ActionProvideRecipe(Action):
    def name(self) -> Text:
        return "action_provide_recipe"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dish = tracker.get_slot("dish")

        if dish:
            print("Current Dish: ", dish)
            # Call Spoonacular API to get recipe data
              
            # This returns recipe information based on recipe ID
            recipe_id = 716429
            api_key = "dfc754527d234b609c4c2597e0f2e04b"
            endpoint = f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=false&apiKey={api_key}"
            response = requests.get(endpoint)
            print(f"exported dish: {len(dish)}")
            if response.status_code == 200:
                data = response.json()

                products = data.get("products", [])

                if products:
                    ingredients = []
                    # Extract information from the first product
                    for i in range(len(products)):
                        ingredients.append(products[i].get("title", "Unknown"))

                    ingredients_text = f""
                    for i in range(len(ingredients)):
                        ingredients_text += (ingredients[i] + "\n")

                    # Construct the response message
                    response_message = f"Here's a recipe for {dish}: {ingredients_text}\n"

                    # Send the response to the user
                    dispatcher.utter_message(text=response_message)
                else:
                    dispatcher.utter_message(text="Sorry, I couldn't find a recipe for that dish 111.")
            else:
                dispatcher.utter_message(
                    text="Sorry, there was an error fetching the recipe. Please try again later.")
        else:
            dispatcher.utter_message(
                text="Sorry, I didn't catch the dish name. Can you please specify the dish again?")
        return []

# Deprecated
class ActionProvideRecipeUsingId(Action):
    def name(self) -> Text:
        return "action_provide_recipe_using_id"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the recipe ID from the tracker
        recipe_id = tracker.get_slot("dish_id")
        print("Extracted recipe id: ", recipe_id)

        if recipe_id:
            # Call Spoonacular API to get recipe instructions based on recipe ID
            api_key = "dfc754527d234b609c4c2597e0f2e04b"
            endpoint = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?stepBreakdown=true&apiKey={api_key}"
            response = requests.get(endpoint)

            if response.status_code == 200:
                data = response.json()
                instructions = []
                if data:
                    for section in data:
                        for step in section.get("steps", []):
                            step_number = step.get("number")
                            instruction = step.get("step")
                            instructions.append(f"Step {step_number}: {instruction}")

                    # Construct the response message
                    response_message = "\n".join(instructions)
                else:
                    response_message = "Unfortunately, we do not have detailed instructions for this recipe."
                # Send the response to the user
                dispatcher.utter_message(text=response_message)
            else:
                dispatcher.utter_message(
                    text="Sorry, there was an error fetching the recipe instructions. Please try again later.")
        else:
            dispatcher.utter_message(
                text="Sorry, I didn't catch the recipe ID. Can you please provide the recipe ID again?")

        return []


class ActionProvideIngredients(Action):
    def name(self) -> Text:
        return "action_provide_ingredients"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_provide_ingredients")
        return []


class ActionProvideCookingTime(Action):
    def name(self) -> Text:
        return "action_provide_cooking_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_provide_cooking_time")
        return []


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

        # Define regular expression pattern to extract ingredients
        pattern = r'(?i)(?:Here are the ingredients:|I have the following ingredients: |My ingredients include:|Ingredients:|I have:|I have |Check out my ingredients:|My list of ingredients is:|Here\'s what I\'m working with:|This is my ingredient list:|These are the ingredients I have:|Here\'s what I\'ve got:|Take a look at my ingredients:)\s*(.*)'
        match = re.search(pattern, message)

        if match:
            # Extract the ingredients text
            ingredients_text = match.group(1).strip()

            # Split the ingredients text into individual ingredients
            ingredients_list = re.split(r',|;|and|\band\b', ingredients_text)

            # Remove empty strings and leading/trailing whitespace
            ingredients_list = [ingredient.strip() for ingredient in ingredients_list if ingredient.strip()]
            ingredients = ingredients_list
            # Send a message back with the extracted ingredients
            if ingredients_list:
                dispatcher.utter_message(text=f"Received ingredients: {', '.join(ingredients_list)}\nWould you like to change any ingredients?")
            else:
                dispatcher.utter_message(text="No ingredients found.")
        else:
            dispatcher.utter_message(text="No ingredients found.")

        return []


class HandleIngredientChange(Action):
    def name(self) -> Text:
        return "action_handle_ingredient_change"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global ingredients  # Declare the variable as global
        # Get the user's message
        message = tracker.latest_message.get("text", "")

        # Extract the ingredient change request
        ingredient_change = self.extract_ingredient_change(message)

        if ingredient_change:
            # Apply the ingredient change to the global variable or any other appropriate data structure
            # global ingredients
            ingredients = self.apply_ingredient_change(ingredient_change, ingredients)
            # Inform the user about the successful ingredient change
            print(f"Current List of ingredients: {ingredients}")
            print(f"Current List of ingredients: {ingredient_change}")

            dispatcher.utter_message(text=f"The ingredient change was successfully applied. Your current ingredients are: {', '.join(ingredients)}\nIs the updated list okay?")
        else:
            dispatcher.utter_message(text="No ingredient change was detected.")

        return []

    def extract_ingredient_change(self, message: Text) -> Dict[Text, Text]:
        # Define a regular expression pattern to extract ingredient change requests
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
        dispatcher.utter_message(text=f"Your recipe is being generated.\n\n ***Functionality .{ingredients} and {dish}")


        result = suggest_recipe(ingredients)[0][1]
        print('RESULT:')
        print(result)
        response_message = """
        This recipe is the closest match to the ingredients provided.
        
        Name: {name}
        This is the instruction:
        {instruction}
        
        """
        final_text = response_message.format(instruction=result['instructions'], name=result['recipe_name'])
        print(final_text)

        dispatcher.utter_message(text=final_text)
        return []
