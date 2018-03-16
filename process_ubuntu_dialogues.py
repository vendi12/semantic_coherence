# -*- coding: utf-8 -*-
'''
svakulenko
28 Feb 2018

Iterate over the dialogues from the Ubuntu corpus
'''
import os
import unicodecsv, csv
from collections import Counter

# from trace_relations import trace_relations
from dbpedia_spotlight import annotate_entities

PATH = './ubuntu/dialogs'
PATH_ANNOTATIONS = './ubuntu/annotated_dialogues'
PATH1 = './ubuntu/dialogs/555'
SAMPLE_DIALOG = './ubuntu/dialogs/135/9.tsv'

dialog_end_symbol = "__dialog_end__"


def create_negative_sample():
    '''
    take 2 random dialogues
    take part of one dialogue and append it to another
    '''
    pass


def translate_dialog_to_lists(dialog_filename):
    """
    from create_ubuntu_dataset.py by Rudolf Kadlec

    Translates the dialog to a list of lists of utterances. In the first
    list each item holds subsequent utterances from the same user. The second level
    list holds the individual utterances.
    :param dialog_filename:
    :return:
    """

    dialog_file = open(dialog_filename, 'r')
    dialog_reader = unicodecsv.reader(dialog_file, delimiter='\t', quoting=csv.QUOTE_NONE)

    # go through the dialog
    first_turn = True
    dialog = []
    same_user_utterances = []
    dialog.append(same_user_utterances)

    for dialog_line in dialog_reader:

        if first_turn:
            last_user = dialog_line[1]
            first_turn = False

        if last_user != dialog_line[1]:
            # user has changed
            same_user_utterances = []
            dialog.append(same_user_utterances)

        same_user_utterances.append(dialog_line[3])

        last_user = dialog_line[1]

    dialog.append([dialog_end_symbol])

    return dialog


def test_translate_dialog_to_lists():
    print translate_dialog_to_lists(PATH + '/10/10007.tsv')


def test_trace_relations():
    dialogue = [' '.join(turn) for turn in translate_dialog_to_lists(SAMPLE_DIALOG)]
    trace_relations(dialogue, True)


def trace_all_dialogues(dir=PATH1):
    # iterate over all the dialogues in the dataset
    for root, dirs, files in os.walk(dir):
        for name in files:
            file_path = os.path.join(root, name)
            print file_path
            dialogue = [' '.join(turn) for turn in translate_dialog_to_lists(file_path)]
            trace_relations(dialogue, True)


def annotate_ubuntu_dialogs(dir=PATH, nlimit=3, offset=0):
    n_files = 1
    for root, dirs, files in os.walk(dir):
        # iterate over dialogues 
        for name in files:
            file_path = os.path.join(root, name)
            annotation_path = os.path.join(PATH_ANNOTATIONS, '_'.join([root.split('/')[-1], name]))
            print annotation_path
            with open(file_path,"rb") as dialog_file:
                dialog_reader = unicodecsv.reader(dialog_file, delimiter='\t', quoting=csv.QUOTE_NONE)
                annotation_file = unicodecsv.writer(open(annotation_path, 'w'), encoding='utf-8')
                for dialog_line in dialog_reader:
                    # dialog line: [0] timestamp [1] sender [2] recepeint [3] utterance [4] entities
                    utterance = dialog_line[3]
                    entities = annotate_entities(utterance)
                    dialog_line.append(entities)
                    print dialog_line
                    annotation_file.writerow(dialog_line)

            # maintain file counter
            n_files += 1
            if n_files > nlimit:
                return


def count_ubuntu_dialogs(dir=PATH):
    n_files = 0
    for root, dirs, files in os.walk(dir):
        # iterate over dialogues 
        for name in files:
            file_path = os.path.join(root, name)
            # print file_path
            n_files += 1
    print n_files


def produce_dialog_stats(dir=PATH):
    # iterate over all the dialogues in the dataset
    n_files = 0
    n_annotated_dialogues = 0
    n_turns_dist = []
    n_utterances_dist = []
    n_entities_dist = []
    n_annotated_turns_dist = []
    n_unique_entities_dist = []

    for root, dirs, files in os.walk(dir):

        # iterate over dialogues 
        for name in files:
            file_path = os.path.join(root, name)
            print file_path
            n_files += 1

            # analyse dialogue-file
            n_turns = 0
            n_utterances = 0
            # DBpedia annotation stats
            n_entities = 0
            dialogue_annotated = 0
            n_annotated_turns = 0
            dialogue_entities = []


            # iterate over turns (speakers switch)
            for turn in translate_dialog_to_lists(file_path):
                turn_annotated = 0
                n_turns += 1

                # iterate over utterances in a turn (same speaker)
                for utterance in turn:
                    n_utterances += 1
                    entities = annotate_entities(utterance)
                    if entities:
                        # print entities
                        dialogue_annotated = 1
                        turn_annotated = 1
                        dialogue_entities.extend(entities)
                        n_entities += len(entities)

                n_annotated_turns += turn_annotated

            n_turns_dist.append(n_turns)
            n_utterances_dist.append(n_utterances)

            n_entities_dist.append(n_entities)
            n_annotated_dialogues += dialogue_annotated
            n_annotated_turns_dist.append(n_annotated_turns)

            dialogue_entities = Counter(dialogue_entities)
            # unique entities
            n_unique_entities = len(dialogue_entities.keys())
            n_unique_entities_dist.append(n_unique_entities)

            # print '\n'

    # dataset stats
    print '#Dialogues:', n_files
    # annotation stats
    print '#Annotated dialogues:', n_annotated_dialogues

    print '#Turns per dialogue:', n_turns_dist
    print '#Annotated turns per dialogue:', n_annotated_turns_dist
    print '#Entities per dialogue:', n_entities_dist
    print '#Unique entities per dialogue:', n_unique_entities_dist


if __name__ == '__main__':
    annotate_ubuntu_dialogs()