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


# contraction parameters
_steps = 50
_angle = 30
_nosmall = 10
_inner = True
_offset = 32

# draw parameters
_thickness = 30
_shape = "plainRect"


gn = 'a'
g = f[gn]
a = sd(g,
steps=_steps, 
thickness=_thickness, 
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
xdone = []

for i in a:
	x,y1,y2 = i
	oval(x-d/2,y1-d/2,d,d)
	oval(x-d/2,y2-d/2,d,d)
	if x not in xdone:
	    xdone.append(x)
	    save()
	    stroke(0)
	    strokeWidth(.1)
	    line((x,-1000),(x,10000))
	    restore()



