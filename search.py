import sys
from collections import Counter
import os
import Stemmer
import numpy as np
import json
import math
import time

from stopwords import getStopWords

def preprocessStr(body, stm, stopwords):
    body = body.lower()
    tbody = []
    for ch in body:
        if((ch >= 'a' and ch <= 'z') or ch == ' ' or (ch >= '0' and ch <= '9')):
            tbody.append(ch)
        else:
            tbody.append(' ')
    tbody = ''.join(tbody).split()
    return [stm.stemWord(word) for word in tbody if word not in stopwords]

def queryParse(query):
    pquery = {}
    stm = Stemmer.Stemmer('english')
    stopwords = Counter(getStopWords())
    if(query.find(':') > 0):
        query = query.replace(':', ' : ')
        bquery = query.split()
        bindex = [i for i in range(len(bquery)) if bquery[i] == ':']
        defaultfields = {"t": "title", "i": "infobox", "b": "body", "c": "category", "l": "links", "r": "references"}
        pquery = {"title": [], "infobox": [], "body": [], "category": [], "links": [], "references": []}
        for i in range(len(bindex)):
            if(bindex[i] == 0):
                pquery["error"] = "No field found"
                break
            elif(bindex[i] == len(bquery) - 1):
                pquery["error"] = "No field query found"
                break
            else:
                if(bquery[bindex[i] - 1] in defaultfields):
                    if(i == len(bindex) - 1):
                        body = ' '.join(bquery[bindex[i] + 1:])
                    else:
                        body = ' '.join(bquery[bindex[i] + 1: bindex[i + 1] - 1])
                    pquery[defaultfields[bquery[bindex[i] - 1]]] = preprocessStr(body, stm, stopwords)
                else:
                    pquery["error"] = "Invalid field"
                    break
    else:
        bquery = query.split(',')
        keys = []
        for bq in bquery:
            body = preprocessStr(bq, stm, stopwords)
            for bd in body:
                keys.append(bd)
        pquery["strings"] = keys
    return pquery

def queryConvert(pquery):
    fquery = {}
    if("title" in pquery):
        for word in pquery["title"]:
            if word not in fquery:
                fquery[word] = [0, 0, 0, 0, 0, 0]
            fquery[word][0] = 1
        for word in pquery["infobox"]:
            if word not in fquery:
                fquery[word] = [0, 0, 0, 0, 0, 0]
            fquery[word][1] = 1
        for word in pquery["body"]:
            if word not in fquery:
                fquery[word] = [0, 0, 0, 0, 0, 0]
            fquery[word][2] = 1
        for word in pquery["category"]:
            if word not in fquery:
                fquery[word] = [0, 0, 0, 0, 0, 0]
            fquery[word][3] = 1
        for word in pquery["links"]:
            if word not in fquery:
                fquery[word] = [0, 0, 0, 0, 0, 0]
            fquery[word][4] = 1
        for word in pquery["references"]:
            if word not in fquery:
                fquery[word] = [0, 0, 0, 0, 0, 0]
            fquery[word][5] = 1
    elif("strings" in pquery):
        for word in pquery["strings"]:
            fquery[word] = [1, 1, 1, 1, 1, 1]
    return fquery

def getTokOff(indexpath, word):
    with open(indexpath + 'indoff_secinv.json', 'r') as f:
        dic = json.load(f)
        off = dic[word[0]]
    st = off[0]
    en = off[1]
    tfd = open(indexpath + 'indoff', 'r')
    while(en - st > 1000):
        mid = int((st + en) / 2)
        tfd.seek(mid, 0)
        cur = tfd.readline()
        mid += len(cur)
        if(mid >= en):
            break
        cur = tfd.readline()
        mid += len(cur)
        cur = cur.split()
        if(cur[0] < word):
            st = mid
        else:
            en = mid
    tfd.seek(st, 0)
    tlst = tfd.read(en - st).split('\n')
    tfd.close()
    tdic = {}
    for tl in tlst:
        if(tl == ""):
            continue
        tl = tl.split()
        tdic[tl[0]] = [tl[1], tl[2], tl[3]]
    data = []
    if(word in tdic):
        data = [int(tdic[word][0]), int(tdic[word][1]), int(tdic[word][2])]
    return data

