import importlib
import slicer
importlib.reload(slicer)

from slicer import *



from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.UI import *
from mojo.events import addObserver, removeObserver
from lib.tools.defaults import getDefault, setDefault
from mojo.drawingTools import *
from vanilla import *
from vanilla.dialogs import getFile
from lib.tools.notifications import PostNotification
from AppKit import *

f = CurrentFont()
g = CurrentGlyph()

from mojo.events import postEvent


event = "draw" 

def writePathInGlyph(path, glyph):
	pen = glyph.getPen()
	path.drawToPen(pen)

def drawGlyph(glyph):
	from fontTools.pens.cocoaPen import CocoaPen
	pen = CocoaPen(glyph.getParent())
	glyph.draw(pen)
	drawPath(pen.path)

def loopList(mylist, n):
	item = n % len(mylist)
	return mylist[item]

f = CurrentFont()
g = CurrentGlyph()



class myObserver(BaseWindowController):
		
	def __init__(self):

		self.steps = 50
		self.thickness = 10
		self.angle = 30
		self.offset = 0
		self.nosmall = 10
		self.inner = False


		self.w = FloatingWindow((300, 200), "PAN", closable = True)
		y=7
		self.w.t_steps = TextBox((7,y,-7,10),"Steps", sizeStyle="mini")
		y+=15
		self.w.s_steps = Slider((7,y,-7,22), minValue=1,maxValue=100,callback=self.update)
		y+=25
		self.w.t_thickness = TextBox((7,y,-7,10),"Thickness", sizeStyle="mini")
		y+=15
		self.w.s_thickness = Slider((7,y,-7,22), minValue=1,maxValue=100,callback=self.update)
		y+=25
		self.w.t_angle = TextBox((7,y,-7,10),"Angle", sizeStyle="mini")
		y+=15
		self.w.s_angle = Slider((7,y,-7,22), minValue=0,maxValue=360,callback=self.update,tickMarkCount=37,stopOnTickMarks=True)
		# self.w.sluit = SquareButton((7,7,-7,16), "Close", callback=self._close, sizeStyle="mini")
		# self.w.slider = Slider((7,30,-7,-7), minValue=-100,maxValue=100, value=0, callback=self.test)
		#self.w.inPreview = CheckBox((7,
		
		addObserver(self, "mainFunction", event)
		self.setUpBaseWindowBehavior()
		self.w.open()
		
	def getUfo(self, sinder):
		ufoPath = getFile()[0]
		self.ufo = OpenFont(ufoPath, showUI=False)
		PostNotification('doodle.updateGlyphView')
	
	def changes(self,sender):
		PostNotification('doodle.updateGlyphView')
			
	def windowCloseCallback(self, sender):
		self.w.hide()
		removeObserver(self, event)
		PostNotification('doodle.updateGlyphView')
		#print "done via windowCloseCallback"

	
	def _close(self,sender):
		self.w.hide()
		removeObserver(self, event)
		PostNotification('doodle.updateGlyphView')

	def mainFunction(self, info):
		save()
		g=CurrentGlyph()
		translate(g.width)
		fill(0)
		p=getSlicedGlyphPath(g,
			self.steps,
			self.thickness,
			self.angle,
			0,40,1,shape="diamondPoint",point=10)
		t=RGlyph()
		writePathInGlyph(p,t)
		drawGlyph(t)
		restore()

	def update(self, sender):
		self.steps = self.w.s_steps.get()
		self.thickness = self.w.s_thickness.get()
		self.angle = self.w.s_angle.get()
		self.mainFunction(self)


					
			





myObserver()

