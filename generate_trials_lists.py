#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import pandas as pd
import random
import itertools
import sys, os
from copy import deepcopy

# Make sure the working directory is correct
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# increase the recursion length
sys.setrecursionlimit(2000)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def generate_event_lists(event_types):
    events_file = 'events.csv'

    events_df = pd.read_csv(events_file)
    # convert the data frame to a list of dictionaries
    all_events = events_df.to_dict('records')
    print(all_events)

    # create a dictionary that groups events by condition
    events_by_type = {}
    for event_type in event_types:
        events_by_type[event_type] = [e for e in all_events if e['event_type']==event_type]

    return events_by_type

# Pseudo-randomize trials so that consecutive events share at most
# the number of specified constituents
def pseudo_randomize_trials(trials, max_shared_const_count=0):
    randomized_trials = []
    num_trials = len(trials)

    trial = random.choice(trials)
    randomized_trials.append(trial)

    append_to_end = True
    append_to_start = False

    unhoused_trials = []

    while len(randomized_trials) < num_trials:
        if trial in randomized_trials:
            trials.remove(trial)

        if append_to_end:
            # get all the trials that don't share a constituent with the last trial in the randomized list
            temp_trials = [trial for trial in trials if shared_const_count(trial, randomized_trials[-1]) <= max_shared_const_count]
            if len(temp_trials) > 0:
                # select a random element from temp_trials and append it to the end of trials
                trial = random.choice(temp_trials)
                randomized_trials.append(trial)
                # move to the next iteration
                continue
            else:
                # there are no more trials that can be appended to the end of the list
                # so append to the start
                append_to_end = False
                append_to_start = True

        if append_to_start:
            # get all the trials that don't share a constituent with the first trial in the randomized list
            temp_trials = [trial for trial in trials if shared_const_count(trial, randomized_trials[0]) <= max_shared_const_count]
            if len(temp_trials) > 0:
                trial = random.choice(temp_trials)
                randomized_trials.insert(0,trial)
                # move to the next iteration
                continue
            else:
                append_to_start = False

        if not append_to_end and not append_to_start:
            # if we've reached this point, it means that none of the remaining trials can be appended either to the start or end
            # try to slot the remaining trials between pairs in the randomized trials list

            # get a list of consecutive pairs of elements from the randomized list
            pairwise_list = pairwise(randomized_trials)
            # pick a random trial and see if it can slot into the randomized trials list
            trial = random.choice(trials)

            slot_found = False
            for pair in pairwise_list:
                if shared_const_count(trial,pair[0]) == 0 and shared_const_count(trial,pair[1]) <= max_shared_const_count:
                    # get the index of the second element of pair: trial is inserted before this
                    ind = randomized_trials.index(pair[1])
                    randomized_trials.insert(ind, trial)
                    slot_found = True
                    break

            if not slot_found:
                if trial not in unhoused_trials:
                    unhoused_trials.append(trial)
                else: # can we say that there\'s no home for the trial?
                    print('Can\'t find a slot. Trials list still contains ' + str(len(trials)))
                    break

    return randomized_trials


def get_trials(trial_list, num_trials, max_shared_constituents=0):
    trials = []
    randomize_list = []

    # get half the trials from the reversible list, half from nonreversible list
    for key in trial_list:
        trials += random.sample(trial_list[key], num_trials//2)

    randomized_list = pseudo_randomize_trials(list(trials), max_shared_constituents)

    if(len(randomized_list) == num_trials):
        return randomized_list
    else:
        # try again
        return get_trials(trial_list, num_trials, max_shared_constituents)

def shared_const_count(trial,trial_to_compare):
    shared_const = 0

    if trial != None and trial_to_compare != None:
        if trial['agent'] == trial_to_compare['agent']:
            shared_const += 1
        if trial['agent'] == trial_to_compare['patient']:
            shared_const += 1
        if trial['patient'] == trial_to_compare['patient']:
            shared_const += 1
        if trial['patient'] == trial_to_compare['agent']:
            shared_const += 1
        if trial['action'] == trial_to_compare['action']:
            shared_const += 1

    return shared_const

def write_to_csv(trials, participant):

    # generate file name from participant id
    file_name = 'trial_list_' + str(participant) + '.csv'

    num = 1
    data_lines = []

    for trial in trials:
        # add the trial number and word order type to each trial
        data_line = ','.join([str(participant),str(num),trial['event_type'],trial['event'],
                                trial['agent'],trial['agent_type'],trial['patient'],trial['patient_type'],
                                trial['action'],trial['event_file_name']])
        data_lines.append(data_line)

        num += 1

    f = open('./trials/' + file_name, 'w')

    line = ','.join(['p_id','trial_num','event_type','event',
    'agent','agent_type','patient','patient_type','action','event_file_name']) #header row, comma-separate
    line += '\n' #add a newline
    f.write(line)

    for i in range(len(data_lines)):
        line = data_lines[i]
        line += '\n' #add a newline
        f.write(line)
        f.flush()
        os.fsync(f)

def make_trials():
    num_trials = 32
    max_shared_const = 0

    for i in range(1,participants+1):
        print('participant: ', i)
        all_trials = []

        all_trials += get_trials(event_list, num_trials, max_shared_const)
        print('trials list made')

        print(len(all_trials))

        # write the trials to csv
        write_to_csv(all_trials, i)

event_types = ['reversible','nonreversible']

# create a list of events for each condition
event_list = generate_event_lists(event_types)
participants = 50

make_trials()
