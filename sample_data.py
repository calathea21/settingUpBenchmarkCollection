import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import collections

#columns of interest: ['sex', 'studytime', 'freetime', 'romantic', 'Walc', 'goout', 'Parents_edu', 'absences', 'reason']

def load_data():
    maths_performance = pd.read_csv('student-mat.csv')
    maths_performance['subject'] = "Maths"
    portuguese_performance = pd.read_csv('student-por.csv')
    portuguese_performance['subject'] = "Portuguese"

    all_performances = pd.concat([maths_performance, portuguese_performance], axis=0)
    all_performances = all_performances.reset_index(drop=True)
    print(len(all_performances))
    all_performances = all_performances[all_performances['G3'] != 0].reset_index(drop=True)
    print(len(all_performances))
    #originally studytime has 4 levels, going to change it to 3 (less than 2 hours, 2-5 hours, more than 5 hours)
    cut_labels_studytime = [1, 2, 3]
    cut_bins_studytime = [0, 1, 2, 4]

    all_performances['Pass'] = all_performances['G3']>=10

    all_performances['studytime'] = pd.cut(all_performances['studytime'], bins=cut_bins_studytime,
                                           labels=cut_labels_studytime)
    #originally Weekly Alcohol Consumption has 5 levels, going to bin to 4 (low/moderate/high/very high)
    cut_labels_walc = [1, 2, 3, 4]
    cut_bins_walc = [0, 1, 2, 3, 6]
    all_performances['Walc'] = pd.cut(all_performances['Walc'], bins=cut_bins_walc, labels=cut_labels_walc)

    #originally freetime has 5 levels, going to bin to 3 (low/average/high)
    cut_labels_freetime = [1, 2, 3]
    cut_bins_freetime = [0, 2, 3, 6]
    all_performances['freetime'] = pd.cut(all_performances['freetime'], bins=cut_bins_freetime, labels=cut_labels_freetime)

    #originally goout has 5 levels, going to bin to 4 (never/once a week/twice a week, thrice or more)
    cut_labels_goout = [1, 2, 3, 4]
    cut_bins_goout = [0, 1, 2, 3, 7]
    all_performances['goout'] = pd.cut(all_performances['goout'], bins=cut_bins_goout, labels=cut_labels_goout)

    #instead of looking at fathers' and mothers' education seperately, going to look at maximum of both
    all_performances['Parents_edu'] = all_performances[['Fedu', 'Medu']].max(axis=1)
    #also going to bin this to 4 levels (lower, middle school, high school, university)
    all_performances['Parents_edu'] = pd.cut(all_performances['Parents_edu'], bins=[-1, 1, 2, 3, 4],
                                             labels=[1, 2, 3, 4])

    cut_labels_absences = [0, 1, 2, 3, 4, 5, 6, 7]
    cut_bins_absences = [-1, 1, 2, 3, 4, 5, 6, 7, 1000]
    all_performances['absences'] = pd.cut(all_performances['absences'], bins=cut_bins_absences, labels=cut_labels_absences)

    all_performances.to_excel("original_data.xlsx")

    final_data = all_performances[['sex', 'studytime', 'freetime', 'romantic', 'Walc', 'goout', 'Parents_edu', 'absences', 'reason', 'G3', 'Pass']]

    return final_data

def sample_428_boys_and_428_girls():
    #misschien toch zo samplen dat groter gedeelte van fails wegvalt
    loaded_data = load_data()
    female = loaded_data[loaded_data.loc[:, 'sex'] == 'F']
    print(len(female))
    male = loaded_data[loaded_data.loc[:, 'sex'] == 'M']
    print(len(male))

    sampled_data_female = female.sample(n=428, random_state=2)
    sampled_data_male = male.sample(n=428, random_state=2)

    all_sampled_data = pd.concat([sampled_data_female, sampled_data_male], axis=0)
    return all_sampled_data


def create_list_of_blocks():
    list_of_blocks = []
    balanced_data = sample_428_boys_and_428_girls()
    number_of_datapoints = balanced_data.shape[0]
    number_of_blocks = int(number_of_datapoints/8)
    for i in range(number_of_blocks):
        sample = balanced_data.groupby('sex', group_keys=False).apply(lambda x: x.sample(4, random_state=2))
        balanced_data = balanced_data.drop(sample.index)
        list_of_blocks.append(sample)
    return list_of_blocks