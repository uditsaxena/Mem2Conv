import json
import os, pprint
import random


def main():
    print("Hello World")
    print(os.getcwd())
    print(os.listdir("../data/wikidata"))
    json_file_name = "../data/wikidata/wikidata_short_1.json"
    count = 0
    # for item in ijson.items(open(json_file_name), 'dic'):
    #     print(item)
    #     count += 1
    #     if (count > 10):
    #         break


# Given a filename, show the turn-based converstion:
def show_conversation(filename="../data/CSQA_v9/train/QA_0/QA_0.json", description=None):
    file = open(filename)
    file_json = json.load(file)
    description_flag = False
    for item in file_json:
        speaker = item['speaker']
        utterance = item['utterance']
        if 'question-type' in item:
            question_type = item['question-type']
            if description is not None and 'question-type' in item and description == item['question-type']:
                description_flag = True

            if description_flag:
                print("---------")
            print("{}: {} (type: {})".format(speaker, utterance, question_type))

        else:
            print("{}: {}".format(speaker, utterance))
            if description_flag:
                print("---------")

            description_flag = False


def show_conversation_with_kb(item_dict, relation_dict, filename="../data/CSQA_v9/train/QA_0/QA_0.json"):
    file = open(filename)
    file_json = json.load(file)
    description_flag = False

    # TODO: a lot of modifications to come to actually print out a legit KB, this is the active set
    for item in file_json:
        speaker = item['speaker']
        print(speaker, ": ", item['utterance'])
        if speaker != "SYSTEM":
            continue
        active_set_list = item['active_set']
        # is a list: []
        print("KB sub-graph: ")
        for kb_tuple_str in active_set_list:

            if kb_tuple_str.startswith("OR"):
                kb_tuple_str = kb_tuple_str[3:-1]
                kb_tuple_str = kb_tuple_str.split(", ")
                print("OR: {}".format(len(kb_tuple_str)))
            elif kb_tuple_str.startswith("AND"):
                kb_tuple_str = kb_tuple_str[4:-1]
                kb_tuple_str = kb_tuple_str.split(", ")
                print("AND: {}".format(len(kb_tuple_str)))
            if isinstance(kb_tuple_str, list):
                kb_tuple_str_list = kb_tuple_str
            else:
                kb_tuple_str_list = [kb_tuple_str]

            for kb_tuple_str_element in kb_tuple_str_list:
                kb_tuple = kb_tuple_str_element[1: -1].split(",")
                item1 = kb_tuple[0]
                relation_str = kb_tuple[1]
                item2 = kb_tuple[2]

                item1_label = parse_item(item1, item_dict)
                item2_label = parse_item(item2, item_dict)
                relation_label = relation_dict[relation_str]
                print("{} -- {} -- {}".format(item1_label, relation_label, item2_label))
            print()


def parse_item(item, item_dict):
    entities_in_item = item.split("|")
    label = ""
    for entity in entities_in_item:
        if entity.startswith("c("):
            entity_key = entity[2:-1]
            # print(entity_key)
        else:
            entity_key = entity
            # print(entity_key)
        if len(label) == 0:
            label = item_dict[entity_key]
        else:
            label += "and" + item_dict[entity_key]
    return label


def build_question_type_filter(data_dir="../data/CSQA_v9", root_dirs=['train'], limit=5):
    qt_filter = {}
    count = 1
    qt_index_lookup = {}
    index = 1
    for directory in root_dirs:
        curr_dir = data_dir + "/" + directory
        subfolder_list = os.listdir(curr_dir)
        for subfolder in subfolder_list:
            if (subfolder.startswith(".")):
                continue
            curr_subfolder_dir = curr_dir + "/" + subfolder
            file_list = os.listdir(curr_subfolder_dir)
            for file in file_list:
                if (count > 1000):
                    continue
                if file.startswith("."):
                    continue
                curr_file_path = curr_subfolder_dir + "/" + file
                # print(subfolder, file)
                subfolder_str = subfolder.replace("QA_", "")
                file_str = file.replace("QA_", "").replace(".json", "")
                file_index = subfolder_str + "_" + file_str
                # e.g. file_index = 103_100
                # print(file_index, subfolder, file)
                with open(curr_file_path) as f:
                    file_json = json.load(f)
                    for item in file_json:
                        # print(item)
                        if 'question-type' not in item:
                            continue
                        question_type = item['question-type']

                        if (question_type not in qt_index_lookup):
                            qt_index_lookup[question_type] = index
                            qt_filter[index] = [file_index]
                            index += 1

                        else:
                            curr_index = qt_index_lookup[question_type]
                            if (len(qt_filter[curr_index]) <= limit):
                                qt_filter[curr_index].append(file_index)
                            else:
                                pass

                count += 1

    # print(count)
    # print(qt_filter)
    sorted_qt_index_lookup = sorted(qt_index_lookup.items(), key=lambda x: x[1])
    print("Question Type Filters: ")
    for item in sorted_qt_index_lookup:
        print(item[0])

    return qt_index_lookup, qt_filter


def filter_sample_conversation(qt_index_lookup, qt_filter,
                               question_type="Comparative|More/Less|Mult. entity type|Indirect"):
    dir = "../data/CSQA_v9/train/"
    index = qt_index_lookup[question_type]
    doc_list = qt_filter[index]
    list_index = random.randrange(1, len(doc_list))
    single_doc = doc_list[list_index].split('_')
    subdir = "QA_" + single_doc[0]
    file = "QA_" + single_doc[1] + ".json"
    file_path = dir + subdir + "/" + file
    print("Present in the file: ", file_path, "\n")
    show_conversation(filename=file_path, description=question_type)


if __name__ == '__main__':
    # main()
    # show_conversation()
    build_question_type_filter()
