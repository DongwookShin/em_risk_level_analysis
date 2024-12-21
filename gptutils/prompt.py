def generate_prompt_problem(input_passage):
    content1 = f"""You are a medical expert. First, identify the single central patient in the following transcript and give a bulleted list of the main problems that this patient is having. Also let me know whether each problem was addressed by the medical provider.

Transcript:
```
{input_passage}
```
"""

    content2 = """
In medical decision making a problem is defined as "a disease, condition, illness, injury, symptom, sign, finding, complaint, or other matter addressed at the encounter, with or without a diagnosis being established at the time of the encounter."

Create a valid JSON with the following format:
[
    {
        "what are the main problems?": [<main problems and conditions affecting the patient.>],
        "what are the main drugs the provider prescribes for the problems?" [<drugs that doctor prescribe to treat the problems>],
        "short quote of <problem>": ...,
    },
    {
        ...
    },
    ...
]

For each "what are the main problems", you should have a "problem" entry.

Think step by step:
- Be aware that the transcript might also discuss other patients.
- Extract main problems of the primary patient.
"""

    return [
        {"role": "system", "content": ""},
        {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_diagnosis(input_passage):
    content1 = f"""Please identify the single central patient in the following transcript and generate a list of diagnostic procedures \
and management that are ordered or prescribed by the current physician or on-going in the transcript. \
And please note that the diagnostic procedures and management that were already done in the past should not be included in the output.
Diagnostic procedures are specific medical tests, examinations, or investigations aimed at identifying or confirming a medical condition or disease. \
Examples of diagnostic procedures include blood tests, imaging studies (X-ray, MRI, CT scan), biopsies, and genetic testing.
Management refers to specific actions taken to treat or manage a diagnosed condition. \
Examples of Management include medication prescriptions, surgical procedures, chemotherapy, physical therapy sessions, and specific lifestyle modifications like dietary restrictions or exercise regimens. 

    Transcript:
    ```
    {input_passage}
    ```
    """

    content2 = """
  After analyzing the transcript, create a JSON that consists of a list of dictionaries with the following keys: "name", "type", "short quote", "involved drug". \
The "name" key represents the specific diagnostic procedure or management intervention that the physician orders or prescribes. \
The "type" key should be one of "order for prescription", "order for further test", "order for surgery", or "medical recommendation"\
If doctor says "refill the drug" or "order the drug", the type should be "order for prescription". \
The "short quote" is the short quote from the transcript that corresponds to the "name".\
The "involved drugs" should include all the names of the drugs mentioned in this quote. Please specify the drug names like "flunazole" or "jardiance". \ 
Any supplement mentioned in the quote should be included here.
And please note that the diagnostic procedures and management that were already done in the past should not be included in the JSON. \ 
Here are some examples that were done in the past and should not be included:
"They put you on some medicine", "So back in December, you had chest pain. Went to the hospital.", "Thy put two stents in." 
On the contrary, herre are some examples that are being ordered or prescribed from the current physicians and should be included:
"I am going to refill ...", "I am going to put you on ...", "You need statin to control cholesterol". or "Why don't we try Ozempic?".
Your output should be only a JSON, and it should look like this: \
[ \
{"name": ..., "type": ..., "short quote": ..., "involved drugs": ...,}, \
... \
] \

And list the items in the same order as it appears in the transcript.

    """ 

    return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_risk(input_json, drug_list):

    content1=f"""
These are levels of risk:
Risk level is minimal when  the passage mentions  procedures with virtually no morbidly risk such as applying superficial dressings or recommending patient rest.
Risk level is low when  the passage mentions  procedures that require a needle (blood draw, give IV fluids) or require some movement (physical therapy).
Risk level is moderate when the passage mentions prescription drug management (ordering, refilling, increasing dosage, decreasing dosage etc), decisions regarding minor surgery, or treatment significantly limited by social determinants of health.
Risk level is high when the passage mentions drug therapy that requires monitoring for toxicity, decisions about major surgery, decisions regarding hospitalization, decisions not to resuscitate, and use of parenteral controlled substances.


INPUTS:
You have two inputs: first input is a JSON where each entry of which is a dictionary composed of three keys: name, type and short quote.
and second input is another JSON that lists three keys: first is the list of high-risk drugs, second is list of other prescription drugs and the third is over-the-counter drugs.
```
    
    Diagnostic information:
```
{input_json}
```
   Drug information :
```
{drug_list}
```

"""


    content2="""
```

Now for each entry in the first input, classify it into a risk level using the risk level information given above and drug information given as the second input.
Each entry of output JSON should have four keys, "name",  "type", "short quote", and "risk".
The first three come from the same keys in the diagnostic information.
The fourth key is the "risk" level of the first key, which is one of 'minimal', 'low', 'moderate', or 'high'.
When determining the risk level, consult the drug list presented in the second input and the guideline of risk level carefully.
Make sure all the prescription drug management should belong to moderate risk. If those require toxicity monitoring like cancer drug, it should be high risk. If the drug is over-the-counter drug, the risk should be low.
Your output should be a JSON, and it should look like the following format. Remove all the unnecessary information that does not fit in the following JSON format. Please do not copy input into the output.\
[
  {
    "name": ...,
    "type": ...,
    "short quote": ...,
    "risk": ...,
  },
  ...
]

"""

    return [
        {"role": "system", "content": ""},
        # {"role": "user", "content": content1},
        {"role": "user", "content": content1 + content2},
    ]


def generate_prompt_drug(input_passage):
    content1 = f"""Please extract all the drugs or drug classes discussed in the transcript and classify those into three categories: "high-risk drug", prescription drugs and over-the-counter drug. \
a
    Transcript:
    ```
    {input_passage}
    ```
    """

    content2 = """
  After analyzing the transcript, create a JSON output that has three categories about drugs:\ 
  (1) High-risk drugs are drugs that require monitoring toxicity like cancer drugs. (2) Prescription drugs are the drugs that are only avaiable by prescription like Ozempic, Jardiance. \
  (3) Over-the-counter or otc drugs are the drugs that can be bought without prescription like Advil, Tyrenol. 
  Make sure you include all the drugs or drug classes mentioned in the transcript.
  Your output should be only a JSON, and it should look like this: \
{
  "high-risk drugs": <list of all drugs or drug classes that requires monitoring toxicity like cancer drugs>,
  "prescription drugs": <list of other prescription drugs or drug classes>. Carefully review each drug information and do not add any over-the-counter (otc) drug here.,
  "otc drugs": <list of all over-the-counter (otc) drugs or drug classes>. Carefully review each drug information and do not add any prescription drug here, 
}
    """ 

    return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_all_drug(input_passage):
    content1 = f"""Please extract all the drugs or surgical procedure discussed in the transcript. \
a
    Transcript:
    ```
    {input_passage}
    ```
    """

    content2 = """
  After analyzing the transcript, create a JSON output that has all the extracted drugs, but do not include add a very general term like "sugar", or "supplement". 
  If a drug name is spelled incorrectly, please write correct drug names.
{
  "drugs": <list of all drugs>,
}
    """ 

    return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]


def generate_prompt_all_drugs_and_correct_names(input_passage):
    content1 = f"""Please extract all the drugs or surgical procedure discussed in the transcript. \
a
    Transcript:
    ```
    {input_passage}
    ```
    """

    content2 = """
  After analyzing the transcript, create a JSON output that has all the extracted drugs or surgical procedure.
These should not be included in JSON output as well: Enzymes, proteins like PSA, lipoprotein like cholesterol, LDL, HDL, triglycerides, LDLP, LDLC or hormones like cortisol, testosterone, estrogen.
If a drug name is spelled incorrectly in the transcript, please fix it and write correct drug name. 
But do not arbitrarily connect two drugs and make one drug by using hypen between two drug names.
For instance, in the quote 'Was it carbidopa, levodopa', two drugs 'carbidopa' and 'levodopa' are mentioned. Do not make 'carbidopa-levodopa'.
  Each drug or surgecal procedure should have three keys:
  "drug name" is the correct name of a drug or surgecal procedure,
  The "short quote" is the short quote from the transcript that mentions the "drug name" and from which you extract the drug name.\
 If there are multiple quotes for the same drug, include all of these, so that a drug can have multiple instances in the JSON output.
 
[
    {
      "drug name": <drug names>,
      "short quote": <short quote from the transcript>
    },
...
]

  Makre sure if the drug names extracted have typo, correct those as well. For example, if the drug name is "semigotide", correct it as "semaglutide".
    """ 

    return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_all_drugs_and_correct_names_2(input_passage):
    content1 = f"""Please extract all the drugs or surgical procedure discussed in the transcript. \
a
    Transcript:
    ```
    {input_passage}
    ```
    """

    content2 = """
  After analyzing the transcript, create a JSON output that has all the extracted drugs or surgical procedure.
These should not be included in JSON output as well: Enzymes, proteins like PSA, lipoprotein like cholesterol, LDL, HDL, triglycerides, LDLP, LDLC or hormones like cortisol, testosterone, estrogen.
If a drug name is spelled incorrectly in the transcript, please fix it and write correct drug name. 
But do not arbitrarily connect two drugs and make one drug by using hypen between two drug names.
For instance, in the quote 'Was it carbidopa, levodopa', two drugs 'carbidopa' and 'levodopa' are mentioned. Do not make 'carbidopa-levodopa'.
  Each drug or surgecal procedure should have three keys:
  "drug name" is the correct names of a drugs or surgecal procedures,
  "status" key indicates one of three status: "checked history" if the physician mentioned it as a drug that patient took in the past, "discussed" if the physician discussed the possibility of the use of drug withoug recommending the drug,
 "recommended" if the current doctor recommends the drug. If the doctor does not recommend the drug, do not include the quote here. 
 The "short quote" is the short quote from the transcript that mentions the "drug names" and from which you extract the drug name.\
 The short quote should not be more than three sentences.
 If there are multiple quotes for the same drug, include the most relevant quotes. In another words, if there is a quote for a drug whose status is recommended,
 include it and ignore all the quotes of the same drug whose status is either "discussed" or "checked history". 
 
[
    {
      "drug name": <drug names>,
      "status": <one of "checked history", "discussed", or "recommended">,
      "short quote": <short quote from the transcript>
    },
...
]

  Makre sure if the drug names extracted have typo, correct those as well. For example, if the drug name is "semigotide", correct it as "semaglutide".
    """ 

    return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_classify_drug(drug_list):
    content1 = f"""For each drug in the drug list, classify the drugs into four categories. \
  (1) High-risk drugs are drugs that require monitoring toxicity like cancer drugs. 
  (2) Prescription drugs are the drugs that are only avaiable by prescription like Ozempic, Jardiance. \
  (3) Over-the-counter or otc drugs are the drugs that can be bought without prescription like Advil, Tyrenol. 
  (4) "non-drugs": <list of all others that do not belong to the above three categories

    Drugs:
    ```
    {drug_list}
    ```
"""
    
    content2 = """
  Your output should be only a JSON, and it should look like this: \
{
  "high-risk drugs": <list of all drugs or drug classes that requires monitoring toxicity like cancer drugs, Anastrozole or Letrozole>,
  "prescription drugs": <list of other prescription drugs or drug classes>. Carefully review each drug information and do not add any over-the-counter (otc) drug here.,
  "otc drugs": <list of all over-the-counter (otc) drugs or drug classes>. Carefully review each drug information and do not add any prescription drug here, 
  "non-drugs": <list of all others that do not belong to these three categories>.
}
"""
    return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_all_disease(input_passage):
    content1 = f"""Please extract all disease that patient have right now by reading the transcript. \
a
    Transcript:
    ```
    {input_passage}
    ```
    """

    content2 = """
  After analyzing the transcript, create a JSON output that lists all the disease the patient have. If the disease is existing when the patient visit the doctor, then the status needs to be "current".
  If the disease has been resolved, the status should be "resolved".

  [
    {
    "disease": <name of disease>,
    "status": <One of "current" or "resolved">
    },
    ...
  ]  
    """ 

    return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]


