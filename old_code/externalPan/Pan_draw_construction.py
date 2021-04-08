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

gn = 'a'

# showing
_glyph = True
sliceLines = True
panLines = False
points = False

# contraction parameters
_steps = 50
_angle = 32.0
_nosmall = 0
_inner = True
_offset = 0

# draw parameters
_draw = False
_thickness = 30
_shape = "plainRect"


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

if _glyph:
    save()
    fill(None)
    stroke(0)
    drawGlyph(g)
    restore()

save()
d= 10
rotate(-_angle)
xdone = []
path = BezierPath()
for i in a:
	x,y1,y2 = i
	if points:
	    oval(x-d/2,y1-d/2,d,d)
	    oval(x-d/2,y2-d/2,d,d)
	if sliceLines and x not in xdone:
	    xdone.append(x)
	    save()
	    stroke(0)
	    strokeWidth(.1)
	    line((x,-1000),(x,10000))
	    restore()
	if panLines:
	    save()
	    stroke(0)
	    strokeWidth(10)
	    line((x,y1),(x,y2))
	    restore()
	if _draw:
	    p = getSlicedGlyphPath(f[gn], steps=_steps, thickness=_thickness, angle=_angle, offset=_offset, inner=_inner, nosmall=_nosmall, shape="tri",)
	    path.appendPath(p)
if _draw:
    rotate(_angle)
    drawPath(path)
	    
        


