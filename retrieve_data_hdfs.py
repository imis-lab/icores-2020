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

# Get HDFS project details.
hdfs = jira.project('HDFS')

# Save HDFS project details.
with open('data/hdfs_data.json', 'w') as f:
    json.dump({'hdfs': hdfs.raw}, f, indent=2)

# Get all HDFS issues.
hdfs_issues = jira.search_issues('project=HDFS', maxResults=10000, json_result=True)

# Save HDFS issues to JSON file.
with open('data/hdfs_issues.json', 'w') as f:
    json.dump({'issues': hdfs_issues['issues']}, f, indent=2)
