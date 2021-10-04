import os
import time

def getInvCount(indexpath):
    with open(indexpath + 'invcount', 'r') as f:
        val = f.read()
    return int(val)

def closeFD(fds):
    for fd in fds:
        fd.close()

def writeLines(fd, invfd, count):
    tlen = 0
    for _ in range(count):
        tmp = invfd.readline()
        tlen += len(tmp)
        fd.write(tmp)
    return tlen

def merger(indexpath):
    fcount = getInvCount(indexpath)
    invfd = []
    for i in range(fcount):
        invfd.append(open(indexpath + 'invind_{}'.format(i), 'r'))
    tokfd = []
    for i in range(fcount):
        tokfd.append(open(indexpath + 'tokoff_{}'.format(i), 'r'))

    finv = open(indexpath + 'invind', 'w')
    ftok = open(indexpath + 'indoff', 'w')

    cdata = [fd.readline()[:-1].split() for fd in tokfd]
    coff = 0
    while True:
        minstr = ""
        minind = []
        allnull = True
        for i in range(len(cdata)):
            if(len(cdata[i]) == 0):
                continue
            allnull = False
            if(len(minind) == 0 or cdata[i][0] < minstr):
                minstr = cdata[i][0]
                minind = [i]
            elif(cdata[i][0] == minstr):
                minind.append(i)
        if(allnull):
            break
        docf = 0
        tbytes = 0
        for ind in minind:
            tbytes += writeLines(finv, invfd[ind], int(cdata[ind][1]))
            docf += int(cdata[ind][1])
            cdata[ind] = tokfd[ind].readline()[:-1].split()
        ftok.write(minstr + ' ' + str(docf) + ' ' + str(coff) + ' ' + str(tbytes) + '\n')
        coff += tbytes

    closeFD(invfd)
    closeFD(tokfd)
    closeFD([finv, ftok])

    os.remove(indexpath + 'invcount')
    for i in range(fcount):
        os.remove(indexpath + 'invind_{}'.format(i))
        os.remove(indexpath + 'tokoff_{}'.format(i))

if __name__ == "__main__":
    print("Merge started")
    st = time.time()
    merger('../index/')
    print("Merge time", time.time() - st)