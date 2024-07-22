'''
Set some constants to be used throughout the ingestion process here.

PreferredTranslator: The translation class to use when generating translations.

PreferredInterface: Where to store the translation results.
'''
from translators import DummyTranslator
# from translators import DeepL
from interfaces import MongoInterface

# PreferredTranslator = DeepL()
PreferredTranslator = DummyTranslator()

PreferredInterface = MongoInterface('mongodb://localhost:27017/')
