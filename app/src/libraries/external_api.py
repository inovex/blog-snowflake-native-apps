import requests

BASE_URL = "https://api.edamam.com/api/recipes/v2"
APP_ID  = "<YOUR_API_ID>"
APP_KEY = "<YOUR_API_KEY>"
FIELD_LIST = ["label", "image", "url", "calories", "totalTime"]


def get_random_recipes(excluded: str) -> str:
  excluded_list = excluded.split(", ")
  
  params = {
    "type": "public",
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "excluded": excluded_list,
    "random": "true",
    "field": FIELD_LIST
  }

  headers = {
    "accept": "application/json",
    "Accept-Language": "en"
  }

  response_txt = requests.get(BASE_URL, params=params, headers=headers).text

  return response_txt
