import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, accuracy_score, classification_report
from sklearn.metrics import f1_score
import csv
import pickle
from sklearn import metrics

def train(trainfile_name):

    r = csv.reader(open(trainfile_name, 'r'), quotechar='\'', delimiter='\t')
    text = []
    label = []
    for row in r:
        text.append(row[0])
        label.append(int(row[1]))
    
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), lowercase=True, max_features=150000)
    tfidf = vectorizer.fit_transform(text)

    logit = LogisticRegression(C=5e1, solver='lbfgs', multi_class='multinomial', random_state=17, n_jobs=4)
    logit.fit(tfidf, label)

    with open('./lrmodel/lrmodel.pkl', 'wb') as f:
        pickle.dump(logit, f)
    
    with open('./lrmodel/lrvectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)


def test(testfile_name):
    r = csv.reader(open(testfile_name, 'r'), quotechar='\'', delimiter='\t')
    text = []
    label = []
    for row in r:
        text.append(row[0])
        label.append(int(row[1]))
    
    with open('./lrmodel/lrmodel.pkl', 'rb') as f:
        logit = pickle.load( f)
    
    with open('./lrmodel/lrvectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load( f)
        # text_transformer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), lowercase=True, max_features=150000)
        X_test_text = vectorizer.transform(text)
        y_pred = logit.predict(X_test_text)

        confusion_matrix = metrics.confusion_matrix(label,  y_pred)
    print("Confusion Matrix:")
    print(confusion_matrix)
    print("accuracy:",accuracy_score(label, y_pred) )
    print("precision_score1:",precision_score(label, y_pred) )
    print("recall_score1:",recall_score(label, y_pred) )
    print("f1_score1:",f1_score(label, y_pred) )
    print("f1_score1:",classification_report(label, y_pred) )

def main():
    # train("./data/train_cleaned_1000_3.tsv")
    test("./data/test_cleaned_404_3.tsv")


if __name__ == '__main__':
    main()