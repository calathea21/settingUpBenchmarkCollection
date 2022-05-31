"""
We used this file once our Qualtrics data collection was complete, to process the collected data. This is included
steps to filter out unusable and non-sensical responses. The grade- and ranking predicitons for each student profile are stored
into a new dataset 'PortuegueseStudentsWithBiasedLabels.xlsx
"""

import pandas as pd
from math import isnan
import numpy as np
import itertools
import collections

block_info_file = "blocks_information.xlsx"
qualtrics_report_file = "qualtrics_01-03.xlsx"

student_to_id = {"Anna":1, 'Sarah': 2, 'Jenny': 3, 'Lisa':4, 'Brian':5, 'Michael': 6, 'David': 7, 'Oliver': 8}
id_to_student = {1: "Anna", 2: "Sarah", 3: "Jenny", 4: "Lisa", 5:"Brian", 6:"Michael", 7:"David", 8:"Oliver"}



#add function to see difference between actual and predicted grade
def add_predictions_to_one_block(block_info, block_id, grade_dict, ranking_dict, stereotype_activation):
    relevant_row_indices = block_info[block_info["BlockID"] == block_id].index

    for relevant_row_index in relevant_row_indices:
        corresponding_student = block_info.loc[relevant_row_index, "name"]
        block_info.loc[relevant_row_index, "PredictedGrade"] = grade_dict[corresponding_student]
        block_info.loc[relevant_row_index, "PredictedRank"] = ranking_dict[corresponding_student]
        block_info.loc[relevant_row_index, "StereotypeActivation"] = stereotype_activation


def add_predictions_to_all_blocks(qualtrics_answers, block_info):
    processed_block_ids = []
    block_info["PredictedGrade"] = ""
    block_info["PredictedRank"] = ""
    block_info["StereotypeActivation"] = ""

    for index, row in qualtrics_answers.iterrows():
        #take the non empty columns
        without_nan = row.dropna().index.tolist()
        block_columns = [block for block in without_nan if block.startswith("Block")]
        block_name = block_columns[0].split("_")[0]
        block_id = int(block_name.split("Block")[1])
        stereotype_activation = row["StereotypeActivation"]
        processed_block_ids.append(block_id)

        grade_dict = {}
        ranking_dict = {}
        for block_column in block_columns:
            student_id = int(block_column.split("_")[1])
            student_name = id_to_student[student_id]
            if block_column.endswith("TEXT"):
                grade_dict[student_name] = row[block_column]
            else:
                ranking_dict[student_name] = row[block_column]

        add_predictions_to_one_block(block_info, block_id, grade_dict, ranking_dict, stereotype_activation)
    return block_info, processed_block_ids



def filter_out_non_participation(data):
    email_adress = data['Q241']
    consent = data['Q242']
    finished = data['Finished']

    no_email_adress = email_adress.index[email_adress=="No (stop participation)"].to_list()
    no_consent = consent.index[consent=="No (stop participation)"].to_list()
    not_finished = finished.index[finished==False].to_list()

    to_drop = set(no_email_adress + no_consent + not_finished)

    data = data.drop(to_drop, axis=0).reset_index(drop=True)
    return data



def filter_short_responses(data):
    duration = data['Duration (in seconds)']
    too_little_time_indices = set(duration.index[duration <= 150])
    print_block_id_of_dropped_rows(data, dropped_rows=too_little_time_indices)
    data = data.drop(too_little_time_indices, axis=0).reset_index(drop=True)
    return data

def print_block_id_of_dropped_rows(data, dropped_rows):
    for index in dropped_rows:
        #take the non empty columns
        without_nan = data.loc[index].dropna().index.tolist()
        block_columns = [block for block in without_nan if block.startswith("Block")]
        block_name = block_columns[0].split("_")[0]
        block_id = int(block_name.split("Block")[1])
        print("Dropped answers given for block id " + str(block_id))
    return


def filter_out_wrong_grade_range(data):
    block_grade_columns = [col for col in data if col.startswith('Block') and col.endswith("TEXT")]

    predicted_grades = data[block_grade_columns]
    number_of_nans_per_row = predicted_grades.isnull().sum(axis=1)

    max_per_row = predicted_grades.max(axis=1)
    max_is_bigger_than_20_rows = max_per_row[max_per_row>20].index.to_list()
    max_is_smaller_than_10_rows = max_per_row[max_per_row<=10].index.to_list()
    more_than_8_non_nans = number_of_nans_per_row[number_of_nans_per_row>848].index.to_list()

    #only_nan_rows = predicted_grades[predicted_grades.isna().all(axis=1)].index.to_list()

    all_dropped_rows = list(itertools.chain(more_than_8_non_nans, max_is_smaller_than_10_rows, max_is_bigger_than_20_rows))
    print_block_id_of_dropped_rows(data, all_dropped_rows)

    data = data.drop(all_dropped_rows, axis=0).reset_index(drop=True)

    return data


