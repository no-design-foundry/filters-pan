__all__ = [
                "plainRect",
                "plainRound",
                "diamondPoint",
                "tri",
]

def plainRect(path, x,y,h, thickness, **kwargs):
    s = 0
    path.moveTo((x, y))
    path.lineTo((x - thickness / 2, y + s))
    path.lineTo((x - thickness / 2, h - s))
    path.lineTo((x, h))
    path.lineTo((x + thickness / 2, h - s))
    path.lineTo((x + thickness / 2, y + s))
    path.closePath()
    return path

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
    s = 0
    path.moveTo((x, y))
    path.lineTo((x - thickness / 2, y + s))
    path.lineTo((x, h - s))
    path.lineTo((x + thickness / 2, y + s))
    path.closePath()
    return path