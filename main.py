import copy
import json
import datetime
import requests
from zoneinfo import ZoneInfo
from collections import deque

BASEURL = "https://script.google.com/macros/s/AKfycbxYRsb-wCsPa6rbTBF-WACTaKdBdGolj33s42Eyq6ajKomV85p4Dj6wkCe-2JDymIW6/exec?token=4eMzpuVNHVWPCTz"

now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
year: str = now.strftime("%Y")
month: str = now.strftime("%m")
day: str = now.strftime("%d")
today: str = now.strftime("%Y-%m-%d")

LIST = deque([
  ("pub", False),
  ("sch_temp", True),
  ("sch", False),
])

def getTodayType() -> str:
  json = requests.get("https://raw.githubusercontent.com/kgi-js-digital-creator/syukujitsu/artifact/syukujitsu.json", timeout=10).json()["body"]
  if today in json or now.weekday() == 6:
    return "holi"
  elif now.weekday() == 5:
    return "sat"
  return "week"
todayType = getTodayType()

def getJson(type: str, isTemp: bool) -> json:
  if isTemp:
    url = BASEURL + f"&md=sch_temp&y={year}&m={month}&d={day}"
  else:
    url = BASEURL + f"&md={type}_{todayType}"

  res = requests.get(url)
  if not res.status_code == 200:
    print(f"Error: {res.status_code} {res.text}")
    return json.loads("{}")
  print(res.text)
  return res.json()

def deep_merge(base: dict, incoming: dict) -> dict:
  result = copy.deepcopy(base)
  for key, value in incoming.items():
    if key not in result:
      result[key] = copy.deepcopy(value)
    elif isinstance(result[key], dict) and isinstance(value, dict):
      result[key] = deep_merge(result[key], value)
    elif isinstance(result[key], list) and isinstance(value, list):
      result[key].extend(copy.deepcopy(value))
  return result

def main() -> dict:
  data = {"update": today}
  while LIST:
    type_name, is_temp = LIST.popleft()
    fetched = getJson(type_name, is_temp)
    data = deep_merge(data, fetched)
  with open("timetable.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

if __name__ == "__main__":
  main()
  
  