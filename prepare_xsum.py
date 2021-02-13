import json
import glob
from yaml import safe_load

remove_words_list = ['Share this with',
  'Email',
  'Facebook',
  'Messenger',
  'Messenger',
  'Twitter',
  'Pinterest',
  'WhatsApp',
  'LinkedIn',
  'Linkedin',
  'Copy this link',
  'These are external links and will open in a new window']

def prepare_data(file = None, remove_words_list = []):
    with open(file, 'r') as f:
        x = f.read().split("\n\n")[1:]
    return ({
        "Summary":
        " ".join(x[0].split("\n")[1:]),
        "Paragraphs":
        [el for el in x[1].split("\n")[1:] if el not in remove_words_list]
    })

def main():
    print("\n\t\t XSUM-DATA PREPARATION \t\t\n")
    print('[INFO] Loading configuration')
    with open("./config.yml", 'r') as file:
        config_var = safe_load(file)["xsum"]
    print("[INFO] Formatting data.")
    list_xsum = [
    prepare_data(file) for file in glob.glob(config_var["input_dir"]+"/*.data")
                ]
    print("[INFO] Saving to json formatted data.")
    with open(config_var["output_dir"]+"/xsum.json", 'w') as file:
        json.dump(list_xsum, file)
    print("[INFO] Program completed.")

if __name__ == "__main__":
    main()
