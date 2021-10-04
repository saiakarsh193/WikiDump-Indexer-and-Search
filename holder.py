import os
import merger
import secinv
import time

class Holder():
    def __init__(self, indexpath):
        self.index = {}
        self.indexpath = indexpath + '/index/'
        self.sectype = ['t', 'i', 'b', 'c', 'l', 'r']
        self.pagecount = 0
        self.indexcount = 0
        if(not os.path.isdir(self.indexpath)):
            os.mkdir(self.indexpath)
        self.titlefd = open(self.indexpath + 'titles', 'w')
        self.titoffd = open(self.indexpath + 'titles_off', 'w')
        self.titcoff = 0
        self.sttime = time.time()

    def addPageIndex(self, data, pageid, title):
        for section in range(len(data)):
            for word in data[section]:
                le = len(word)
                isd = word.isdigit()
                isa = word.isalpha()
                if((le > 2 and le < 15) and (isd or isa) and not (isd and isa)):
                    if(not word in self.index):
                        self.index[word] = []
                    if(not(len(self.index[word]) > 0 and self.index[word][-1][0] == pageid)):
                        self.index[word].append([pageid, 0, 0, 0, 0, 0, 0])
                    self.index[word][-1][section + 1] += 1
        title = title.strip().encode("ascii", errors="ignore").decode() + '\n'
        self.titlefd.write(title)
        self.titoffd.write(pageid + ' ' + str(self.titcoff) + ' ' + str(len(title)) + '\n')
        self.titcoff += len(title)
        self.pagecount += 1
        if(self.pagecount % 30000 == 0):
            self.writeIndex()
        return
    
    def writeIndex(self):
        fii = open(self.indexpath + 'invind_{}'.format(self.indexcount), 'w')
        ftl = open(self.indexpath + 'tokoff_{}'.format(self.indexcount), 'w')
        st = time.time()
        print("writing:", self.pagecount)
        for word in sorted(self.index):
            tmp = ""
            for doc in range(len(self.index[word])):
                tmp += self.index[word][doc][0]
                for section in range(1, 7):
                    if(self.index[word][doc][section] > 0):
                        tmp += self.sectype[section - 1] + str(self.index[word][doc][section])
                tmp += '\n'
            fii.write(tmp)
            ftl.write(word + ' ' + str(len(self.index[word])) + '\n')
        fii.close()
        ftl.close()
        print("finished dT:", time.time() - st, "T:", time.time() - self.sttime)
        self.index = {}
        self.indexcount += 1
        return

    def endHolder(self):
        self.writeIndex()
        with open(self.indexpath + 'invcount', 'w') as f:
            f.write(str(self.indexcount))
        self.titlefd.close()
        self.titoffd.close()
        merger.merger(self.indexpath)
        secinv.createTitleSecInv(self.indexpath)
        secinv.createTokenSecInv(self.indexpath)

