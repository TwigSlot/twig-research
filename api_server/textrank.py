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
    def keywords(self):
        self.doc = Summariser.nlp(self.text)
        d = {}
        cnt = 0
        for i in self.doc._.phrases:
            l = i.text.lower()
            print(l)
            if(l in d): continue
            d[l] = ''
            cnt+=1
            if(cnt > 50): break
        return list(d.keys())
        # remove duplicates