def generate_prompt_drug_quotes(drug_list, transcript):
    
  content1 = f"""You will be given a transcript of a medical appointment (delimited by triple backticks below), and a list of drugs (also delimited by triple backticks below). 
  Your task is to find all quotes for each drug in the drug list that the doctor says.

  Transcript:
  ```
  {transcript}
  ```

  Drug list:
  ```
  {drug_list}
  ```
  """
  
  content2 = """
  Your output should be only a valid JSON list that is the list of the drug name and quote pair and it should look like below: \
  [
    {
       "drug name": <each drug name in the drug list>,
       "quote": <a quote that include the drug in the transcript>
    },
    ...
  ]
If there are multiple quote for a drugs, you should include all the "drug name", "quote" pair multiple times with the same drug name.
  """
  return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_procedure_quotes(procedure_list, transcript):
    
  content1 = f"""You will be given a transcript of a medical appointment (delimited by triple backticks below) and list of procedures. 
  Your task is to find all quotes for each procedure in the procedure list that the doctor says.

  Transcript:
  ```
  {transcript}
  ```
    Procedure list:
  ```
  {procedure_list}
  ```
  """
  
  content2 = """
Your output should be only a valid JSON list that is the list of the procedure name and quote pair and it should look like below: \
  [
    {
       "medical procedure": < each procedure name in the procedure list >,
       "quote": <a quote that mentions the medical procedure in the transcript>
    },
    ...
  ]
If there is no pair that meets the criteria, return [].
  """
  return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_surgery_quotes(transcript):
    
  content1 = f"""You will be given a transcript of a medical appointment (delimited by triple backticks below). 
  Your task is to find all surgeries (major or minor) 
  that doctor mentions, their CPT code, quotes for those surgeries and determine if the surgery is minor or major based upon global days
  assigned by CMS.

  Transcript:
  ```
  {transcript}
  ```
  ```
  """
  
  content2 = """
  Your output should be only a valid JSON list that is the list of minor or major surgeries, their CPT codes, quote pair and severity and it should look like below: \
  [
    {
       "surgery": < minor or major surgeries>,
       "cpt code": <Cpt code of the surgery>,
       "quote": <a quote that mentions the surgery in the transcript>
       "severity": <minor or major based upon global days assignment by CMS>
    },
    ...
  ]
  Please remember "do not include any test" in the list because those are not surgeries.
And if you cannot find the CPT code for surgery, do not include it with CPT code "N/A" because it is not a surgery defined by CMS.
  """
  return [
    {"role": "system", "content": ""},
    # {"role": "user", "content": content1},
    {"role": "user", "content": content1 + content2},
    ]

