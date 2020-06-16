# Craigs List Scrapper

### background
With the prospect of moving I needed a way to look at the different neighborhoods within the dc market area.  With such a large market, and many different areas, I wanted an easy to search them all to see what was where.

## Required imports
```
from bs4 import BeautifulSoup
import json
from requests import get
import numpy as np
import pandas as pd
import csv
from fuzzywuzzy import fuzz as fw
```
### running
1. clone from github
2. using command line go the directory that you cloned the repository to
3. to run the program inside your command line type: `python scrapper.py`
4. your output files will be located in the same directory as `scrapper.py`
### output
running the script will output three files:
- rent_clean.csv: This file shows a clean version of the scrapped data.  This includes a pass through with fuzzy matching to try to match up neighborhood names and combine more together.  And, it pulls out any listings that had a null value for bedrooms and square footage.
- neighborhood_clean_a.csv: This file is just a list of the neighborhood that have been run through the fuzzy matching.  This allows you to see what if any neighborhood could still be better matched.
- neighborhood_analyze.csv: The final file, is the basic information about the different neighborhood.  It includes the max and minimum rental price, as well as the average price.