python3 sft_finetune.py \
  --model_name meta-llama/Llama-2-7b-hf \
  --dataset_name saamenerve/mcgill-requisites --dataset_text_field instruction --load_in_4bit \
  --use_peft \
  --batch_size 2 \
  --gradient_accumulation_steps 2 >>./log/sft_finetune.log
