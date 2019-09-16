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

# Get AIRFLOW project details.
airflow = jira.project('AIRFLOW')

# Save AIRFLOW project details.
with open('data/airflow_data.json', 'w') as f:
    json.dump({'airflow': airflow.raw}, f, indent=2)

# Get all AIRFLOW issues.
airflow_issues = jira.search_issues('project=AIRFLOW', maxResults=10000, json_result=True)

# Save AIRFLOW issues to JSON file.
with open('data/airflow_issues.json', 'w') as f:
    json.dump({'issues': airflow_issues['issues']}, f, indent=2)
