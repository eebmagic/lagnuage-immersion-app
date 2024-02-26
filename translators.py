class Google:
    def __init__(self):
        from googletrans import Translator
        self.translator = Translator()

    def translate(self, text):
        '''
        Default translator function, using googletrans (a free python wrapper for Google Translate).
        This can be swapped out for a different translator if desired.
        '''
        translationResult = self.translator.translate(text, src='pt', dest='en')

        return translationResult.text


class HuggingFace:

    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        tokenizer = AutoTokenizer.from_pretrained("unicamp-dl/translation-pt-en-t5")
        model = AutoModelForSeq2SeqLM.from_pretrained("unicamp-dl/translation-pt-en-t5")
        self.pten_pipeline = pipeline('text2text-generation', model=model, tokenizer=tokenizer)

    def translate(self, text):
        return self.pten_pipeline(text)
