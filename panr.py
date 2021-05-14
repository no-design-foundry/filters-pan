from drawBot import *
from drawBot import BezierPath as DBBP
from drawBot import drawPath, save, restore, rotate, BezierPath
from fontParts.world import RGlyph, NewFont
from fontPens.marginPen import MarginPen


import sys
from pathlib import Path
# import importlib
import string
from fontTools.ttLib import TTFont
import defcon

#sys.path.append("/Users/thom/Documents/Code/extractor/Lib/")
import extractor
# import os
# print(os.getcwd())
# sys.path.append('../Pan')
#from panLib import slicer


import argparse
import string


def getPath(glyph):
    from fontTools.pens.cocoaPen import CocoaPen
    pen = CocoaPen(glyph.getParent())
    glyph.draw(pen)
    return BezierPath(pen.path)
    
def drawPathInGlyph(path, glyph):
    pen = glyph.getPen()
    path.drawToPen(pen)

def font2ufo(fontpath):
  ufo = defcon.Font()
  extractor.extractUFO(fontpath, ufo)
  return ufo

# data
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
    #print(g.bounds())
    if not g.bounds():return []
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

def drawGlyph(glyph):
    from fontTools.pens.cocoaPen import CocoaPen
    pen = CocoaPen(glyph.getParent())
    glyph.draw(pen)
    drawPath(pen.path)

def writePathInGlyph(path, glyph):
    pen = glyph.getPen()
    path.drawToPen(pen)


#####
#
# S H A P E S
#
#####

def plainRound(path, x,y,h, thickness, **kwargs):
    s=thickness/2
    r=thickness/4
    path.moveTo((x, y))
    path.curveTo((x-r,y),(x - thickness / 2,y+s-r),(x - thickness / 2, y + s))
    path.lineTo((x - thickness / 2, h - s))
    path.curveTo((x - thickness / 2, h - s+r),(x-r, h), (x,h))
    path.curveTo((x+r,h),(x + thickness / 2, h - s+r),(x + thickness / 2, h - s))
    path.lineTo((x + thickness / 2, y + s))
    path.curveTo((x + thickness / 2, y + s-r),(x+r,y),(x,y))
    path.closePath()
    return path

def diamondPoint(path, x,y,h, thickness, **kwargs):
    s = kwargs['point']
    path.moveTo((x, y))
    path.lineTo((x - thickness / 2, y + s))
    path.lineTo((x - thickness / 2, h - s))
    path.lineTo((x, h))
    path.lineTo((x + thickness / 2, h - s))
    path.lineTo((x + thickness / 2, y + s))
    path.closePath()
    return path

def tri(path, x,y,h, thickness, **kwargs):
    #path.moveTo((x, y))
    path.moveTo((x - thickness / 2, y ))
    path.lineTo((x, h ))
    path.lineTo((x + thickness / 2, y ))
    path.closePath()
    return path

def hex(path, x,y,h, thickness, **kwargs):
    base = kwargs['base']
    top = kwargs['top']
    #path.moveTo((x, y))
    path.moveTo((x - base / 2, y ))
    
    path.lineTo((x - thickness/2, y+(h-y)/2 ))
    
    path.lineTo((x - top / 2, h ))
    #path.lineTo((x, h))
    path.lineTo((x + top / 2, h ))
    
    path.lineTo((x + thickness/2, y+(h-y)/2 ))

    path.lineTo((x + base / 2, y ))
    path.closePath()

    return path

def plainRect(path, x,y,y2, thickness, **kwargs):
    path.moveTo((x+thickness/2,y))
    path.lineTo((x-thickness/2,y))
    path.lineTo((x-thickness/2,y2))
    path.lineTo((x+thickness/2,y2))
    path.closePath()
    return path



def getSlicedGlyphPath(glyph, 
                        steps=10, 
                        thickness=10, 
                        angle=30, 
                        offset=0, 
                        nosmall=10, 
                        inner=0,
                        DEBUG=False, 
                        **kwargs
                        ):
    """?"""
    save()
    glyphPath = DBBP()
    result = getSlicedGlyphData(glyph, steps=steps, thickness=thickness, angle=angle, offset=offset, nosmall=nosmall, inner=inner, **kwargs)
    if DEBUG:return result
    if result:
        for r in result:
            save()
            rotate(-angle)
            x,y,h = r
            try:
                eval(kwargs['shape'])(glyphPath, x,y,h, thickness, **kwargs)
            except:
                glyphPath.rect(x-thickness/2,y,thickness,h-y)
            restore()
    restore()
    glyphPath.rotate(-angle)
    return glyphPath



def getSlicedPathPath(path, 
                        steps=10, 
                        thickness=10, 
                        angle=0, 
                        offset=0, 
                        nosmall=10, 
                        inner=0,
                        DEBUG=False, 
                        **kwargs
                        ):
    """?"""
    #save()
    pathPath = DBBP()
    path = path.copy()
    result = getSlicedPathData(path, steps=steps, thickness=thickness, angle=angle, offset=offset, nosmall=nosmall, inner=inner, **kwargs)
    if DEBUG:return result
    if result:
        for r in result:
            save()
            #pathPath.rotate(-angle)
            x,y,h = r
            try:
                eval(kwargs['shape'])(pathPath, x,y,h, thickness, **kwargs)
            except:
                pathPath.rect(x-thickness/2,y,thickness,h-y)
            restore()
    pathPath.rotate(-angle)
    #restore()
    return pathPath


def panr(ufo=None, **settings):
  for glyph in ufo:
    _p = getPath(glyph)
    q = getSlicedPathPath(_p, 
                                steps=int(settings['steps']), 
                                thickness=int(settings['thickness']), 
                                angle=int(settings['angle']), 
                                offset=int(settings['offset']), 
                                inner=settings['counters']=='yes!', 
                                nosmall=30, 
                                shape=settings['shape'], 
                                
                                top=10, 
                                point=-10, 
                                base=int(settings['thickness']),
      )
    glyph.clear()
    writePathInGlyph(q,ufo[glyph.name])
    # processGlyph(glyph, steps, angle, thickness, inner, noSmall, offset, shape, )
  return ufo