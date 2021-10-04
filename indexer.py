import os
import xml.sax
from collections import Counter
import Stemmer
import sys
import time
import re
from bz2file import BZ2File

from stopwords import getStopWords
from holder import Holder

def split_on_links(text):
    text = text.split("==external links==")
    if len(text) > 1:
        return text
    if len(text) == 1:
        text = text[0].split("== external links==")
    if len(text) == 1:
        text = text[0].split("==external links ==")
    if len(text) == 1:
        text = text[0].split("== external links ==")
    return text


def split_on_references(text):
    text = text.split("==references==")
    if len(text) == 1:
        text = text[0].split("== references==")
    if len(text) == 1:
        text = text[0].split("==references ==")
    if len(text) == 1:
        text = text[0].split("== references ==")
    return text


def get_infobox(lines):
    infobox_open = False
    infobox_data = ""
    last_line_infobox = 0
    for i in range(len(lines)):
        line = lines[i].strip()
        if infobox_open and line == "}}":
            infobox_open = False
            last_line_infobox = i+1
        elif infobox_open:
            infobox_data = " ".join([infobox_data, line])
        elif not infobox_open and len(re.findall(r"\{\{infobox", line)) > 0:
            infobox_open = True
            line = re.sub(r"\{\{infobox", "", line)
            infobox_data = " ".join([infobox_data, line])
    return infobox_data, last_line_infobox

def text_preprocessing(text, stm, stopwords):
    text = text.strip().encode("ascii", errors="ignore").decode()
    text = re.sub(r"<!--.*-->", "", text)
    text = re.sub(r"&.+;", "", text)
    text = re.sub(r"`|~|!|@|#|\$|%|\^|&|\*|\(|\)|-|_|=|\+|\||\\|\[|\]|\{|\}|;|:|'|\"|,|<|>|\.|/|\?|\n|\t", " ", text) # removing non alpha numeric
    text = text.split()
    text = list(filter(lambda x: len(x) > 0 and x not in stopwords, text))
    text = stm.stemWords(text)
    return text

def get_fields(title, text, stm, stopwords):
    fields = {}
    fields["t"] = text_preprocessing(title, stm, stopwords)
    text = split_on_links(text)
    fields["l"] = []
    if len(text) > 1:
        fields["c"] = text_preprocessing(" ".join(re.findall(r"\[\[category:(.*?)\]\]", text[-1])), stm, stopwords)
        text[-1] = re.sub(r"\[\[category:(.*?)\]\]", "", text[-1])
        hyperlinks = re.findall(r"\[(.*)\]", text[-1])
        hyperlinks = " ".join(hyperlinks)
        fields["l"] = text_preprocessing(hyperlinks, stm, stopwords)
    text = text[0]
    text = split_on_references(text)
    fields["r"] = []
    if len(text) > 1:
        if "c" not in fields.keys():
            fields["c"] = text_preprocessing(" ".join(re.findall(r"\[\[category:(.*?)\]\]", text[-1])), stm, stopwords)
            text[-1] = re.sub(r"\[\[category:(.*?)\]\]", "", text[-1])
        references1 = filter(lambda x: x not in["reflist", "refbegin", "refend", "cite"], re.findall(r"\{(.*)\}", text[-1]))
        references2 = filter(lambda x: x not in["reflist", "refbegin", "refend", "cite"], re.findall(r"\[(.*)\]", text[-1]))
        references = " ".join(references1)
        references = " ".join(references2)
        fields["r"] = text_preprocessing(references, stm, stopwords)
    text = text[0]
    if "c" not in fields.keys():
        fields["c"] = text_preprocessing(" ".join(re.findall(r"\[\[category:(.*?)\]\]", text)), stm, stopwords)
        text = re.sub(r"\[\[category:(.*?)\]\]", "", text)
    text = text.split("\n")
    fields["i"], line_number = get_infobox(text)
    fields["i"] = text_preprocessing(fields["i"], stm, stopwords)
    text = " ".join(text[line_number:])
    fields["b"] = text_preprocessing(text, stm, stopwords)
    return fields

class PageHandler(xml.sax.ContentHandler):
    def __init__(self, indexpath):
        self.stopwords = Counter(getStopWords())
        self.stm = Stemmer.Stemmer('english')
        self.holder = Holder(indexpath)
        self.currentTag = ""
        self.pagecount = 0

    def startElement(self, tag, attributes):
        self.currentTag = tag
        if(tag == "page"):
            self.title = []
            self.content = []

    def endElement(self, tag):
        if(tag == "page"):
            self.title = ''.join(self.title).strip()
            self.content = ''.join(self.content)
            kdata = get_fields(self.title.lower(), self.content.lower(), self.stm, self.stopwords)
            data = [kdata['t'], kdata['i'], kdata['b'], kdata['c'], kdata['l'], kdata['r']]
            self.holder.addPageIndex(data, str(self.pagecount), self.title)
            self.pagecount += 1
     
    def characters(self, content):
        if(self.currentTag == "title"):
            self.title.append(content)
        if(self.currentTag == "text"):
            self.content.append(content)

    def endDocument(self):
        return self.holder.endHolder()

if __name__ == "__main__":
    wikipath = BZ2File(sys.argv[1])
    indexpath = sys.argv[2]
    if(not os.path.exists(indexpath)):
        os.makedirs(indexpath)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = PageHandler(indexpath)
    parser.setContentHandler(handler)
    st = time.time()
    print("Parser and indexer started")
    parser.parse(wikipath)
    print("Total time:", time.time() - st)
