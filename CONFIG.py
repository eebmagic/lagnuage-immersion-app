from translators import DeepL
PreferredTranslator = DeepL()

from interfaces import MongoInterface
PreferredInterface = MongoInterface('mongodb://localhost:27017/')