def filter_out_wrong_grade_orders(data):
    for index, row in data.iterrows():
        #take the non empty columns
        without_nan = row.dropna().index.tolist()
        grade_columns = [col for col in without_nan if col.startswith("Block") and col.endswith("TEXT")]
        rank_columns = [col for col in without_nan if col.startswith("Block") and not col.endswith("TEXT")]

        predicted_grades = row[grade_columns]
        predicted_grade_rankings = row[rank_columns].array

        ordered_row_according_to_grades = ((predicted_grades * -1).argsort().argsort() + 1).array
        difference_in_ordering = abs(ordered_row_according_to_grades - predicted_grade_rankings)
        if max(difference_in_ordering) >=3:
            print(grade_columns)
            print(index)
    return data


def find_biased_instances(block_info):
    block_info = block_info.replace(r'^\s*$', np.nan, regex=True)
    block_info.dropna(subset=["PredictedGrade"], inplace=True)

    block_info["Predicted_Pass"] = block_info["PredictedGrade"] >= 10
cd 
    boys_data = block_info[block_info["sex"] == 'M']
    print("Number of boys made predictions for: " + str(len(boys_data)))

    discriminated_by_fail_pred_boys = boys_data[(boys_data["Predicted_Pass"] == False) & (boys_data["Pass"] == True)]
    print("Percentage of discriminated by fail prediction boys: " + str(len(discriminated_by_fail_pred_boys)/len(boys_data[boys_data["Pass"] == True])))
    discriminated_by_lowest_ranks_boys = boys_data[(boys_data["PredictedRank"] >= 7) & (boys_data["Pass"] == True)]
    print("Percentage of discriminated by rank boys: " + str(len(discriminated_by_lowest_ranks_boys)/len(boys_data[boys_data["Pass"] == True])))
    favoured_boys = boys_data[(boys_data["Predicted_Pass"] == True) & (boys_data["Pass"] == False)]
    print("Percentage of favoured boys:" + str(len(favoured_boys)/ len(boys_data[boys_data["Pass"] == False])))
    favoured_by_ranking_boys = boys_data[(boys_data["PredictedRank"] < 3) & (boys_data["Pass"] == False)]
    print("Percentage of favoured by ranking boys:" + str(len(favoured_by_ranking_boys) / len(boys_data[boys_data["Pass"] == False])))
    no_change_boys = boys_data[(boys_data["Predicted_Pass"] == boys_data["Pass"])]
    print("Percentage of no change boys:" + str(len(no_change_boys) / len(boys_data)))

    girls_data = block_info[block_info["sex"] == 'F']
    print("Number of girls made predictions for: " + str(len(girls_data)))
    discriminated_girls = girls_data[(girls_data["Predicted_Pass"] == False) & (girls_data["Pass"] == True)]
    print("Percentage of discriminated girls: " + str(len(discriminated_girls)/len(girls_data[girls_data["Pass"] == True])))
    discriminated_by_lowest_ranks_girls = girls_data[(girls_data["PredictedRank"] >= 7) & (girls_data["Pass"] == True)]
    print("Percentage of discriminated by rank girls: " + str(len(discriminated_by_lowest_ranks_girls)/len(girls_data[girls_data["Pass"] == True])))
    favoured_girls = girls_data[(girls_data["Predicted_Pass"] == True) & (girls_data["Pass"] == False)]
    print("Percentage of favoured girls:" + str(len(favoured_girls) / len(girls_data[girls_data["Pass"] == False])))
    favoured_by_ranking_girls = girls_data[(girls_data["PredictedRank"] < 3) & (girls_data["Pass"] == False)]
    print("Percentage of favoured by ranking girls:" + str(len(favoured_by_ranking_girls) / len(girls_data[girls_data["Pass"] == False])))
    no_change_girls = girls_data[(girls_data["Predicted_Pass"] == girls_data["Pass"])]
    print("Percentage of no change girls:" + str(len(no_change_girls) / len(girls_data)))


def add_qualtrics_data_to_blocks():
    qualtrics_answers = pd.read_excel(qualtrics_report_file, header=0)
    block_info = pd.read_excel(block_info_file)

    qualtrics_answers = filter_out_non_participation(qualtrics_answers)
    qualtrics_answers = filter_short_responses(qualtrics_answers)
    qualtrics_answers = filter_out_wrong_grade_range(qualtrics_answers)
    qualtrics_answers = filter_out_wrong_grade_orders(qualtrics_answers)

    block_info, processed_blocks = add_predictions_to_all_blocks(qualtrics_answers, block_info)
    block_info = block_info.set_index('index')
    block_info = block_info.drop(["Unnamed: 0"], axis=1)
    block_info = block_info.rename(columns={"BlockID": "ParticipantID"})
    block_info.to_excel("PortugueseStudentsWithBiasedLabels.xlsx")
    return block_info

