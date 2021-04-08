import sys
sys.path.append('./externalPan/')
import slicer
import slicerData
import importlib
import string
importlib.reload(slicer)
importlib.reload(slicerData)

f = CurrentFont()
tick = 30
t = 4
b=8
s=10
a=20




wieber = NewFont(showInterface=False)
# print(dir(wieber))
for gn in f.selection:
    print(gn)
    wieber.newGlyph(gn)
    wieber[gn].width = f[gn].width
    
    b=0
    t=0
    s=30
    
    
    p = slicer.getSlicedGlyphPath(f[gn], steps=s, thickness=tick, angle=a, offset=0, inner=1, nosmall=3, shape="hex", base=b, top=t, point=-10)
    slicer.writePathInGlyph(p,wieber[gn])
    
    p = slicer.getSlicedGlyphPath(f[gn], steps=s, thickness=tick, angle=a, offset=s/2-0, inner=1, nosmall=70, shape="hex", base=t, top=b, point=10)
    slicer.writePathInGlyph(p,wieber[gn])
    
    # b=20
    # t=40
    # s=60
    # p = slicer.getSlicedGlyphPath(f[gn], steps=s, thickness=tick, angle=a+90, offset=0, inner=1, nosmall=30, shape="hex", base=b, top=t, point=-10)
    # slicer.writePathInGlyph(p,wieber[gn])
    
    # p = slicer.getSlicedGlyphPath(f[gn], steps=s, thickness=tick, angle=a+90, offset=s/2-0, inner=1, nosmall=70, shape="hex", base=t, top=b, point=10)
    # slicer.writePathInGlyph(p,wieber[gn])    
    

wieber.openInterface()