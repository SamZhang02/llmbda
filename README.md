# llmbda
Welcome to the  repository for the McGill University COMP550 Natural Language Processing project "llmbda". This repository contains all the code and resources required to replicate the findings and experiments presented in the report.

<p align='center'>
  <img src="https://github.com/SamZhang02/llmbda/assets/112342947/b1b7fa0e-3a19-4b24-8465-e2918ec47c0c" width=250/>
</p>

<p align="center">
    <a href="https://github.com/SamZhang02/report/Report.pdf">Project Report</a>
</p>

Since late 2022, large language models (LLMs) like ChatGPT have gained popularity in research and industry uses due to their ability to perform diverse natural language processing tasks with human-like proficiency. In this study, we investigate the ability to understand logic of various large language models, including open-source ones like Llama 2 and closed-source models such as GPT and Gemini, on the task of parsing semi-formal natural language into propositional logic. Our analysis compared different alignment methods: zero-shot and few-shot prompting, and supervised fine-tuning. 

We observe that LLMs performed well in these tasks, LLMs can understand logical semantics with appropriate training data, especially when fine-tuned with a dedicated dataset. However, chat-instruct and general-purpose LLMs suffer from inconsistent performance on this task.

Our findings suggests that there may be potential downstream engineering and research use cases for LLMs for semantic related tasks, given its understanding of logic. 

## Environment Setup
### Prerequisites

#### Prompt engineering scripts 
These make calls to the official OpenAI and Google APIs, and do not have specific system requiremenets. 

#### Fine-tuning Llama2  
System requirements:
- Ubuntu (Some libraries used in huggingface's Transformer's API require Linux)
- CUDA (torch devices are set to CUDA)

### Virutal Environment
Dependency management is done using [poetry](https://python-poetry.org/docs/basic-usage/), dependencies can be installed via:

```shell
poetry install
```

To run a script, use: 

```shell
poetry run python3 <?.py>
```

## Training 
Experiment scritps are located under `/experiments`, each experiment have their own scritpt. Only the Llama finetuning requires local trainning. 

### Llama fine-tune scripts 
Make note of the Llama fine tune scripts, where it uses the `sft_finetune.py` scripts from Huggingface. To run it with the same options as the experiment, run the bash script.

```shell
experiments/llama2/finetune.sh
````

Additonally, you can experiment with different options in the bash script. 

#### Handling CUDA OOM
Our setup ran on a single RTX 3060 12GB. To reduce memory usage, try reducing the batch size in the bash script. 

## Evaluation
Evaluation is pipelines with the `eval.py` script. Simply run `eval.py` with desired options 

```shell
model_name             the name of the model 
label_path             The path where the correct labeled csv is located 
pred_path              The path where the predictions csv is located 
--log_result           Option to indicate whether we save the result in a text file. Default is False. 
--ans_text_field       Column name of the correct labels in the labeled csv. Default is 'object_tree'.
--pred_text_field      Column name of the correct labels in the prediction csv. Default is 'predictions'.
--join_on              The key column name to join the two csv on. Default is 'index'.
```

a sample eval script is located in the `justfile`, you can run it with 

```shell
just eval {{model_name}} {{pred_path}}
```
## Project Report 
For a comprehensive understanding of our project, methodologies, and detailed results, please refer to our [project report](https://github.com/SamZhang02/report/Report.pdf).
