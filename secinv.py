import json
import time

def createTitleSecInv(indexpath):
    inter = 10000
    ctr = 0
    off = 0
    clen = 0
    dic = {}
    sfd = open(indexpath + 'titles_off', 'r')
    while True:
        line = sfd.readline()
        if(line == ""):
            break
        if(ctr % inter == 0):
            if(ctr > 0):
                dic[ctr - 1] = [off, off + clen]
            off += clen
            clen = 0
        clen += len(line)
        ctr += 1
    dic[ctr - 1] = [off, off + clen]
    sfd.close()
    with open(indexpath + 'titles_off_secinv.json', 'w') as f:
        json.dump(dic, f)
    with open(indexpath + 'doc_count', 'w') as f:
        f.write(str(ctr))

def createTokenSecInv(indexpath):
    tlist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    ctr = 0
    off = 0
    clen = 0
    dic = {}
    sfd = open(indexpath + 'indoff', 'r')
    while True:
        line = sfd.readline()
        if(line == ""):
            break
        if(line[0] != tlist[ctr]):
            if(clen > 0):
                dic[tlist[ctr]] = [off, off + clen]
            while(line[0] != tlist[ctr]):
                ctr += 1
            off += clen
            clen = 0
        clen += len(line)
    dic[tlist[ctr]] = [off, off + clen]
    sfd.close()
    with open(indexpath + 'indoff_secinv.json', 'w') as f:
        json.dump(dic, f)

if __name__ == "__main__":
    indexpath = '../index/'
    print("Secinv started")
    st = time.time()
    createTitleSecInv(indexpath)
    print("Titles sec inv time", time.time() - st)
    st = time.time()
    createTokenSecInv(indexpath)
    print("Tokens sec inv time", time.time() - st)
