import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import ast
from sklearn import preprocessing
import numpy as np
from sklearn.preprocessing import normalize
from keras.preprocessing import image
from time import time
from scipy.spatial.distance import cosine, euclidean, hamming
import re

def extract_text_within_quotes(text):
    pattern = r"'(.*?)'"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None

def get_intersection(items, arr):
    count = 0
    for item in items:
        if item in arr:
            count += 1

    return count

df = pd.read_csv("./assets/modified_data.csv")
df = df[['ingredients', 'recipe_name', 'instructions']]
data = df.to_dict()

def suggest_recipe(items):
    res = []
    for index, row in df.iterrows():
        ingredients = [extract_text_within_quotes(i) for i in row['ingredients'][1:-1].split(',')]
        intersection = get_intersection(ingredients, items)
        if len(res) < 5:
            res.append((intersection, row))
        else:
            res = sorted(res, key=lambda x: x[0])
            for index, i in enumerate(res):
                if i[0] < intersection:
                    res[index] = (intersection, row)

    return res

