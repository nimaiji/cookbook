# 🍳 Cooking Assistant Bot 
This project aims to utilize computer vision models like YOLO within a Rasa bot to create an experience for users to obtain their desired recipes. It is runnable on CPU. Also, it is accessible in a [discord server]('https://discord.gg/ttBuk39J'). Feel free to join and test the bot.

## Running as a dicord Bot

Use the following instructions to run the bot as a discord bot in three different terminals:

Terminal 1(running discord client):
```bash
export DISCORD_TOKEN=<Dicord Bot Token>
python3 run discord_bot.py
```

Terminal 2(train the new version of rasa model, and running the server):
```bash
rasa train
rasa run --enable-api --credentials credentials.yml --cors "*"
```

Terminal 3(running actions server):
```bash
rasa run actions
```

## Customizing vision model
In discord_bot.py you can change the vision part of the application. It uses Roboflow APIs to integrate with vision models. 

You can change it to your custom model:
```python
rf = Roboflow(api_key="API_KEY")
project = rf.workspace().project("MODEL_PREFIX")
model = project.version('VERSION_CODE').model
```

## Customizing Recipes
You can also change the list of recipes. You don't to struggle with the suggestions or handling the instructions. In assets > modified_data.csv, you can find recipes and instructions. You can modify the file as you want. You can use other csv files, you just need to have three columns, including recipe, instructions, ingredients.



