import sys
from preon.normalization import PrecisionOncologyNormalizer
from preon.drug import store_ebi_drugs, load_ebi_drugs
import time
import spacy
import os
import psycopg2
from configparser import ConfigParser
from gptutils.utils import GPTResponseHelper
from gptutils.prompt import generate_prompt_drug_quotes, generate_prompt_procedure_quotes

from recommender.recommender import DoctorRecommender

select_drug = "select otc, rx, tx, cs  from drug_name where name = '{}'"

def load_config(filename='./database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

 # Extract the severity of the drug using drug name column: otx, rx, tx (toxic drug) and cs (Schedule 2 controlled substance)
def determine_drug_severity(row):
    if row[0] == True:
        return 3  # Row risk
    elif row[1] == True:
        return 4  # Midium risk
    elif row[2] == True:
        return 5  # High risk
    else:
        return 5 # High risk

def determine_procedure_severity(severity_str):
    if severity_str == "Therapy" or severity_str == "Needle Procedure":
        return 3 # Low risk
    elif severity_str == "Minor Surgery":
        return 4 # Moderate risk
    elif severity_str == "Major Surgery":
        return 5 # High risk
    elif severity_str == "Minor/Major Surgery":
        return 5 # Temporarily returns High risk, but needs more research

# Find the charaacter "." occurring before the index. This is to find the start of the sentence that contain the drug
def prev_find(text, character, index): 
    prev_index = index
    while prev_index >= 0:
        if text[prev_index] == character:
            return prev_index + 1
        else:
            prev_index -= 1
    
    return 0 # If there is no "." character before the drug name, then return 0

# FInd all sentences that contain the drug name in the transcript
def find_quotes_from_text(name, key, text):
    index = 0
    quotes = []
    while True:
        index = text.find(name, index)
        if index >= 0:
            start_index = prev_find(text, ".", index-1)
            end_index = text.find(".", index)
            asentence = text[start_index: end_index].strip()
            quotes.append({key: name, "quote": asentence})
            index = end_index + 1 # Start with the next sentence
        else:
            break
    return quotes
    
class EMRiskAnalysis:
    def __init__(self):
        # Initialize preon
        # Before running this, preon drug database ebi_drugs.csv needs to be copied into the file ~/preon/resources/ebi_drugs.csv
        self.drug_names, self.chembl_ids = load_ebi_drugs()
        self.normalizer = PrecisionOncologyNormalizer().fit(self.drug_names, self.chembl_ids)

        # Initialize spaCy model
        self.nlp1 = spacy.load("en_core_web_sm")
        self.nlp2 = spacy.blank("en")

        #Create the EntityRuler
        # ruler = nlp.add_pipe(EntityRuler(nlp=nlp, matcher_fuzzy_compare={"@misc": "spacy.levenshtein_compare.v1"})).from_disk("./spacy/procedure.jsonl")
        self.nlp2.add_pipe("entity_ruler").from_disk("./spacy/procedure.jsonl")

        # Load the pretrained recommendation model
        self.dr = DoctorRecommender().from_pretrained()

        self.config = load_config()
        self.conn = connect(self.config)
        self.cursor = self.conn.cursor()
        self.helper = GPTResponseHelper()
    
    def get_response_from_gpt(self, message):
        return self.helper.get_gpt_response(message)
    
    def predict_recommendation(self, quote):
        return self.dr.predict(quote)

def risk_anal(text):

    raw_text = text.replace("Speaker 1:", " ").replace("Speaker 2:", " ").replace("Speaker 3:", " ")
    risk_anal = EMRiskAnalysis()

    start = time.time()
    # Extract drugs from transcript using preon
    drug_names_from_preon = risk_anal.normalizer.query(text)
    drug_names_severity = {}
    drug_quotes = []

    # Extract procedure (surgery or therapy) and its severity using AvodahMed spaCy rule based model
    procedure_names_severity = {} 
    procedure_quotes = []
    doc = risk_anal.nlp1(text)
    corpus = []
    #use the spacy tokenizer to get the sentences.
    for sent in doc.sents:
        corpus.append(sent.text)
    
    #iterate over the sentences
    for sentence in corpus:
        doc = risk_anal.nlp2(sentence)

        #extract entities
        for ent in doc.ents:
            print (ent.text, ent.start_char, ent.end_char, ent.label_)
            procedure_names_severity[ent.text] = ent.label_

    risk_level = 2
    # drug_names = []
    if drug_names_from_preon:
        # Extract the severity of the drug using drug table among: otx, rx, tx (toxic drug) and cs (Schedule 2 controlled substance)
        for name in drug_names_from_preon[0]:
            risk_anal.cursor.execute(select_drug.format(name))
            rows = risk_anal.cursor.fetchall()
            if rows:
                for arow in rows:
                    severity = determine_drug_severity(arow)
                    drug_names_severity[name] = severity
                    drug_quotes.extend(find_quotes_from_text(name, "drug name", raw_text))
                    break

        """
        Extracting quotes from transcript that includes the input drug
        If There is GPT error, then drug_quotes_from_gpt should be empty
        """
        drug_quotes_from_gpt = []
        if drug_names_severity:
            message = generate_prompt_drug_quotes(drug_names_severity.keys(), raw_text)
            try:
                drug_quotes_from_gpt = risk_anal.get_response_from_gpt(message)
            except:
                print("Error on GPT processing")
        
        for drug_info in drug_quotes_from_gpt:
            drug_info["severity"] = drug_names_severity[drug_info["drug name"]]
            # Predict recommendation using recommendation classifier
            drug_info["recommendation"] = risk_anal.predict_recommendation([drug_info["quote"]])

        
        for drug_info in drug_quotes:
            drug_info["severity"] = drug_names_severity[drug_info["drug name"]]
            # Predict recommendation using recommendation classifier
            drug_info["recommendation"] = risk_anal.predict_recommendation([drug_info["quote"]])

        drug_quotes.extend(drug_quotes_from_gpt) # Combine two quotes 

    for drug_info in drug_quotes:
        # If the quote is determined that the doctor makes a recommendation
        if "recommendation" in drug_info and drug_info["recommendation"][0] == 1:
            risk_level = max(risk_level, drug_info["severity"])

    if procedure_names_severity:
        for name in procedure_names_severity.keys():
            #Extracting quotes from transcript that includes the input procedure
            procedure_quotes.extend(find_quotes_from_text(name, "medical procedure", raw_text))
        
        for procedure_info in procedure_quotes:
            procedure_info["severity"] = determine_procedure_severity(procedure_names_severity[procedure_info["medical procedure"]])
            # Predict recommendation using recommendation classifier
            procedure_info["recommendation"] = risk_anal.predict_recommendation([procedure_info["quote"]])
        
        message = generate_prompt_procedure_quotes(procedure_names_severity.keys(), raw_text)

        try:
            procedure_quotes_from_gpt = risk_anal.get_response_from_gpt(message)
        except:
            print("GPT error during retrieving quotes for procedure")

        for procedure_info in procedure_quotes_from_gpt:
            procedure_info["severity"] = determine_procedure_severity(procedure_names_severity[procedure_info["medical procedure"]])
            # Predict recommendation using recommendation classifier
            procedure_info["recommendation"] = risk_anal.predict_recommendation([procedure_info["quote"]])
        
        procedure_quotes.extend(procedure_quotes_from_gpt)

    for procedure_info in procedure_quotes:
        # If the quote is determined that the doctor makes a recommendation
        if procedure_info["recommendation"][0] == 1:
            risk_level = max(risk_level, procedure_info["severity"])

    # Now risk level is the maximum value of the risk for all drugs and medical procedures
    # TODO: add decisions regarding hospitalization, decisions not to resuscitate, 
    # and use of parenteral controlled substances

    final_risk_anal = [drug_info for drug_info in drug_quotes if drug_info["severity"] == risk_level and drug_info["recommendation"][0] == 1]
    risk_procedure_anal = [procedure_info for procedure_info in procedure_quotes if procedure_info["severity"] == risk_level and procedure_info["recommendation"][0] == 1]
    final_risk_anal.extend(risk_procedure_anal)
    end = time.time()
    print("Elapsed time : ", end - start)
    risk_anal.cursor.close()
    risk_anal.conn.close()
    return risk_level, final_risk_anal

def main():
    # Reading transcript from input file and remove diarization.
    transcript = sys.argv[1]
    ifile = open(transcript, "r")
    datalist = ifile.readlines()
    text = ''.join(line for line in datalist).lower()
    risk_level, explain = risk_anal(text)
    print("Risk level :", risk_level)
    print("Evidence: ", explain)

if __name__ == '__main__':
    main()
