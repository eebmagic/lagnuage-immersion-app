# TODO: Make generic translator class, and then inherit from it for each specific translator
import os

from abc import ABC, abstractmethod

class BaseTranslator(ABC):
    '''
    This class is used to check that all translators have the required methods.
    '''
    @abstractmethod
    def translate(self):
        pass

class DummyTranslator(BaseTranslator):
    '''
    Just returns the same text for testing purposes.
    '''
    def __init__(self):
        self.metaName = 'dummy'
        self.ogLanguage = 'portuguese'
        self.userLanguage = 'english'

    def translate(self, text):
        return text

class Google(BaseTranslator):
    def __init__(self):
        from googletrans import Translator
        self.translator = Translator()
        self.metaName = 'googletrans'
        self.ogLanguage = 'portuguese'
        self.userLanguage = 'english'

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


class HuggingFace(BaseTranslator):
    def __init__(self, modelName='unicamp-dl/translation-pt-en-t5', pipelineType='text2text-generation'):
        self.metaName = f'huggingface/{modelName}'
        self.modelName = modelName
        self.pipelineType = pipelineType
        self.ogLanguage = 'portuguese'
        self.userLanguage = 'english'

        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        tokenizer = AutoTokenizer.from_pretrained(self.modelName)
        model = AutoModelForSeq2SeqLM.from_pretrained(self.modelName)
        self.pten_pipeline = pipeline(self.pipelineType, model=model, tokenizer=tokenizer)


    def translate(self, text):
        if type(text) == str:
            return self.pten_pipeline([text])[0]['generated_text']
        elif type(text) == list:
            return [item['generated_text'] for item in self.pten_pipeline(text)]


class HuggingFaceTranslator(BaseTranslator):
    def __init__(self, modelName='facebook/nllb-200-distilled-600M', pipelineType='translation_pt_to_en'):
        self.metaName = f'huggingface/{modelName}'
        self.modelName = modelName
        self.pipelineType = pipelineType
        self.ogLanguage = 'portuguese'
        self.userLanguage = 'english'

        # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TranslationPipeline
        self.tokenizer = AutoTokenizer.from_pretrained(modelName)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(modelName)

        self.pipeline = TranslationPipeline(task=self.pipelineType, model=self.model, tokenizer=self.tokenizer)

    def translate(self, text):
        if type(text) == str:
            # return self.model.generate(**self.tokenizer.prepare_translation_batch([text]))
            return self.pipeline([text])
        elif type(text) == list:
            # return [self.model.generate(**self.tokenizer.prepare_translation_batch([t])) for t in text]
            return self.pipeline(text)


class DeepL(BaseTranslator):
    def __init__(self):
        self.metaName = 'deepl'
        self.ogLanguage = 'portuguese'
        self.userLanguage = 'english'

        import deepl
        from dotenv import load_dotenv
        load_dotenv()
        AUTH_KEY = os.getenv('DEEPL_AUTH_KEY')

        self.translator = deepl.Translator(auth_key=AUTH_KEY)

    def translate(self, text):
        if type(text) == str:
            result = self.translator.translate_text(text, target_lang='EN-US')
            return result.text
        else:
            result = self.translator.translate_text(text, target_lang='EN-US')
            return [item.text for item in result]
