import os
from urllib.parse import urlparse
from datetime import datetime
import numpy as np
from transformers import BertTokenizerFast, TrainingArguments, Trainer, BertForSequenceClassification
import torch
import pkg_resources
import csv
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

#  Create The Dataset Class.
class TheDataset(torch.utils.data.Dataset):

    def __init__(self, texts, values, tokenizer):
        self.texts    =  texts
        self.values = values
        self.tokenizer  = tokenizer
        self.max_len    = tokenizer.model_max_length

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        text = str(self.texts[index])
        value = self.values[index]

        encoded_text = self.tokenizer.encode_plus(
            text,
            add_special_tokens    = True,
            max_length            = self.max_len,
            return_token_type_ids = False,
            return_attention_mask = True,
            return_tensors        = "pt",
            padding               = "max_length",
            truncation            = True
        )

        return {
            'input_ids': encoded_text['input_ids'][0],
            'attention_mask': encoded_text['attention_mask'][0],
            'labels': torch.tensor(value, dtype=torch.long)
        }


class DoctorRecommender(object):

    def __init__(self, root_dir='.', max_length=128, learning_rate=0.0001, tokenizer=None, bert_model=None, augment_data=False):
        self.root_dir = root_dir
        self.max_length = max_length
        self.learning_rate = learning_rate
        self.initial_epoch = 0

        self.tokenizer = tokenizer
        self.bert_model = bert_model

    def train(self, trainfile_name, valid_ratio, ckpt_name, num_epochs=10, batch_size=128, steps_per_epoch=1000, quiet=False, log=False):
        # df = pd.read_csv(trainfile_name, sep='\t', engine='python')
        # df = df.dropna()
        r = csv.reader(open(trainfile_name, 'r'), quotechar='\'', delimiter='\t')
        text = []
        label = []
        for row in r:
            text.append(row[0])
            label.append(int(row[1]))

        # split train dataset into train, validation and test sets
        train_text, valid_text, train_labels, valid_labels = train_test_split(text, label,
                                                                    random_state=2018,
                                                                    test_size=valid_ratio,
                                                                    stratify=label)

        train_dataset = TheDataset(
            texts    = train_text,
            values = train_labels,
            tokenizer  = self.tokenizer,
        )

        valid_dataset = TheDataset(
            texts    = valid_text,
            values = valid_labels,
            tokenizer  = self.tokenizer,
        )

        training_args = TrainingArguments(
            output_dir                  = ckpt_name,
            num_train_epochs            = num_epochs,
            per_device_train_batch_size = batch_size,
            per_device_eval_batch_size  = batch_size,
            warmup_steps                = 500,
            weight_decay                = 0.01,
            save_strategy               = "steps",
            save_steps=250,
            evaluation_strategy         = "steps"
        )

        trainer = Trainer(
            model           = self.bert_model,
            args            = training_args,
            train_dataset   = train_dataset,
            eval_dataset    = valid_dataset,
            compute_metrics = self._compute_metrics
        )

        trainer.train()
    
    def predict(self, text, return_probs=False):
        trainer = Trainer( model  = self.bert_model)
        # trainer = Trainer( model  = model)

        test_dataset = TheDataset(
           texts    = text,
           values = [1]*len(text),
           tokenizer  = self.tokenizer
        )
        # Make prediction
        raw_preds, _, _ = trainer.predict(test_dataset)
        y_preds = np.argmax(raw_preds, axis=1)
        results = []
        for idx, y_pred in enumerate(y_preds):
            results.append(y_pred)

        return results

    @staticmethod
    def from_pretrained():
        path_lookup = pkg_resources.resource_filename(__name__, 'pretrained') 
        # print('Checking for checkpoint at: {}'.format(path_lookup))
        if os.path.exists(path_lookup):
            fpath = path_lookup
        else:
            raise Exception('No such file exists: {}'.format(fpath))

        print('Checking for checkpoint at: {}'.format(fpath))
        bert_model = BertForSequenceClassification.from_pretrained(fpath)
        tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
        return DoctorRecommender(bert_model=bert_model,tokenizer=tokenizer)

    @staticmethod
    def _compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='macro')
        acc = accuracy_score(labels, preds)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    @staticmethod
    def compute_metrics(labels, preds):
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='macro')
        acc = accuracy_score(labels, preds)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    @staticmethod
    def _false_negative(text, label, pred):
        total_p =  0
        total_n = 0
        for count, l in enumerate(label):
            if l ==1 and pred[count] == 0:
                print(text[count])
                total_n += 1
            if l == 1:
                total_p += 1
        
        print(total_p, ",", total_n)

    @staticmethod
    def _false_positive(text, label, pred):
        total_p =  0
        total_n = 0
        for count, l in enumerate(label):
            if l ==0 and pred[count] == 1:
                print(text[count])
                total_n += 1
            if l == 1:
                total_p += 1
        
        print(total_p, ",", total_n)

