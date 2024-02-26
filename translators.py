class Google:
    def __init__(self):
        from googletrans import Translator
        self.translator = Translator()

    def translate(self, text):
        '''
        Default translator function, using googletrans (a free python wrapper for Google Translate).
        This can be swapped out for a different translator if desired.
        '''
        if type(text) == str:
            translationResult = self.translator.translate(text, src='pt', dest='en')
        else:
            translationResult = [self.translator.translate(t, src='pt', dest='en') for t in text]

        return translationResult.text


class HuggingFace:

    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        tokenizer = AutoTokenizer.from_pretrained("unicamp-dl/translation-pt-en-t5")
        model = AutoModelForSeq2SeqLM.from_pretrained("unicamp-dl/translation-pt-en-t5")
        self.pten_pipeline = pipeline('text2text-generation', model=model, tokenizer=tokenizer)

    def translate(self, text):
        if type(text) == str:
            return self.pten_pipeline(text)['generated_text']
        elif type(text) == list:
            return [item['generated_text'] for item in self.pten_pipeline(text)]
