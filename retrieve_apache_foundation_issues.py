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

# Get HADOOP project details.
hadoop = jira.project('HADOOP')


# Get all HADOOP issues.
hadoop_issues = jira.search_issues('project=HADOOP', maxResults=10000, json_result=True)

def retrieve_project_data(project_name):
    project = jira.project(project_name)
    return project.raw

def save_project_data_to_json(filename, project_data):
    # Save HADOOP project details.
    with open('hadoop_data.json', 'w') as f:
        json.dump({'data': project_data}, f, indent=2)

def retrieve_issues(project_name, block_size=1000, max_number_of_iterations=None):
    issues = []
    block_num = 0
    number_of_iterations = 0
    while True:
        number_of_iterations += 1
        start_idx = block_num*block_size 
        retrieved_issues = jira.search_issues('project=%s' % (project_name), startAt=start_idx, maxResults=block_size, json_result=True, expand='changelog', fields='summary,assignee,description')
        if len(retrieved_issues['issues']) == 0 or max_number_of_iterations is not None and number_of_iterations >= max_number_of_iterations:
            break
        block_num += 1
        issues += retrieved_issues['issues']

    return issues

def save_issues_to_json(filename, issues):
    # Save HADOOP issues to JSON file.
    with open('hadoop_issues.json', 'w') as f:
        json.dump({'issues': hadoop_issues['issues']}, f, indent=2)
