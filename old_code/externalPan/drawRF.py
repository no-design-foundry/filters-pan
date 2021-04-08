from slicerData import getSlicedGlyphData as sd
from slicer import *

from fontParts.world import OpenFont
path = "/Users/thom/Dropbox/HT-Letters/Doodles/Farhill-Contrast.ufo"
f = OpenFont(path, showInterface=False)

def drawGlyph(glyph):
	from fontTools.pens.cocoaPen import CocoaPen
	pen = CocoaPen(glyph.getParent())
	glyph.draw(pen)
	drawPath(pen.path)


_steps = 40
_angle = 30
_nosmall = 10
_inner = False
_offset = 1


gn = 'a'
g = f[gn]
c = g.copy()
c.removeOverlap()
g=c

a = sd(g,
steps=_steps, 
thickness=10, 
angle=_angle, 
offset=_offset, 
nosmall=_nosmall, 
inner=_inner,)
#print(a)
translate(200,200)

save()
fill(None)
stroke(0)
drawGlyph(g)
restore()

save()
d= 10
rotate(-_angle)
for i in a:
	x,y1,y2 = i
	oval(x-d/2,y1-d/2,d,d)
	oval(x-d/2,y2-d/2,d,d)
	save()
	stroke(0)
	strokeWidth(.1)
	line((x,-1000),(x,10000))
	restore()



