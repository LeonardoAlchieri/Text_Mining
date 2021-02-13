# DESCRIPTION

This is the Text Mining & Search project repo. It contains the script and the data to run the whole project.
See below for more information as how to install and run everything.

# DATA

In this project 2 main datasets are used:
- NYTimes data, obtained using an automated scraper (purpose built).
- The XSum dataset, obtained as detailed by the researchers (see https://github.com/EdinburghNLP/XSum)

Any other dataset can be used with the following code, given its preparation as follow:
- List of dictionaries.
- Each dictionary must have the following keys:
  - "Summary": a short summary of the article. Must be a single string.
  - "Paragraphs": a list of strings, containing the paragraphs of the article.
- Saved in json format.

# REQUIREMENTS & INSTALLATION

The scripts have been tested on `python 3.7`, `python 3.8` and `python3.9`. It has not been tested no less recent versions, but it might work on any `3.*` release.
All of the requirements for the scripts are listed in the file `requirements.txt`.
Please run `pip install -r requirements.txt` to run everything.

*Suggestion*: it may be a good idea to install everything in a virtua environment. If using *Anaconda*, this can be achieved by running `conda create --name MY_ENV python=3.7`

# SCRIPTS

The following order is the one used to run all of the project.
1. Prepare the configurations in the `config.yml` file. Under the `main` identifier, specify:
  - name of the datafile (plase give a `json` file) [`data_to_use`]
  - name of the folder of the datafile ['dataset_folder']
  - language in which the articles have been written ['language']
  - output folder, for where to place the results ['output_folder']
  - number of manual evaluations to be performed in the pipeline ["num_eval"]
  - name with which to save plots ["name"]
  - folder to which save the visualizations ['vis_folder']
  - it is possible to specificy as well a list of HEX colors to be used for the visulizations ['color_vis']
  By default, the configuration to run smoothly the NyTimes dataset is provided (and commentede is the configuration for the XSum dataset).
2. Run `python3 main.py`. This scripts will clean the data, generate the summarizations and evaluate them using the various rouge metrics provided by the `sumy` package.
3. Run `python3 visualizations.py` to create visualizations from the evaluation results. This will be saved as pdf file in the corresponding visualization folders.
4. Run `python3 manual_evaluation.py` to randomly sample some summaries and manually compare the real one to the different generated ones. CMD inputs will be required to give human scores to each summary. The files will be saved to the configured output folder as a json file.

# WARNINGS
There are 2 scripts, namely `scraping\NYTimes_scraping.py` and `prepare_xsum.py`, that have been used to scrape the data and clean up the data from XSum, respectively. Since they are technically not part of the project, where the data is considered given "as is", please do not run them.
In particular, the former script is very time consuming, with the whole scraping processes taking well over a few hours and using a virtual machine.

For more information on this regard, please contact me and I shall give more details.

-------
If some problems arise during the execution of any of the above steps, please do not hesitate to contact me.
All of the scripts have been successfully tested on `MacOS 11.1`.

@Leonardo Alchieri, 2021
