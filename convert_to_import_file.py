"""
In sample_data.py we preprocessed and sampled the data we want to present in the experiment. In this file we
put all of the data in a .txt file and format it such that it can be loaded directly into Qualtrics
"""

import pandas as pd
import random
random.seed(2)
from sample_data import create_list_of_blocks


def reason_to_text(reason_indicator):
    if reason_indicator=='home':
        return "Close to home"
    elif reason_indicator=="course":
        return "Curriculum"
    elif reason_indicator=="reputation":
        return "Reputation"
    elif reason_indicator=="other":
        return "Unknown"

def studytime_number_to_text(studytime_number):
    if studytime_number==1:
        return "less than 2 hours"
    elif studytime_number==2:
        return "2-5 hours"
    elif studytime_number==3:
        return "more than 5 hours"
    return ""

def freetime_number_to_text(freetime_number):
    if freetime_number==1:
        return "low"
    elif freetime_number==2:
        return "average"
    elif freetime_number==3:
        return "high"
    return ""

def absences_number_to_text(absences_number):
    if absences_number<=6:
        return absences_number
    else:
        return "more than 6"

def alc_consumption_number_to_text(alc_number):
    if alc_number==1:
        return "low"
    elif alc_number==2:
        return "moderate"
    elif alc_number==3:
        return "high"
    elif alc_number==4:
        return "very high"
    return ""

def goout_number_to_text(goout_number):
    if goout_number==1:
        return "never"
    elif goout_number==2:
        return "once a week"
    elif goout_number==3:
        return "twice a week"
    elif goout_number==4:
        return "thrice or more"
    return ""

def parents_edu_number_to_text(parent_edu_number):
    rating_to_word = ''
    if parent_edu_number == 1:
        rating_to_word = 'Primary Education'
    if parent_edu_number == 2:
        rating_to_word = 'Middle School'
    if parent_edu_number == 3:
        rating_to_word = 'High School'
    if parent_edu_number == 4:
        rating_to_word = 'University'
    return rating_to_word

def column_value_to_qualtrics_description(column, column_value):
    if column == 'goout':
        return goout_number_to_text(column_value)
    if column == 'freetime':
        return freetime_number_to_text(column_value)
    if column == 'Walc':
        return alc_consumption_number_to_text(column_value)
    if column == 'studytime':
        return studytime_number_to_text(column_value)
    if column == 'Parents_edu':
        return parents_edu_number_to_text(column_value)
    if column == "reason":
        return reason_to_text(column_value)
    if column == "absences":
        return absences_number_to_text(column_value)
    else:
        return column_value

# '<b> Reason School Choice</b> - <em>Curriculum</em> <br>'
# '<b> Freetime</b> - <em>average</em> <br>'
# '<b> Going out</b> - <em>Twice a week</em> <br>'
# '<b> In a relationship</b> - <em>no</em> <br>'
# '<b> Alcohol consumption</b> - <em>moderate</em> <br>'
# '<b> Studytime</b> - <em>between 2 and 5 hours</em> <br>'
# '<b> Absences</b> - <em>3</em> <br>'
# '<b> Parents\' education</b> - <em>Middle School</em> <br>'
# '<b> Sex</b> - <em>female</em> <br>'

def vignette_to_text(vignette, name):
    column_name_to_description_dict = {'freetime': 'Freetime', 'goout': 'Going out',
                                       'romantic': 'In a relationship', 'Walc': 'Alcohol consumption',
                                       'studytime': 'Studytime', 'absences': 'Absences',
                                       'Parents_edu': "Parents' education", 'reason': "Reason School Choice"}
    column_names = ['freetime', 'goout', 'romantic', 'Walc', 'studytime', 'absences', 'Parents_edu', 'reason']
    random.shuffle(column_names)

    vignette_text = "<div style = \"text-align: center;\"> <div id=\"" + name + "\"> <span style=\"font-size:22px;\"> <b>" + name
    vignette_text += "</b> </span></div><div style=\"text-align: center;\"><span style=\"font-size:22px;\"><b><br></b></span></div>"
    vignette_text += "<div style = \"text-align: center;\">\n"

    for column in column_names:
        vignette_text += "<b>" + column_name_to_description_dict[column] + "</b> - "
        vignette_text += "<em>" + str(column_value_to_qualtrics_description(column, vignette[column])) + "</em> <br> \n"


    return vignette_text

def draw_random_vignette(block, girl_names, boys_names, indices, dataframe, id):
    #hier dus iets doen om de goede index te krijgen,
    random_index = random.sample(indices, 1)[0]
    indices.remove(random_index)

    data_point = block.iloc[random_index]
    index = block.index[random_index]
    sex = data_point['sex']

    if (sex=='F'):
        name = random.sample(girl_names, 1)[0]
        girl_names.remove(name)
    else:
        name = random.sample(boys_names, 1)[0]
        boys_names.remove(name)

    vignette_description = vignette_to_text(data_point, name)

    data_entry = data_point.copy()
    data_entry['name'] = name
    data_entry["index"] = index
    data_entry["BlockID"] = id
    dataframe = dataframe.append(data_entry)
    return vignette_description, dataframe


def create_one_block(block, block_id, dataframe):
    girl_names = ["Anna", "Sarah", "Lisa", "Jenny"]
    boy_names = ["Michael", "Brian", "David", "Oliver"]
    available_indices = [0, 1, 2, 3, 4, 5, 6, 7]

    block_text = "[[Question: DB]]\n"
    block_text += "[[ID:" + str(block_id) + "a]]\n"

    table = "<table border=\"1\" bordercolor=\"white\" cellpadding=\"10\" cellspacing=\"50\" style=\"width:100%\";> <tbody> <tr>\n"

    for i in range(8):
        vignette_text, dataframe = draw_random_vignette(block, girl_names, boy_names, available_indices, dataframe, block_id)
        table += "<td>" + vignette_text + "</td>\n"
        if (i%2 != 0 and i!=0):
            table += "<tr>"
    table += "</tr></tbody> </table>"

    block_text += table
    block_text += "\n"

    return block_text, dataframe


def make_file():
    all_blocks = create_list_of_blocks()

    columns_dataframe = ["BlockID", "index", "name"]
    columns_dataframe.extend(all_blocks[0].columns.tolist())
    data_frame = pd.DataFrame(columns=columns_dataframe)

    complete_text = "[[AdvancedFormat]] \n"
    i = 1
    for block in all_blocks:
        complete_text += "[[Block: Block" + str(i) + "]]\n"
        text, data_frame = create_one_block(block, i, data_frame)
        complete_text += text

        i +=1
    print(complete_text)

    text_file = open("output.txt", "w")
    text_file.write(complete_text)
    text_file.close()

    print(data_frame)
    data_frame.to_excel("blocks_information.xlsx")
    return complete_text

