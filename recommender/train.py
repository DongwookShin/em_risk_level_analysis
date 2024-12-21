
from recommender import DoctorRecommender
import torch
from transformers import BertTokenizer, BertForSequenceClassification

def main():
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased", # Use the 12-layer BERT model, with an uncased vocab.
        num_labels = 2, # The number of output labels--2 for binary classification.
    )
    doctor_recommender = DoctorRecommender(tokenizer=tokenizer, bert_model=model)
    doctor_recommender.train("./data/annotation_second_synthetic_dedup_training.tsv", 0.2, "./recommender/pretrained", num_epochs=20, batch_size=32)



if __name__ == '__main__':
    main()