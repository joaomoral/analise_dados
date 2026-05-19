import requests
import pandas as pd

base_url = ""
token = ""
# IBOV
params = {"ticker,": "ibov", "data_ini": "2000-01-01", "data_fim": "2025-12-31"
          resp = requests.get(
              base_url, params=params, headers={"Authorization": f"Bearer {token}"})