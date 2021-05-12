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
  parser = argparse.ArgumentParser(description='''Font filter PAN''')

  # not pan specific                                     )
  parser.add_argument('-c', '--characters', default=string.ascii_letters, type=str,
                        help="Characters...")
  parser.add_argument('-f', '--fontfile', type=str,
                        required=True, help='otf or ttf font')
  
  # pan
  parser.add_argument('-steps', default=30, type=int,
                        help="Interval of the slicer, in fontUnits")
  parser.add_argument('-angle', default=15, type=int,
                        help="Angle in degrees.")
  parser.add_argument('-t', '--thickness', default=30, type=int,
                        help="Thickness in font units.")  
  parser.add_argument('-noCounters',default=False, type=bool,
                        const=True, nargs="?", help="Ignore inner contours.")
  parser.add_argument('-noSmall', default=30, type=int, help='No segments under this value.')
  parser.add_argument('-o', '--offset', default=0, type=int, help='Offset slicer [0, steps].')
  
  # shape arguments  
  parser.add_argument('-shape', default="plainRect", type=str,
                        help="plainRect, plainRound, hex, tri, diamondPoint, (custom?)") 
  # extra shape
  parser.add_argument('-base', default=10, type=int, help='Some shapes use base [hex].')
  parser.add_argument('-top', default=10, type=int, help='Some shapes use top [hex].')
  parser.add_argument('-point', default=10, type=int, help='Some shapes use point [diamonPoint].')
  
  args = parser.parse_args()
  font_file = args.fontfile
  
  s = args.steps
  a = args.angle
  t = args.thickness
  o = args.offset
  ns = args.noSmall

  inner = not args.noCounters
  shape = args.shape

  

  chars = args.characters

  ufo = font2ufo(font_file)
  panfont = NewFont(showInterface=False)

  for gn in chars:
    panfont.newGlyph(gn)
    panfont[gn].width = ufo[gn].width
    
    _p = getPath(ufo[gn])

    q = slicer.getSlicedPathPath(_p, steps=s, thickness=t, angle=a, offset=o, inner=inner, nosmall=ns, shape=shape, base=args.base, top=args.top, point=args.point)
    slicer.writePathInGlyph(q,panfont[gn])
    
  panfont.save("%s/Desktop/pan.ufo" % Path.home())

if __name__ == "__main__":
  run()