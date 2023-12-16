import pandas as pd 
import argparse 

from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
torch.device('cuda')

# - Utils
prompt = f"""
###User: 
Prerequisites: BIOL 202 or BIOL 302; BIOL 219 or BIOL 200 plus either BIOL 201 or ANAT212/BIOC212 

###Answer: 
['&', ['|', 'BIOL 202', 'BIOL 302'], ['|', 'BIOL 219', 'BIOL 200'], ['|', 'BIOL 201', 'ANAT 212', 'BIOC 212']]

###User: 
Prerequisites: BIOC 212 or ANAT 212 or BIOL201, ANAT 262, one of PHGY 209 or BIOL 205; one of BIOC 312 or ANAT 365; BIOC 311 recommended 

###Answer: 
['&', ['|', 'BIOC 212', 'ANAT 212', 'BIOL 201'], 'ANAT 262', ['|', 'PHYG 209', 'BIOL 205'], ['&', 'BIOC 312', 'ANAT 365']]

###User: 
Prerequisite: Successful completion of any Survey of Literature (HISP 241, HISP 242, HISP 243, HISP 244) or permission of the instructor. Note: Course taught in Spanish. 

###Answer: 
['|', 'HISP 241', 'HISP 242', 'HISP 243', 'HISP 244']

###User: 
Corequisite: NRSC/BIOL 451 and ANTH/GEOG 451.

###Answer: 
['&', ['|', 'NRSC 451', 'BIOL 451'], ['|', 'ANTH 451', 'GEOG 451']]

####User:
Prerequisite: COMP 202 and COMP 250 or permission of instructor.

###Answer:
['&', 'COMP 202', 'COMP 250']

####User:
Prerequisite: COMP 202 and COMP 250.

###Answer:
['&', 'COMP 202', 'COMP 250']

####User:
Corequisite: COMP 202 or COMP 250.

###Answer:
['|', 'COMP 202', 'COMP 250']

####User:
Prerequisite: COMP 202 and COMP 206) or COMP 250.

###Answer:
['|', ['&', 'COMP 202', 'COMP 206'], 'COMP 250']

####User:
Prerequisite: COMP 202.

###Answer:
'COMP 202'

###User: 
Prerequisites: MATH 251 or MATH 247, and MATH 248 or MATH 314 or MATH 358 

###Answer: 
['&', ['|', 'MATH 251', 'MATH 247'], ['|', 'MATH 248', 'MATH 314', 'MATH 358']]


###User: 
Prerequisite: JWST 340 or permission of instructor.

###Answer: 
'JWST 340'

###User: 
Prerequisites: ECSE 205, COMP 206, ECSE 250, and (ECSE 343 or MATH 247) or equivalents. 

###Answer: 
['&', 'ECSE 205', 'COMP 206', 'ECSE 250', ['|', 'ECSE 343', 'MATH 247']]

####User:
Prerequisite: MATH 323D1/D2.

###Answer:
['&', 'MATH 323D1', 'MATH 323 D2']

####User:
Prerequisite: MATH 350 and MATH 323D1/D2.

###Answer:
['&', 'MATH 350', 'MATH 323D1', 'MATH 323 D2']

####User:
Prerequisite: MATH 350 and optionally more MATH classes.

###Answer:
'MATH 350'

####User:
Prerequisite: BIEN 350 or Permission of Instructor.

###Answer:
'BIEN 350'
"""

def infer(pipeline, string):

    print(f"running inference on {string}...")

    sequences = pipeline(
                f"{prompt}\nUser:\n{string}\n###Answer:\n",
                top_k=1,
                num_return_sequences=1,
                eos_token_id=tokenizer.eos_token_id,
                max_new_tokens=400)
               

    print("inference done")

    res = sequences[0]['generated_text'].removeprefix(prompt).strip().split("\n")[3]

    print(res)

    return res 

# - Experiments

parser = argparse.ArgumentParser()

parser.add_argument('--path', default="./test.csv")
parser.add_argument('--model', default="./models/fine_tuned_llama2_7b")

args = parser.parse_args()

print("loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(args.model)
print("tokenizer loaded")

print("loading pipeline...")
pipeline = transformers.pipeline(
            "text-generation",
            model=args.model,
            torch_dtype=torch.float16,
            device_map="auto"
)
print("pipeline loaded")

data = pd.read_csv(args.path)

indices = data["index"].to_list()
requisites = data["requisite"].to_list()

print("Starting inference on test set")
pred = [infer(pipeline,req) for req in requisites]
print("inference done")

pred_df = pd.DataFrame({
        "index": indices,
        "prediction": pred
        })

pred_df.to_csv("./llama2_finetuned_pred.csv")

