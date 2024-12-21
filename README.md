# med_risk_level_analysis

In order to run this package, several applications needs to be installed and prepared properly.

(1) Install python packages using the folliwing command.
```
    % pip install -r requirements.txt
```

(2) PostgreSQL needs to be installed first. Change password of user "postgres" as shown in "database.ini". Next, database drug_db needs to be created. After that, the dumpfile "./database/drug.sql" needs to imported as:
```
    % createdb -h hostname -U postgres drug_db
    % psql -h hostname -d drug_db -U postgres -f ./database/drug.sql
```

(3) Install preon using "pip install preon". If that does not work, use the preon that is locally copied. In that case, find the preon drug file named "ebi_drugs.csv" at S3 bucket "med-ai-internal/sandbox/dwshin/", create a directory ./preon/resources and copy the drug file to "./preon/resources".

(4) Download the spaCy model "en_core_web_sm" with the command:
```
    % python -m spacy download en_core_web_sm
```

(5) Check if the spaCy rule based file named "procedure.jsonl" is in the directory "./spacy". This is the file that allows to extract procedures from transcripts. If there is no file or the file is not up-to-date, the latest file is stored in S3 bucket "med-ai-internal/sandbox/dwshin/ and should be copied to the directory.

(6) Copy the BERT trained model for recommendation classifier. The model files (config.json, model.safetensors, optimizer.pt, rng_state.pth, schedule.pt, trainer_state.json and training_args.bin) are found at S3 bucket "med-ai-internal/sandbox/dwshin/". Create a directory "./recommender/recommender/pretrained/" and "copy those model files to the directory "./recommender/recommender/pretrained/".

(7) Go to the recommender directory and run the following command.
```
    % python test_annotation_yes.py
```

    You need to see the lines like this and all the first colums should be "yes"
```
    yes     |  So then you need refill.
    yes     |  So then she's going to need to refill.
    yes     |  We'll send another vial and then we'll do 0.2. 
    ...
```

(8) Test if GPT is set properly and returns an answer without error:
```
    % python utils/test_drug.py 
```

(9) You can run the EM risk level analysis program using the following command.
```
    % python em_risk_analysis.py <input_transcript_file_name>
```



