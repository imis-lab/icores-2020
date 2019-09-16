# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 19:27:41 2018

@author: nkanak
"""

import json
from jira import JIRA

jira = JIRA('https://issues.apache.org/jira')

# Get all projects.
projects = jira.projects()

# Get SPARK project details.
spark = jira.project('SPARK')

# Save SPARK project details.
with open('data/spark_data.json', 'w') as f:
    json.dump({'spark': spark.raw}, f, indent=2)

# Get all SPARK issues
spark_issues = jira.search_issues('project=SPARK', maxResults=10000, json_result=True)

# Save SPARK issues to JSON file.
with open('data/spark_issues.json', 'w') as f:
    json.dump({'issues': spark_issues['issues']}, f, indent=2)
