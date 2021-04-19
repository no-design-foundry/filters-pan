# getSlicedGlyphPath return a list (data)  of all the marginCoords
# use this data with a drawing function

#from drawBot import *
"""
eg:
    for i in data:
        save()
        path.rotate(angle)
        x,y,h = i
        #path.rect(x-thickness/2,y,thickness,h-y)
        s=7
        path.moveTo((x,y))
        path.lineTo((x-thickness/2,y+s))
        path.lineTo((x-thickness/2,h-s))
        path.lineTo((x,h))
        path.lineTo((x+thickness/2,h-s))
        path.lineTo((x+thickness/2,y+s))

        path.closePath()
        path.rotate(-angle)
        restore()
"""

from fontPens.marginPen import MarginPen
from fontParts.world import RGlyph
__all__ = [
                "getSlicedGlyphData","getSlicedPathData"
]
def getStartPoints(g):
    sp = []
    for c in g.contours:
        sp.append((c.points[0].x,c.points[0].y))
    return(sp)

class PanMO(MarginPen):
    def __init__(self, glyphSet, value, isHorizontal=True):
        super().__init__(glyphSet, value, isHorizontal=False)
        
    def getAllPan(self):
        allHits = []
        for index, pts in self.hits.items():
            allHits.extend(pts)
        
        if len(allHits) > 1:
            if allHits[-1] == allHits[-2]:
                allHits.remove(allHits[-1])
        if len(allHits) > 1:
            if allHits[0] == allHits[1]:
                allHits.remove(allHits[0])
        
        ## sometimes the startPoint is counted double
        ## remove startPoint
        # if len(allHits)%2 != 0:
        #     sps = getStartPoints(self.glyphSet)
        #     for sp in sps:
        #         if allHits[-1] == sp[1]:
        #             allHits.remove(allHits[-1])
        boo = []
        for i in allHits:
            if allHits.count(i) == 3:
                boo.append(i)
        boo=list(set(boo))
        for b in boo:
            allHits.remove(b)

        # if 3 remove the middle one
        if len(allHits) == 3:
            weg3 = None
            for i in allHits:
                if i == min(allHits): continue
                if i == max(allHits): continue
                weg3 = i
            if weg3:
                allHits.remove(weg3)

        if len(allHits)%2 != 0:
            print(allHits)
            boo = []
            for i in allHits:
                if allHits.count(i) == 2:
                    boo.append(i)
            boo=list(set(boo))
            for b in boo:
                print(b)
                del(allHits[allHits.index(b)])
            print(allHits)
        # if len(allHits)%2 != 0:
        #     allHits = allHits[1:]


        #print(allHits)
        # if len(allHits) > 2:
        #     d = []
        #     for i,v in enumerate(allHits[:-1]):
        #         if v == allHits[i+1]:
        #             d.append(i)

        #     remove = (list(set(d)))
        #     remove.sort()
        #     print(allHits, remove, len(allHits))
            
            # if 1 in remove:
            #     remove.remove(1)
        
        unique = list((allHits))
        unique.sort()
        return unique


def getSlicedGlyphData(
                            glyph, 
                            steps=10, 
                            thickness=10, 
                            angle=30, 
                            offset=0, 
                            nosmall=10, 
                            inner=0,
                            DEBUG=False, 
                            **kwargs,
                            ):
    results = []

    g = RGlyph()
    g.appendGlyph(glyph)
    g.width=glyph.width
    g.decompose()
    g.removeOverlap()
    g.removeOverlap()

    steps = int(steps)
    g.rotate((angle)%360)

    pt = range( int(g.bounds[0]-offset), int(g.bounds[2]), steps)
    for i in range(len(pt)):

        pen = PanMO(g, pt[i], isHorizontal=False)
        g.draw(pen)
        if not inner:
            result = pen.getMargins()

        else:
            result = pen.getAllPan()
            if DEBUG:return result
            # if len(result) == 3:
            #     result = pen.getMargins()
            if len(result) > 3:
                spaces = int(((len(result)-2)/2))
                ts =[]
                for x in range(spaces):
                    end = result[1+(x*2)]
                    start = result[2+(x*2)]
                    #print(end,start)
                    if start-end < nosmall:
                        ts.append(start)
                        ts.append(end)
                for x in ts:
                    result.remove(x)

        if result and len(result)%2 ==0:
            for a,b in zip(result[0::2], result[1::2]):
                #print str(i), '+', str(k), '=', str(i+k)
                #if result[0]-2 > result[1] or result[0]+2 < result[1]:
                if b-a > nosmall:
                    # very small contours can cause probs, so do not do them.
                    results.append((pt[i], a,b))

    return results


def getSlicedPathData(
                            path, 
                            steps=10, 
                            thickness=10, 
                            angle=0, 
                            offset=0, 
                            nosmall=10, 
                            inner=0,
                            DEBUG=False, 
                            **kwargs,
                            ):
    results = []

    g = path

    steps = int(steps)
    g.rotate((angle)%360)

    pt = range( int(g.bounds()[0]-offset), int(g.bounds()[2]), steps)
    for i in range(len(pt)):

        pen = PanMO(g, pt[i], isHorizontal=False)
        g.drawToPen(pen)
        if not inner:
            result = pen.getMargins()

        else:
            result = pen.getAllPan()
            if DEBUG:return result
            # if len(result) == 3:
            #     result = pen.getMargins()
            if len(result) > 3:
                spaces = int(((len(result)-2)/2))
                ts =[]
                for x in range(spaces):
                    end = result[1+(x*2)]
                    start = result[2+(x*2)]
                    #print(end,start)
                    if start-end < nosmall:
                        ts.append(start)
                        ts.append(end)
                for x in ts:
                    result.remove(x)

        if result and len(result)%2 ==0:
            for a,b in zip(result[0::2], result[1::2]):
                #print str(i), '+', str(k), '=', str(i+k)
                #if result[0]-2 > result[1] or result[0]+2 < result[1]:
                if b-a > nosmall:
                    # very small contours can cause probs, so do not do them.
                    results.append((pt[i], a,b))

    return results
