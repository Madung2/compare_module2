def ner_model(model_dir):
    # Load tokenizer and model from the specified path
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)  # Load tokenizer locally
    model = AutoModelForTokenClassification.from_pretrained(model_dir, local_files_only=True)  # Load model locally
    ner = pipeline("token-classification", model=model, tokenizer=tokenizer)
    return ner

model_name  = "/app/ner_model"
ner = ner_model(model_name)

