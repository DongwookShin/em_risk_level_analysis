import sys
# sys.path.append(".")
from preon.normalization import PrecisionOncologyNormalizer
from preon.drug import store_ebi_drugs, load_ebi_drugs
import timeit
import os
from os import listdir
import psycopg2
from configparser import ConfigParser
from openai import AzureOpenAI
from gptutils.utils import GPTResponseHelper
from gptutils.prompt import generate_prompt_high_risk, generate_prompt_dnr, generate_prompt_hospitalization
from em_risk_analysis import EMRiskAnalysis

def main(anno_path):
    risk_anal = EMRiskAnalysis()
   
    files = listdir(anno_path)
    for file in files:
        ifile = open(anno_path + "/" + file, "r")
        datalist = ifile.readlines()
        text = ''.join(line for line in datalist)
        text = text.replace("Speaker 1:", " ").replace("Speaker 2:", " ").replace("Speaker 3:", " ")

        try: 
            # message = generate_prompt_high_risk(text)
            # message = generate_prompt_dnr(text)
            message = generate_prompt_hospitalization(text)
            response = risk_anal.get_response_from_gpt(message)
            print(response)

        except:
             print(file)
             # errfile.write(file + "\n")
             continue

if __name__ == '__main__':
    main('./annotation-sample2')