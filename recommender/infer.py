from recommender import DoctorRecommender
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import csv

def main(testfile_name):
    dr = DoctorRecommender().from_pretrained()
    r = csv.reader(open(testfile_name, 'r'), quotechar='\'', delimiter='\t')
    text = []
    label = []
    count = 1
    for row in r:
        try:
            text.append(row[0])
            label.append(int(row[1]))
        except:
            print(count)
            print(row)
        count += 1
    predict = dr.predict(text)
    m = DoctorRecommender().compute_metrics(label, predict)
    print(m)
    # DoctorRecommender()._false_negative(text, label, predict)
    DoctorRecommender()._false_positive(text, label, predict)



if __name__ == '__main__':
    main("./data/test_cleaned_404_3.tsv")