from translators import DeepL
PreferredTranslator = DeepL()

from exporters import MongoExporter
PreferredExporter = MongoExporter('mongodb://localhost:27017/')
