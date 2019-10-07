# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 19:27:41 2018

@author: nkanak
"""

import csv
import json
import logging

from jira import JIRA

BLOCK_SIZE = 500
# Set this variable to None when the retrieval of all the issues is needed.
MAX_NUMBER_OF_ITERATIONS = None

def read_project_names_from_csv_file(filename='projects.csv'):
    project_names = []
    with open(filename) as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            project_names.append(row['project_name'])
    return project_names

PROJECT_NAMES = read_project_names_from_csv_file()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s \033[35m%(message)s\033[0m', datefmt='[%d/%b/%Y %H:%M:%S]')

class DataReader(object):
    def read_issues_from_json_file(self, filename, keep_only_issues_with_assignee=False):
        with open(filename) as f:
            issues = json.load(f)
        issues = issues['issues']
        if keep_only_issues_with_assignee is True:
            issues = [issue for issue in issues if issue['fields'].get('assignee') is not None]
        return issues

class DataRetriever(object):
    def __init__(self, jira_client, block_size=1000, max_number_of_iterations=None):
        self.__jira_client = jira_client
        self.__block_size = block_size
        self.__max_number_of_iterations = max_number_of_iterations

    def retrieve_project_data(self, project_name):
        logging.info('Retrieve project data for %s' % (project_name))
        # Get X project details.
        project = self.__jira_client.project(project_name)
        return project.raw

    def retrieve_issues(self, project_name):
        logging.info('Retrieve issues for %s project' % (project_name))
        logging.info('Retrieval block size: %s, Max number of iterations: %s' % (self.__block_size, self.__max_number_of_iterations))
        issues = []
        block_num = 0
        number_of_iterations = 0
        while True:
            number_of_iterations += 1
            if self.__max_number_of_iterations is not None and number_of_iterations > self.__max_number_of_iterations:
                break

            logging.debug('%s iteration out of %s' % (number_of_iterations, self.__max_number_of_iterations))
            start_idx = block_num*self.__block_size
            # Get X project issues.
            retrieved_issues = self.__jira_client.search_issues('project=%s' % (project_name), startAt=start_idx, maxResults=self.__block_size, json_result=True, expand='changelog', fields='summary,assignee,description')
            if len(retrieved_issues['issues']) == 0:
                break
            issues += retrieved_issues['issues']

            block_num += 1

        logging.debug('Retrieved total %s unique issues of project %s' % (len(set([issue['key'] for issue in issues])), project_name))
        return issues

class DataWriter(object):
    def __init__(self, indent=2):
        self.__indent = indent

    def save_project_data_to_json(self, filename, project_data):
        logging.info('Write project information to file: %s' % (filename))
        # Save X project details.
        with open(filename, 'w') as f:
            json.dump({'data': project_data}, f, indent=self.__indent)

    def save_issues_to_json(self, filename, issues):
        logging.info('Write project issues to file: %s' % (filename))
        # Save X project issues to JSON file.
        with open(filename, 'w') as f:
            json.dump({'issues': issues}, f, indent=self.__indent)

    # Generate a CSV file for descriptive statistics.
    def save_issues_to_csv(self, filename, issues, keep_only_issues_with_assignee=False):
        logging.info('Write project issues to csv file: %s' % (filename))
        logging.debug('Keep only issues with assignee: %s' % (keep_only_issues_with_assignee))
        fieldnames = ['key', 'summary', 'description', 'assignee']
        with open(filename, 'w') as f:
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
            csv_writer.writeheader()
            for issue in issues:
                if keep_only_issues_with_assignee is True and issue['fields'].get('assignee') is None:
                    continue

                csv_writer.writerow({
                    'key': issue['key'],
                    'summary': issue['fields']['summary'],
                    'description': issue['fields']['description'] if not None else '',
                    'assignee': issue['fields']['assignee']['key'] if issue['fields'].get('assignee') is not None else 'N/A'
                })

if __name__ == '__main__':
    jira = JIRA('https://issues.apache.org/jira')
    all_issues = []
    writer = DataWriter()
    retriever = DataRetriever(jira_client=jira, block_size=BLOCK_SIZE, max_number_of_iterations=MAX_NUMBER_OF_ITERATIONS)
    for project_name in PROJECT_NAMES:
        project_data = retriever.retrieve_project_data(project_name)
        writer.save_project_data_to_json('data/project_data_%s.json' % (project_name), project_data)
        issues = retriever.retrieve_issues(project_name)
        all_issues += issues
        writer.save_issues_to_json('data/issues_%s.json' % (project_name), issues)
        writer.save_issues_to_csv('data/issues_%s.csv' % (project_name), issues, keep_only_issues_with_assignee=False)
    writer.save_issues_to_json('data/all_issues.json', all_issues)
    writer.save_issues_to_csv('data/all_issues.csv', all_issues, keep_only_issues_with_assignee=False)
