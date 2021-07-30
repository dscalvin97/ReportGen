import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from generatorClasses import Student, TestResults
import traceback
from PIL import Image


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    print(os.path.join(base_path, relative_path))

    return os.path.join(base_path, relative_path)


def removeFile(path):
    if os.path.exists(path):
        os.remove(path)


def getReportData(data_file, profile_imgs_path, test_subject_name=""):
    if not os.path.isfile(data_file):
        return 'There was an issue with the Excel path, please check the path and try again'
    if not os.path.isdir(profile_imgs_path):
        return 'The selected folder path does not exist, please check the path and try again'
    elif len(os.listdir(profile_imgs_path)) == 0:
        return 'The selected folder is empty, please select a valid folder and try again'

    profile_imgs_path = os.path.join(profile_imgs_path, '')

    # get excel sheet
    workbook = pd.ExcelFile(data_file)

    # global variables
    sheet_cols = []
    test_data = TestResults()

    # iterate through all sheets in workbook
    for sheet_name in workbook.sheet_names:
        worksheet_df = pd.read_excel(workbook, sheet_name=sheet_name, header=1)

        # ignore if sheet empty
        if len(worksheet_df.values) == 0:
            continue

        sheet_cols = list(worksheet_df.columns)

        # get student registration numbers
        registration_numbers = worksheet_df[sheet_cols[5]].unique()

        # iterate for every student and store details
        for registration_number in registration_numbers:
            student_details = worksheet_df[
                worksheet_df[sheet_cols[5]] == registration_number
            ]

            question_details = {}
            test_data.question_count = student_details.shape[0]

            # Iterate through each question
            for question_idx in range(test_data.question_count):
                question_details[student_details.iloc[question_idx, 13]] = list(
                    student_details.iloc[question_idx, 14:19]
                )

            # get total score by score category
            test_data.q_score_categories = list(
                student_details.iloc[:, 17].unique()
            )

            for category_idx in range(len(test_data.q_score_categories)):
                test_data.q_score_categories[category_idx] = len([
                    x[4]
                    for x in question_details.values()
                    if x[3] == test_data.q_score_categories[category_idx] and x[2] == "Correct"
                ])

            outcome_col = list(student_details.iloc[:, 16])
            if len(test_data.q_attempt_global_avg_lst) == 0:
                test_data.q_attempt_global_avg_lst = [
                    1 if x != 'Unattempted' else 0 for x in outcome_col
                ]
            else:
                test_data.q_attempt_global_avg_lst = [
                    test_data.q_attempt_global_avg_lst[x] + 1 if outcome_col[x] != 'Unattempted' else test_data.q_attempt_global_avg_lst[x] for x in range(len(outcome_col))
                ]

            if len(test_data.q_correct_global_avg_lst) == 0:
                test_data.q_correct_global_avg_lst = [
                    1 if x == 'Correct' and x != 'Unattempted' else 0 for x in outcome_col
                ]
            else:
                test_data.q_correct_global_avg_lst = [
                    test_data.q_correct_global_avg_lst[x] + 1 if outcome_col[x] == 'Correct' and outcome_col[x] != "Unattempted" else test_data.q_correct_global_avg_lst[x] for x in range(len(outcome_col))
                ]

            tmp_img = Image.open(os.path.join(
                profile_imgs_path, student_details[sheet_cols[4]].iat[0] + ".png"))
            profile_path = \
                './' + student_details[sheet_cols[4]].iat[0] + ".png"
            tmp_img = tmp_img.save(resource_path(profile_path))

            student_fname = student_details[sheet_cols[2]].iat[0]
            test_data.students.append(Student(
                student_fname,
                student_details[sheet_cols[3]].iat[0],
                student_details[sheet_cols[9]].iat[0].strftime(
                    "%d-%b %Y"),
                student_details[sheet_cols[8]].iat[0],
                student_details[sheet_cols[10]].iat[0],
                student_details[sheet_cols[12]].iat[0],
                student_details[sheet_cols[6]].iat[0],
                registration_number,
                student_details[sheet_cols[7]].iat[0],
                test_subject_name,
                student_details[sheet_cols[-2]].sum(),
                student_details[sheet_cols[11]].iat[0],
                student_details[sheet_cols[-1]].iat[0],
                profile_path,
                student_details[sheet_cols[1]].iat[0],
                student_details[sheet_cols[-3]].sum(),
                len([x for x in question_details.values() if x[2] != "Unattempted"]),
                len([x for x in question_details.values() if x[2] == "Correct"]),
                test_data.q_score_categories,
                question_details
            ))

    # update test_data global values
    test_data.update_student_count()
    test_data.update_global_averages()
    return test_data


