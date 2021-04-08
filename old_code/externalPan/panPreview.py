f = CurrentFont()
g = f["E"]

from vanilla import *
from mojo.glyphPreview import GlyphPreview
from drawBot import *

from marginPen import MarginPen
import slicerData
from slicerData import *

import importlib
importlib.reload(slicerData)




def getSlicedGlyph(sender):
    if "Slider" in (str(sender)):
        steps=w.steps.get()
        w.sread.set(steps)
        
        thickness=w.weight.get()
        w.wread.set(thickness)
        
        angle=w.angle.get()
        w.aread.set(angle)
        
        offset=w.offset.get()
        w.oread.set(offset)
        
    # if "EditText" in (str(sender)):
    #     print(str(sender))
    #     steps=int(w.sread.get())
    #     thickness=int(w.wread.get())
    #     angle=int(w.aread.get())
    #     offset=int(w.oread.get())
    g = CurrentGlyph().copy()
    g.decompose()
    panData = getSlicedGlyphPath(g, steps=steps, thickness=thickness, angle=angle, offset=offset)
    #pan = getSlicedGlyphPath(g, steps=steps, thickness=thickness, angle=angle, offset=offset)
    ng = RGlyph()
    ng.width = f[CurrentGlyph().name].width
    path = BezierPath()
    for i in panData:
        print(i)
        save()
        rotate(-angle)
        x,y,h = i
        path.rect(x-thickness/2,y,thickness,h-y)
        restore()
        
    writePathInGlyph(pan, ng)
    w.g.setGlyph(ng)




w = Window((300,600), minSize=(300,600))
y=10
w.stxt = TextBox((10,y,50,20),"steps")
w.steps = Slider((60,y,-55,20), minValue=10, maxValue=100, callback=getSlicedGlyph)
w.sread = EditText((-50,y,-10,20), )
y+=30
w.atxt = TextBox((10,y,50,20),"angle")
w.angle = Slider((60,y,-55,20), minValue=0, maxValue=180, value=90, callback=getSlicedGlyph)
w.aread = EditText((-50,y,-10,20))

y+=30
w.wtxt = TextBox((10,y,50,20),"weight")
w.weight = Slider((60,y,-55,20), minValue=0, maxValue=100, value=20, callback=getSlicedGlyph)
w.wread = EditText((-50,y,-10,20))

y+=30
w.otxt = TextBox((10,y,50,20),"offset")
w.offset = Slider((60,y,-55,20), minValue=0, maxValue=100, callback=getSlicedGlyph)
w.oread = EditText((-50,y,-10,20))

y+=40
w.g = GlyphPreview((0,y,-0,-0))







w.open()