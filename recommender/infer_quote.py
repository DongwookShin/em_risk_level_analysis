from recommender import DoctorRecommender
import torch
from transformers import BertTokenizer, BertForSequenceClassification

def main():
    dr = DoctorRecommender().from_pretrained()
    text = ["i was suggesting the course with the prozac for now"]
    text = ["And are you doing okay with your testosterone at home still? "]
    text = ["tell me what are your thoughts on doing some physical therapy for balance?"]
    predict = dr.predict(text)
    print(predict)



if __name__ == '__main__':
    main()