def getTitle(indexpath, id):
    with open(indexpath + 'titles_off_secinv.json', 'r') as f:
        dic = json.load(f)
        for k in dic:
            if(id <= int(k)):
                break
        off = dic[k]
    word = str(id)
    st = off[0]
    en = off[1]
    tfd = open(indexpath + 'titles_off', 'r')
    while(en - st > 1000):
        mid = int((st + en) / 2)
        tfd.seek(mid, 0)
        cur = tfd.readline()
        mid += len(cur)
        if(mid >= en):
            break
        cur = tfd.readline()
        mid += len(cur)
        cur = cur.split()
        if(int(cur[0]) < id):
            st = mid
        else:
            en = mid
    tfd.seek(st, 0)
    tlst = tfd.read(en - st).split('\n')
    tfd.close()
    tdic = {}
    for tl in tlst:
        if(tl == ""):
            continue
        tl = tl.split()
        tdic[tl[0]] = [tl[1], tl[2]]
    if(word in tdic):
        data = [int(tdic[word][0]), int(tdic[word][1])]
        ifd = open(indexpath + 'titles', 'r')
        ifd.seek(data[0])
        title = ifd.read(data[1])
        ifd.close()
        return title.strip()
    else:
        return ''

def querySearch(indexpath, query):
    pquery = queryParse(query)
    if(not os.path.isdir(indexpath)):
        print("Index does not exist")
    elif("error" in pquery):
        print('Error:', pquery["error"])
    else:
        querylist = queryConvert(pquery)
        weights = [50, 30, 5, 3, 1, 1]
        ctrmap = {"t": 1, "i": 2, "b": 3, "c": 4, "l": 5, "r": 6}
        with open(indexpath + 'doc_count', 'r') as f:
            docount = int(f.read())
        docval = np.zeros(docount)
        toplist = []
        toplen = 10
        for word in querylist:
            tokoff = getTokOff(indexpath, word)
            if(len(tokoff) == 0):
                continue
            idf = math.log10(docount / tokoff[0])
            ifd = open(indexpath + 'invind', 'r')
            ifd.seek(tokoff[1])
            current = tokoff[1]
            inter = 1000000
            while(current < tokoff[1] + tokoff[2]):
                if(tokoff[1] + tokoff[2] - current < inter):
                    data = ifd.read(tokoff[1] + tokoff[2] - current)
                    current += tokoff[1] + tokoff[2] - current
                else:
                    data = ifd.read(inter)
                    current += inter
                    ext = ifd.readline()
                    data += ext
                    current += len(ext)
                data = data[:-1].split('\n')
                postlst = []
                for d in data:
                    tmp = ['0'] * 7
                    ctr = 0
                    for ch in d:
                        if ch in ctrmap:
                            ctr = ctrmap[ch]
                        else:
                            tmp[ctr] += ch
                    postlst.append([int(t) for t in tmp])
                for pl in postlst:
                    tf = 0
                    for i in range(6):
                        tf += (pl[1 + i] * querylist[word][i] * weights[i])
                    tf = math.log10(1 + tf)
                    docval[pl[0]] += tf * idf
                    updateTop(pl[0], docval[pl[0]], toplist, toplen)
            ifd.close()
        data = ""
        if(len(toplist) > 0):
            for i in range(len(toplist)):
                title = getTitle(indexpath, toplist[i][0])
                data += str(toplist[i][0]) + ", " + title + "\n"
        else:
            data = "No Document Found\n"
        return data

def updateTop(id, val, toplist, toplen):
    if(val > 0 and (len(toplist) < toplen or val > toplist[toplen - 1][1])):
        insid = len(toplist)
        for i in range(len(toplist)):
            if(val > toplist[i][1]):
                insid = i
                break
        toplist.insert(insid, [id, val])
        if(len(toplist) > toplen):
            toplist.pop()

if __name__ == '__main__':
    indexpath = sys.argv[1] + '/index/'
    querypath = sys.argv[2]
    queryout = ""
    with open(querypath, 'r') as f:
        while True:
            query = f.readline()
            if(query == ""):
                break
            query = query.strip()
            st = time.time()
            queryout += querySearch(indexpath, query)
            queryout += str(round(time.time() - st, 3)) + '\n\n'
    with open('queries_op.txt', 'w') as f:
        f.write(queryout)
