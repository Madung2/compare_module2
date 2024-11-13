from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import os

# Define the model directory where you want to save the model
model_dir = "/app/ner_model"

# Ensure the directory exists
os.makedirs(model_dir, exist_ok=True)

print(f"Downloading and saving model and tokenizer to {model_dir}...")

# Download tokenizer and save it to the specified directory
tokenizer = AutoTokenizer.from_pretrained('FacebookAI/xlm-roberta-large-finetuned-conll03-english')
tokenizer.save_pretrained(model_dir)

# Download model and save it to the specified directory
model = AutoModelForTokenClassification.from_pretrained('FacebookAI/xlm-roberta-large-finetuned-conll03-english')
model.save_pretrained(model_dir)

print("Model and tokenizer download and save completed.")