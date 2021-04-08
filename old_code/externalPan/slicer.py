
import importlib

from drawBot import *
from drawBot import BezierPath as DBBP
from fontParts.world import *
from marginPen import MarginPen

import slicerData
importlib.reload(slicerData)

from slicerData import *
__all__ = [
                "writePathInGlyph",
                "getSlicedGlyphPath",
                "drawGlyph"
]
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

