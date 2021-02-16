import random
import json
from yaml import safe_load
import pandas as pd

def load_clean_data(path_to_file=None):
    print("[INFO] Loading json data from", path_to_file)
    with open(path_to_file, 'r') as file:
        data = pd.DataFrame(json.load(file))

    print("[INFO] Removing articles without summary or paragraphs")
    print("[INFO] Size before cleaning:", len(data))
    data = data[(data["Summary"].map(len) >= 1)
                & (data["Paragraphs"].map(len) >= 1)]
    print("[INFO] Size after cleaning:", len(data))

    print("[INFO] Removing summaries where the first word is 'By'")
    print("[INFO] Size before cleaning:", len(data))
    data = (data[data["Summary"].apply(lambda x: (x[0:2] != "By"))])
    print("[INFO] Size after cleaning:", len(data))
    print("[INFO] Remove 'daily briefing' articles.")
    week_day = [
        "Monday:", "Tuesday:", "Wednesday:", 'Thursday:', "Friday:",
        "Saturday:", "Sunday:"
    ]
    print("[INFO] Size before cleaning:", len(data))
    data = (data[data["Summary"].apply(lambda x:
                                       (x.split(" ")[0] not in week_day))])
    print("[INFO] Size after cleaning:", len(data))
    return data.reset_index(drop=True)

def main():
    print("\n\t\t SUMMARIZATION MANUAL EVALUATION\t\t\n")
    print('[INFO] Loading configuration.')
    with open("./config.yml", 'r') as file:
        config_var = safe_load(file)["main"]
    print("[INFO] Loading generated summaries.")
    with open(config_var["output_folder"] + "/summaries.json", 'r') as file:
        summaries = pd.DataFrame(json.load(file))

    data = load_clean_data(path_to_file=str(config_var['dataset_folder']) + "/" +
                           str(config_var['data_to_use']))
    #
    #

    ##### Initiate empty dictionary
    score_dict = {}
    for col in summaries:
        score_dict[col] = {}
    print("[INFO] Evaluation Time")
    for n, idx in enumerate(
            random.sample(range(0, len(summaries)), config_var["num_eval"])):
        print("[INFO] Test number", n)
        print('[INFO] Real summary:\n\n«', data["Summary"][idx], "»\n")
        for col in summaries:
            print("[INFO] Generate summary by " + str(col) + ":\n\n«",
                  summaries[col][idx], "»\n")
            while True:
                print("[INPUT] Give score [1-5]:")
                try:
                    score = int(input())
                except:
                    score = 0
                if score > 5 or score < 1:
                    print("[ERROR] Please give number between 1 and 5 (included).")
                    pass
                else:
                    break
            score_dict[col].update({idx: score})
    print("[INFO] Saving manual evaluations to", config_var['output_folder']+"/manual_evaluation.json")

    with open(config_var['output_folder']+"/manual_evaluation.json", 'w') as file:
        json.dump(score_dict, file)

if __name__ == "__main__":
    main()
