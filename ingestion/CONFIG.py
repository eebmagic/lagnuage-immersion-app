# from translators import DeepL
# PreferredTranslator = DeepL()
from translators import DummyTranslator
PreferredTranslator = DummyTranslator()

from interfaces import MongoInterface
PreferredInterface = MongoInterface('mongodb://localhost:27017/')