# def generateGraphs(student, test_data):
def getReportPdfs(student, test_data, output_directory):

    output_directory = os.path.join(output_directory, '')

    graph_size = 2.5

    # generate student graph file names
    chart_img_names = [
        './' + student.fname + '_' + str(x) + '.png' for x in range(5)
    ]

    # graph 1
    plt.figure(figsize=[graph_size, graph_size])

    plt.bar(
        ['Total\nAttempts', 'Global Avg.'],
        [student.total_attempts, test_data.q_attempts_global_avg]
    )
    plt.savefig(resource_path(chart_img_names[0]), bbox_inches='tight')

    # graph 2
    plt.figure(figsize=[graph_size, graph_size])
    data1 = [
        student.correct_attempts,
        student.total_attempts - student.correct_attempts
    ]
    data2 = [
        test_data.q_correct_global_avg,
        test_data.q_incorrect_global_avg
    ]
    bar_width = 0.3
    plt.bar(np.arange(len(data1)) - (bar_width*0.5), data1, width=bar_width,
            tick_label=['Correct\nAttempts', 'Incorrect\nAttempts'])
    plt.bar(np.arange(len(data2)) + (bar_width*0.5), data2, width=bar_width)
    plt.legend(
        [student.fname, 'Global Avg.'], labelspacing=0.1, fontsize='x-small'
    )
    plt.savefig(resource_path(chart_img_names[1]), bbox_inches='tight')

    # graph 3
    plt.figure(figsize=[graph_size*2.5, graph_size*0.75])
    data1 = test_data.q_score_categories
    data2 = test_data.q_category_global_avg
    plt.bar(np.arange(len(data1)), data1, width=bar_width,
            tick_label=['2-mark\nquestions', '3-mark\nquestions', '5-mark\nquestions'])
    plt.bar(np.arange(len(data2)) + bar_width, data2, width=bar_width)
    plt.legend(
        [student.fname, 'Global Avg.'], labelspacing=0.1, fontsize='x-small'
    )
    plt.ylabel('Correct answer\ncount')
    plt.ylim
    plt.savefig(resource_path(chart_img_names[2]), bbox_inches='tight')

    # graph 4
    data1 = [
        1 if x[2] != "Unattempted" else 0 for x in student.question_details.values()
    ]
    data2 = test_data.q_attempt_global_avg_lst.copy()
    labels = list(student.question_details.keys())

    num_vars = len(labels)
    angles = np.linspace(0, 2*np.pi, num_vars, endpoint=False).tolist()
    data1 += data1[:1]
    data2 += data2[:1]
    angles += angles[:1]
    labels += labels[:1]
    ax = plt.subplots(
        figsize=[graph_size, graph_size],
        subplot_kw=dict(polar=True)
    )[1]
    ax.plot(angles, data1, ',-', linewidth=1.5)
    ax.fill(angles, data1, alpha=0.2)
    ax.plot(angles, data2, '--', linewidth=1.25)
    ax.fill(angles, data2, alpha=0.6)
    ax.set(yticklabels=[])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles), labels)
    ax.set_ylim(-0.2, 1.2)
    ax.legend(
        [student.fname, 'Global Avg.'], loc=(0.9, 1.0), labelspacing=0.1, fontsize='x-small'
    )

    plt.savefig(resource_path(chart_img_names[3]), bbox_inches='tight')

    # graph 5
    data1 = [
        1 if x[2] == "Correct" and x[2] != "Unattempted" else 0 for x in student.question_details.values()
    ]
    data2 = test_data.q_correct_global_avg_lst.copy()
    labels = list(student.question_details.keys())

    num_vars = len(labels)
    angles = np.linspace(0, 2*np.pi, num_vars, endpoint=False).tolist()
    data1 += data1[:1]
    data2 += data2[:1]
    angles += angles[:1]
    labels += labels[:1]
    ax = plt.subplots(
        figsize=[graph_size, graph_size],
        subplot_kw=dict(polar=True)
    )[1]
    ax.plot(angles, data1, ',-', linewidth=1.5)
    ax.fill(angles, data1, alpha=0.2)
    ax.plot(angles, data2, '--', linewidth=1.25)
    ax.fill(angles, data2, alpha=0.6)
    ax.set(yticklabels=[])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles), labels)
    ax.set_ylim(-0.2, 1.2)
    ax.legend(
        [student.fname, 'Global Avg.'], loc=(0.9, 1.0), labelspacing=0.1, fontsize='x-small'
    )

    plt.savefig(resource_path(chart_img_names[4]), bbox_inches='tight')
    plt.close('all')

    env = Environment(loader=FileSystemLoader(resource_path(".")))
    try:
        template = env.get_template("./report_template.html")
    except Exception as e:
        return 'An Error occurred:\n' + repr(e) + '\n' + traceback.format_exc()

    template_var = student.get_student_template_var()

    # add global comparison graphs
    template_var['total_attempt_barchart'] = chart_img_names[0]
    template_var['total_attempt_accuracy_barchart'] = chart_img_names[1]
    template_var['score_category_perf_linechart'] = chart_img_names[2]
    template_var['test_attempt_spiderchart'] = chart_img_names[3]
    template_var['test_accuracy_spiderchart'] = chart_img_names[4]

    # print(template_var['student_profile_img'])

    html_out = template.render(template_var)

    # save .html file - for debugging purposes only
    # with open(student.fname + ".html", 'w+') as debug_html:
    #     debug_html.write(html_out)

    output_path = os.path.join(
        output_directory, str(student.registration_number) + "_" + student.fname + ".pdf")
    HTML(
        string=html_out,
        base_url=resource_path("")
    ).write_pdf(output_path, stylesheets=[resource_path('report_template_styling.css')])

    # print('Generated report for ' + student.fname)

    removeFile(resource_path(chart_img_names[0]))
    removeFile(resource_path(chart_img_names[1]))
    removeFile(resource_path(chart_img_names[2]))
    removeFile(resource_path(chart_img_names[3]))
    removeFile(resource_path(chart_img_names[4]))
    removeFile(resource_path(template_var['student_profile_img']))
    return 0


# td = getReportData("Dummy Data.xlsx", "Pics for assignment/", "History")

# for student in td.students:
#     getReportPdfs(student, td, "./")     # Testing call