def generate_prompt_surgery(transcript_text):
    content1 = f"""You are a medical expert. Your task is to identify surgeries in the following transcript. 

Surgery is a medical procedure involving the use of instruments to make incisions or perform manipulations on body tissues to diagnose, treat, or repair physical conditions. It often requires a sterile environment, specialized surgical instruments, and, in most cases, anesthesia to ensure patient comfort. Surgery can be either invasive (involving cuts or incisions) or minimally invasive (using smaller incisions or specialized instruments like scopes).

Minor surgeries are usually less invasive, with low risk and typically performed on an outpatient basis. These procedures are often brief, require local anesthesia, and generally do not involve extensive recovery periods. Examples of minor surgeries are: mole or cyst removal, biopsy, carpal tunnel release, wound debridement, laparoscopic tubal ligation

Major surgeries are more complex, generally requiring general anesthesia, a longer recovery time, and often involve critical organs or systems. They typically require hospital admission and specialized surgical teams. Examples of major surgeries are: coronary artery bypass grafting (CABG), hip or knee replacement, organ transplant, spinal fusion, hysterectomy, mastectomy.

Transcript:
```
{transcript_text}
```
"""

    content2 = f"""


Create a valid JSON with the following format:
[
    {{
        "surgery": <name of the surgery>,
        "does the surgery have a specific medical name?": <yes|no>,
        "is this a non-surgical procedure?": <yes|no>,
        "is this a diagnostic procedure?": <yes|no>,
        "short quote of <surgery>": ...
    }},
    ...
]    
"""
    return [
        {"role": "system", "content": ""},
        {"role": "user", "content": content1 + content2},
    ]

"""
Instructions:
- The output JSON can only contain medical problems listed in the above "List of medical problems".
- If a particular problem has no associated sub_problems, then just list the problem as a stand-alone "main_problem".
"""