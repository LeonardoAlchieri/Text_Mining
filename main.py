# Json to load dataset
import json
from yaml import safe_load
import pandas as pd
import re
# Extractive
from nltk.tokenize import WordPunctTokenizer, PunktSentenceTokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.random import RandomSummarizer
from sumy.summarizers.kl import KLSummarizer
from sumy.summarizers.reduction import ReductionSummarizer
from sumy.utils import get_stop_words

from sumy.evaluation.rouge import (rouge_1, rouge_2,
                                   rouge_l_sentence_level,
                                   rouge_l_summary_level, rouge_n)
from sumy.models.dom._sentence import Sentence

import numpy as np

import nltk
from nltk.corpus import stopwords

import progressbar

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
    data["Paragraphs_as_string"] = data["Paragraphs"].apply(lambda x: "\n\n".join(x))
    return data.reset_index(drop=True)
#
#
#
#
def main():
    print("\n\t\t SUMMARIZATION REVIEW\t\t\n")
    print('[INFO] Loading configuration')
    with open("./config.yml", 'r') as file:
        config_var = safe_load(file)["main"]

    data = load_clean_data(path_to_file=str(config_var['dataset_folder']) + "/" +
                       str(config_var['data_to_use']))
    #
    #
    #
    print("[INFO] Training sentence tokenizer for summary on all articles.")
    punkt_tokenizer = PunktSentenceTokenizer(
    train_text="\n".join([sent for sent in data["Paragraphs_as_string"]])
                                            )
    #
    #
    #
    len_sum = np.mean(data["Summary"].apply(lambda x: len(punkt_tokenizer.tokenize(x))))
    print("[INFO] Average number of sentences in article summaries", len_sum)
    print("[COMMENT] Considering this value as reference to generate the automatic summaries.")
    len_sum = int(len_sum)
    #
    #
    #
    print("[INFO] Using "+str(config_var['language'])+"stenner")
    stemmer = Stemmer(config_var['language'])
    print("[INFO] Preparing summarizers")
    summarizer_dict = {"LSA":LsaSummarizer(stemmer),
                        "Luhn": LuhnSummarizer(stemmer),
                        "LexRank":LexRankSummarizer(stemmer),
                        "SumBasics":SumBasicSummarizer(stemmer),
                        "Random": RandomSummarizer(stemmer),
                        "Reduction": ReductionSummarizer(stemmer)}

    print("[INFO] Preparing stopwords.")
    for summarizer in summarizer_dict.values():
        summarizer.stop_words = get_stop_words('english')

    print("[INFO] Summaries preparation")
    dict_res = {}
    dict_summs = {}
    for name, summarizer in summarizer_dict.items():
        print("[INFO] Method:", name)
        results_rouge_1 = []
        results_rouge_2 = []
        results_rouge_l_1 = []
        results_rouge_l_2 = []
        sums = {}
        for i in progressbar.progressbar(range(len(data))):
            (article, summary) = (data["Paragraphs_as_string"][i],
                                  data["Summary"][i])

            parser = PlaintextParser.from_string(
                article, tokenizer=Tokenizer('english'))

            summaries = [
                sentence for sentence in summarizer(parser.document, len_sum)
            ]
            summaries_str = [
                str(sentence) for sentence in summarizer(parser.document, len_sum)
            ]
            # Append current summary results
            # Since there are problems with some documents
            # being skipped, I need to save the index as well
            sums[i] = (" ".join(summaries_str))

            #     To use sumy's evaluation functions, I need to have the text in
            #     Sentence objects
            reference_sentences = [
                Sentence(sent, tokenizer=Tokenizer("english"))
                for sent in punkt_tokenizer.tokenize(summary)
            ]
            try:
                results_rouge_1.append(
                    rouge_1(evaluated_sentences=summaries,
                            reference_sentences=reference_sentences))
            except:
                results_rouge_1.append(np.nan)
            try:
                results_rouge_2.append(
                    rouge_2(evaluated_sentences=summaries,
                                          reference_sentences=reference_sentences))
            except:
                # print("[ERROR] Some problem occurd in the rouge_L (summary level) calculation. This is most likely caused by sentences too short in the summary. No workaround has been found for this: the value will be set to NA.")
                results_rouge_2.append(np.nan)

            try:
                results_rouge_l_1.append(
                    rouge_l_sentence_level(evaluated_sentences=summaries,
                                          reference_sentences=reference_sentences))
            except:
                # print("[ERROR] Some problem occurd in the rouge_L (summary level) calculation. This is most likely caused by sentences too short in the summary. No workaround has been found for this: the value will be set to NA.")
                results_rouge_l_1.append(np.nan)

            try:
                results_rouge_l_2.append(
                    rouge_l_summary_level(evaluated_sentences=summaries,
                                          reference_sentences=reference_sentences))
            except:
                # print("[ERROR] Some problem occurd in the rouge_L (summary level) calculation. This is most likely caused by sentences too short in the summary. No workaround has been found for this: the value will be set to NA.")
                results_rouge_l_2.append(np.nan)
    #         Save results and progress to next summarizer
        dict_res[name] = {
            "Rouge_1": results_rouge_1,
            "Rouge_2": results_rouge_2,
            "Rouge_L_sentence_level": results_rouge_l_1,
            "Rouge_L_summary_level": results_rouge_l_2
        }
        # Save summaries to dictionary
        dict_summs[name] = sums
    print("[INFO] Summaries and evaluations completed.")
    print("[INFO] Saving data to output.")
    # Create pandas dataframe for mean of results
    res_mean = pd.DataFrame(columns = dict_res.keys())
    # Dataframe for std of results
    res_se = pd.DataFrame(columns = dict_res.keys())
    for col in res_mean:
        res_mean[col] = pd.Series(
            {key: np.nanmean(value)
             for key, value in dict_res[col].items()})
        res_se[col] = pd.Series(
            {key: np.nanstd(value)/np.sqrt(len(value))
             for key, value in dict_res[col].items()})

    print("[INFO] Saving evaluation averages.")
    with open(config_var['output_folder']+"/avgs.csv", 'w') as file:
        res_mean.to_csv(file)
    print("[INFO] Saving evaluations standard errors.")
    with open(config_var['output_folder']+"/ses.csv", 'w') as file:
        res_se.to_csv(file)
    print("[INFO] Saving to json all produced summaries.")
    with open(config_var['output_folder']+"/summaries.json", 'w') as file:
        json.dump(dict_summs, file)
    print("[INFO] Program completed successfully.")
if __name__ == "__main__":
    main()
