from typing import List
import spacy
import pytextrank


class Summariser:

    try:
        nlp = spacy.load('en_core_web_sm')
    except:
        spacy.cli.download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('textrank')
    def __init__(self, text):
        self.text = text
    @classmethod
    def clean_keyword(cls, phrase):
        if(len(phrase) < 2): return ''
        if(phrase[0] == '[' and phrase[-1] == ']'): return ''
        return phrase
    @classmethod
    def remove_duplicates(self, stuff: List[str])->List[str]:
        d = {}
        for i in stuff:
            l = i.lower()
            if(l in d): continue
            d[l] = ''
        return list(d.keys())
    def keywords(self):
        self.doc = Summariser.nlp(self.text)
        return Summariser.remove_duplicates([x.text for x in self.doc._.phrases[:50]])