import re
import sys
sys.path.append("..")
from preon.normalization import PrecisionOncologyNormalizer
from preon.drug import store_ebi_drugs, load_ebi_drugs
import timeit
import psycopg2
from configparser import ConfigParser

select_otc = "select * from drug_name_otc where name = '{}'"
select_rx = "select * from drug_name_rx where name = '{}'"
select_cs = "select * from drug_name_cs where name = '{}'"
select_tx = "select * from drug_name_tx where name = '{}'"

def load_config(filename='../database.ini', section='postgresql'):
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

def main():       
    ifile = open('./data/recommender_annotation_1404.tsv', "r")
    ofile = open('./data/recommender_annotation_1404_cleaned_3.tsv', "w")
    store_ebi_drugs("../preon/ebi_drugs.csv")
    # store_ebi_drugs("./preon/all.csv")
    drug_names, chembl_ids = load_ebi_drugs()
    normalizer = PrecisionOncologyNormalizer().fit(drug_names, chembl_ids)

    config = load_config()
    conn = connect(config)
    cursor = conn.cursor()

    lines = ifile.readlines()

    for line in lines:
        items = line.split('\t')
        drug = items[1].lower().strip()
        label = items[2].strip()
        text = items[3].lower().strip()

        text = text.replace(drug, "drug")
        text = re.sub(r"(milligram[s]*|\smg|tablet[s]*)", " ", text)
        #text = re.sub(r"(\smg)", " ", text)
        text = re.sub(r"\d+[./]?\d*", "", text)

        names = normalizer.query(text)
        drug_names = []
        if names:
            for name in names[0]:
                cursor.execute(select_otc.format(name))
                if cursor.fetchone(): # If the drug is otc drug
                    drug_names.append(name)
                else:
                    cursor.close()
                    cursor = conn.cursor()
                    cursor.execute(select_rx.format(name))
                    if cursor.fetchone(): # If the drug is rx drug
                        drug_names.append(name)
                    else:
                        cursor.close()
                        cursor = conn.cursor()
                        cursor.execute(select_cs.format(name))
                        if cursor.fetchone(): # If the drug is controlled substance drug
                            drug_names.append(name)
                        else:
                            cursor.close()
                            cursor = conn.cursor()
                            cursor.execute(select_tx.format(name))
                            if cursor.fetchone(): # If the drug is controlled substance drug
                                drug_names.append(name)
        
            if drug_names:
                for drug in drug_names:
                    text = text.replace(drug, "drug")
        
        text = ' '.join(text.split())
        print(text + "|||" + label)
        ofile.write(text + "\t" + label + "\n")

    ofile.close()

if __name__ == '__main__':
    main()
