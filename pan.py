import sys
from pathlib import Path
import importlib
import string
from fontTools.ttLib import TTFont
import defcon

sys.path.append("/Users/thom/Documents/Code/extractor/Lib/")
import extractor

sys.path.append('/Users/thom/Documents/Code/JAN/Pan/old_code/externalPan/')
import slicerData
import slicer

from fontParts.world import *
from drawBot import BezierPath

import argparse
import string

importlib.reload(slicer)
importlib.reload(slicerData)


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

def run():
  parser = argparse.ArgumentParser(description='''Font filter PAN''',
                                     )
  parser.add_argument('-f', '--fontfile', type=str,
                        required=True, help='otf or ttf font')
  parser.add_argument('-c', '--characters', default=string.ascii_letters, type=str,
                        help="Characters...")
  parser.add_argument('-steps', default=30, type=int,
                        help="Steps")
  parser.add_argument('-angle', default=15, type=int,
                        help="Angle in degrees.")
  parser.add_argument('-t', '--thickness', default=30, type=int,
                        help="Thickness in font units.")  
  parser.add_argument('-shape', default="plainRect", type=str,
                        help="plainRect, plainRound, hex, tri, diamondPoint") 
  parser.add_argument('-noCounters',default=False, type=bool,
                        const=True, nargs="?", help="Ignore inner contours.")
  
  
  
  args = parser.parse_args()
  font_file = args.fontfile
  
  s = args.steps
  a = args.angle
  t = args.thickness
  inner = not args.noCounters
  shape = args.shape


  chars = args.characters

  ufo = font2ufo(font_file)
  panfont = NewFont(showInterface=False)

  for gn in chars:
    panfont.newGlyph(gn)
    panfont[gn].width = ufo[gn].width
    
    _p = getPath(ufo[gn])

    q = slicer.getSlicedPathPath(_p, steps=s, thickness=t, angle=a, offset=0, inner=inner, nosmall=t, shape=shape, base=10, top=10, point=-10)
    slicer.writePathInGlyph(q,panfont[gn])
    
  panfont.save("%s/Desktop/pan.ufo" % Path.home())

if __name__ == "__main__":
  run()