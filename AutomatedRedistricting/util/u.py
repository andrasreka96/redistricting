import math
from itertools import islice

def iteratef(f,x,n):
        if n == 0:
            return []
        else:
            return [f(x)] + iteratef(f,f(x),n-1)


def allVariatons(values,length,ind,newlist):

    if ind == length:
        yield newlist[:]
    else:
        for i in values:
            newlist[ind]=i
            #for result in allVariatons(values,length,ind+1,newlist):
                #yield result
            yield from allVariatons(values,length,ind+1,newlist)

def generateColors(n):
        print(n)
        basecolors_number = math.ceil(math.pow(n+2,1/3))
        print(basecolors_number)
        basecolors =iteratef(lambda x:x//2,255,basecolors_number)
        basecolors.append(0)
        print(basecolors)
        colors = [(color[0],color[1],color[2]) for color in allVariatons(basecolors,3,0,[0,0,0])]
        print(colors[1:len(colors)-2])

generateColors(21)

#for i in allVariatons([1,2,3,4],3,0,[0,0,0]):
#    print(i)
