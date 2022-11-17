import pyautogui as pag
import time
import numpy as np
import mouse

#Types
#-1 empty  -2 flag   -3 unknown safe    -4 unknown danger

def click(pos,butt):
    mouse.move(pos[0],pos[1])
    mouse.click(butt)

class Board:
    def __init__(self, x=24, y=20):
        self.size = (x, y)
        self.grid = [[-1 for _ in range(x)] for _ in range(y)]
        self.bLoc = self.getBoardLoc()
    
    def print(self):
        for row in self.grid:
            line = ""
            for v in row:
                if v==-1:
                    sym=" "
                elif v==-2:
                    sym="P"
                else: sym=str(v)
                line+="["+sym+"]"
            print(line)
    
    def clickAt(self, x, y, clickType):
        clickPoint = (self.bLoc[0]+x*25+12, self.bLoc[1]+y*25+12)
        click(clickPoint, clickType)

    def isSolved(self):
        for row in self.grid:
            line = ""
            for v in row:
                if v==-1:
                    return False
        return True

    def setValue(self, x, y, value):
        self.grid[y][x]=value
    
    def getValue(self, x, y):
        if x>self.size[0]-1 or y>self.size[1]-1 or x<0 or y<0:
            return 0
        return self.grid[y][x]

    def setValueIf(self, x, y, value):
        val = self.getValue(x,y)
        if (val==-1 or val==-3 or val==-4):
            self.setValue(x,y, value)

    def getBoardLoc(self):
        screenshot = pag.screenshot()
        diffPos = pag.locateOnScreen("diffLoc.png", confidence=0.8)
        if diffPos!=None:
            pos = (int(diffPos.left), int(diffPos.top))
            offset = (0,0)
            loc = pos
            while screenshot.getpixel(loc)==(74, 117, 44):
                offset=(offset[0]-1,offset[1])
                loc = (pos[0]+offset[0], pos[1]+offset[1])
            offset=(offset[0]+1,offset[1])
            loc = (pos[0]+offset[0], pos[1]+offset[1])
            while screenshot.getpixel(loc)==(74, 117, 44):
                offset=(offset[0],offset[1]+1)
                loc = (pos[0]+offset[0], pos[1]+offset[1])
            offset=(offset[0],offset[1]-1)
            loc = (pos[0]+offset[0], pos[1]+offset[1])
            return (loc)
        else:
            print("Could not find board!")

    def updateBoard(self):
        screenshot = pag.screenshot()
        safe = True
        blockSize = 600/self.size[0]
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                pos1 = (self.bLoc[0]+x*blockSize+13, self.bLoc[1]+y*blockSize+12)
                color1 = screenshot.getpixel(pos1)
                if color1==(170,215,81) or color1==(162,209,73):
                    self.setValueIf(x,y,-1)
                elif color1==(224,95,26) or color1==(222, 93, 24):
                    self.setValueIf(x,y,-2)
                elif color1==(25,118,210):
                    self.setValueIf(x,y,1)
                elif color1==(56,142,60):
                    self.setValueIf(x,y,2)
                elif color1==(211,47,47):
                    self.setValueIf(x,y,3)
                elif color1==(123,31,162):
                    self.setValueIf(x,y,4)
                elif color1==(255,143,0):
                    self.setValueIf(x,y,5)
                elif color1==(0,151,167):
                    self.setValueIf(x,y,6)
                elif color1==(229,194,159) or color1==(215,184,153):
                    self.setValueIf(x,y,0)
                else:
                    self.setValueIf(x,y,-4)
                    safe=False
        return safe

    def findMoves(self):
        loc = self.bLoc
        totalMoves = 0
        mov=1
        while mov>0:
            unknown=False
            mov=0
            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    num = self.getValue(x,y)
                    if num==-1 or num==0:
                        continue
                    emptySpots = []
                    flagCount=0
                    danger=False
                    for xOff in (-1,0,1):
                        for yOff in (-1,0,1):
                            if (xOff==0 and yOff==0):
                                continue
                            if self.getValue(x+xOff, y+yOff)==-1:
                                emptySpots.append((x+xOff, y+yOff))
                            elif self.getValue(x+xOff, y+yOff)==-2:
                                flagCount+=1
                            elif self.getValue(x+xOff, y+yOff)==-4:
                                danger=True
                                unknown=True
                    if num-flagCount==len(emptySpots) and not danger:
                        for e in emptySpots:
                            mov+=1
                            self.setValue(e[0], e[1], -2)
                            self.clickAt(e[0],e[1],mouse.RIGHT)
                    if flagCount==num and not danger:
                        for e in emptySpots:
                            mov+=1
                            self.setValue(e[0], e[1], -3)
                            self.clickAt(e[0],e[1],mouse.LEFT)
            totalMoves+=mov
        return (totalMoves==0 and not unknown)


    def generateAndTest(self,checkList,testList,i):
        if (len(testList)==i):
            return [testList.copy()]

        if self.test(checkList, testList)==False:
            return False
        testList[i]=1
        test1 = self.generateAndTest(checkList,testList,i+1)
        testList[i]=0
        test2 = self.generateAndTest(checkList,testList,i+1)
        testList[i]=-1
        if test1==False and test2==False:
            return False
        toReturn = []
        if test1!=False:
            toReturn += test1
        if test2!=False:
            toReturn += test2
        return toReturn

    def OptGenTest(self, checkList, testList):
        i=0
        c=0
        agroList = None
        while i>=0:
            if testList[i]<1:
                testList[i]+=1

                test = self.test(checkList,testList)
                if not test:
                    i-=1

                if (len(testList)-1==i):
                    c+=1
                    if agroList == None:
                        agroList = testList.copy()
                    else:
                        for i in range(len(testList)):
                            if testList[i]!=agroList[i]:
                                agroList[i]=-1
                    i-=1

                i+=1
            else: 
                testList[i]=-1
                i-=1
        
        return agroList


    def test(self, checkList, testList):       
        for test in checkList:
            val = test[0]
            emptyChildren = test[1]
            emptyCount=0
            mineCount=0
            unknownCount=0
            for e in emptyChildren:
                if testList[e]==-1:
                    unknownCount+=1
                elif testList[e]==0:
                    emptyCount+=1
                else:
                    mineCount+=1
            if (mineCount>val):
                return False
            if (unknownCount<val-mineCount):
                return False
        return True

    def findAdvancedMoves(self):
        emptySpotList = []
        checkList = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                num = self.getValue(x,y)
                if num==-1 or num==0 or num==-2 or num==-3:
                    continue
                flagCount=0
                localEmptyList = []
                for xOff in (-1,0,1):
                    for yOff in (-1,0,1):
                        if (xOff==0 and yOff==0):
                            continue
                        if self.getValue(x+xOff, y+yOff)==-1:
                            loc = (x+xOff, y+yOff)
                            if loc in emptySpotList:
                                ind = emptySpotList.index(loc)
                            else:
                                ind = len(emptySpotList)
                                emptySpotList.append(loc)
                            localEmptyList.append(ind)
                        elif self.getValue(x+xOff, y+yOff)==-2:
                            flagCount+=1
                val = num-flagCount
                if (val>=0):
                    checkList.append([val,localEmptyList])


        testList = [-1 for _ in range(len(emptySpotList))]  
        possiblePerms = self.OptGenTest(checkList,testList) 
        testList = possiblePerms
        for i,e in enumerate(emptySpotList):
            if testList[i]!=-1:
                if testList[i]==1:
                    self.setValue(e[0], e[1], -2)
                    self.clickAt(e[0],e[1],mouse.RIGHT)
                elif testList[i]==0:
                    self.setValue(e[0], e[1], -3)
                    self.clickAt(e[0],e[1],mouse.LEFT)

b = Board()

b.clickAt(12,10,mouse.LEFT)
pag.moveTo(10,10)
time.sleep(0.2)
while not b.isSolved():
    while True:
        b.updateBoard()
        if b.findMoves():
            print("Smart mode activated!")
            break
        pag.moveTo(10,10)
    pag.moveTo(10,10)
    b.updateBoard()
    b.findAdvancedMoves()