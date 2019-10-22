from sklearn.externals import joblib

from lime.lime_text import LimeTextExplainer
from ortools.graph import pywrapgraph

def load_object_from_pickle(path):
    return joblib.load(path)

def pickle_object(filename, object):
    joblib.dump(object, filename)

def analyze_selected_examples(index, issues_df, classifier, count_vectorizer, explainer):
    print(index)
    print('Real selected label: %s' % issues_df.iloc[index]['class'])
    print('Probabilities of each label: %s' % classifier.predict_proba(count_vectorizer.transform([issues_df.iloc[index]['text']])))
    exp = explainer.explain(issues_df.iloc[index]['text'], classifier)
    exp.show_in_notebook()
    #exp.save_to_file('example_explanations/%s.html' % (index))
    print(issues_df.iloc[index]['text'])
    return exp

"""def assign_employees_to_issues(selected_example_indeces, relevance_of_each_employee_per_issue_percentage, unique_person_names, ignored_values):
    def create_data_array():
        cost = relevance_of_each_employee_per_issue_percentage
        inverse_cost = [[100 - c for c in row] for row in cost]

        # print(cost)
        # print(inverse_cost)
        return inverse_cost

    cost = create_data_array()
    rows = len(cost)
    cols = len(cost[0])

    assignment = pywrapgraph.LinearSumAssignment()
    for worker in range(rows):
      for task in range(cols):
        #if cost[worker][task] != 100:
        #print('cost##')
        #print(cost[worker][task])
        assignment.AddArcWithCost(worker, task, cost[worker][task])
    solve_status = assignment.Solve()
    if solve_status == assignment.OPTIMAL:
      total_relevance = 0
      for i in range(0, assignment.NumNodes()):
        if ignored_values[i][assignment.RightMate(i)] == 'IGNORE':
          continue
        relevance = relevance_of_each_employee_per_issue_percentage[i][assignment.RightMate(i)]
        total_relevance += relevance
        print('Employee %s (index:%s) is assigned to issue %s.  Relevance = %d' % (
              unique_person_names[i],
              i,
              selected_example_indeces[assignment.RightMate(i)],
              relevance))
      print('Total relevance = ', total_relevance)
    elif solve_status == assignment.INFEASIBLE:
      print('No assignment is possible.')
    elif solve_status == assignment.POSSIBLE_OVERFLOW:
      print('Some input costs are too large and may cause an integer overflow.')
"""

from scipy.optimize import linear_sum_assignment
import numpy as np

def assign_employees_to_issues(selected_example_indeces, relevance_of_each_employee_per_issue_percentage, unique_person_names):
    def create_data_array():
        cost = relevance_of_each_employee_per_issue_percentage
        inverse_cost = [[100 - c for c in row] for row in cost]

        return inverse_cost

    print('Relevance of each employee per issue:')
    relevance_of_each_employee_per_issue_percentage = np.array(relevance_of_each_employee_per_issue_percentage)
    print(relevance_of_each_employee_per_issue_percentage)
    cost = create_data_array()
    cost = np.array(cost)
    workers_ind, task_ind = linear_sum_assignment(cost)
    for i in range(len(selected_example_indeces)):
        print('Employee %s is assigned to task %s (cell position: [%s, %s]) with relevance %s' % (unique_person_names[workers_ind[i]], selected_example_indeces[task_ind[i]], workers_ind[i], task_ind[i], relevance_of_each_employee_per_issue_percentage[workers_ind[i], task_ind[i]]))

    print('Total relevance: %s' % relevance_of_each_employee_per_issue_percentage[workers_ind, task_ind].sum())


class TextClassificationExplainer(object):
    def __init__(self, class_names, count_vectorizer):
        self.__class_name = class_names
        # Text Explainer for explaining the selected examples.
        # Reference: https://arxiv.org/abs/1602.04938
        # The Explanations help us to check the reliability and validity of the trained machine learning model.
        # The Explanations confirm that the model chooses the right label/class for the right reason (e.g. meaningful words/features).
        self.__explainer = LimeTextExplainer(class_names=class_names)
        self.__count_vectorizer = count_vectorizer

    def explain(self, text, classifier, top_labels=4):
        return self.__explainer.explain_instance(text, lambda x: classifier.predict_proba(self.__count_vectorizer.transform(x)), top_labels=top_labels)

    def explain_in_notebook(self, text, classifier, top_labels=4):
        explanation = self.explain(text, classifier, top_labels)
        explanation.show_in_notebook()
        return explanation

    def explanation_save_to_html_file(self, path, explanation):
        explanation.save_to_file(path)

def get_relevance_of_each_employee_per_issue_percentage(classifier, count_vectorizer, issues_df, selected_example_indeces):
    # Row == employee.
    # Column == issue.
    # Transpose a list code: list(map(list, zip(*l)))
    relevance_of_each_employee_per_issue = list(map(list, zip(*[
        list(classifier.predict_proba(count_vectorizer.transform([issues_df.iloc[i]['text']]))[0]) for i in selected_example_indeces
    ])))
    relevance_of_each_employee_per_issue_percentage = [[int(round(c*100)) for c in row] for row in relevance_of_each_employee_per_issue]
    #print('Relevance of each employee per issue:')
    #for row in relevance_of_each_employee_per_issue_percentage:
    #    print(row)
    return relevance_of_each_employee_per_issue_percentage

def explain_in_notebook_verbose(index, classifier, explainer, issues_df, count_vectorizer, top_labels=4):
    print('Real selected label: %s' % issues_df.iloc[index]['class'])
    print('Probabilities of each label: %s' % classifier.predict_proba(count_vectorizer.transform([issues_df.iloc[index]['text']])))
    explanation = explainer.explain_in_notebook(issues_df.iloc[index]['text'], classifier, top_labels)
    return explanation