from defcon import Font, Glyph, Point, Contour
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.misc.bezierTools import segmentSegmentIntersections
from math import hypot, radians, cos, sin, atan2, pi, ceil
from defcon.objects.base import BaseObject
from decimal import Decimal
from ufo2ft import compileVariableTTF
from .designspace import make_designspace
from pathops.operations import union as skia_union
BaseObject.addObserver = lambda *args,**kwargs:None
BaseObject.postNotification = lambda *args,**kwargs:None
BaseObject.removeObserver = lambda *args,**kwargs:None
BaseObject.beginSelfNotificationObservation = lambda *args,**kwargs:None
BaseObject.endSelfContourNotificationObservation = lambda *args,**kwargs:None


def interpolate(a, b, t=.5):
    return a + t * (b - a)


def interpolate_point(point_a, point_b, t=.5):
    return [interpolate(a, b, t) for a, b in zip(point_a, point_b)]
    

def rotate_point_around_axis(point, axis_coos, angle_degrees):
    angle_radians = Decimal(radians(angle_degrees))
    # Translate point back to origin:
    try:
        translated_x = Decimal(point.x) - axis_coos[0]
        translated_y = Decimal(point.y) - axis_coos[1]
    except AttributeError:
        translated_x = Decimal(point[0]) - axis_coos[0]
        translated_y = Decimal(point[1]) - axis_coos[1]
    
    # Rotate point
    angle_cos = Decimal(cos(angle_radians))
    angle_sin = Decimal(sin(angle_radians))
    rotated_x = translated_x * angle_cos - translated_y * angle_sin
    rotated_y = translated_x * angle_sin + translated_y * angle_cos
    
    # Translate point back to its original location
    final_x = rotated_x + axis_coos[0]
    final_y = rotated_y + axis_coos[1]
    
    try:
        point.x = float(final_x)
        point.y = float(final_y)
    except AttributeError:
        return float(final_x), float(final_y)



def rotate_glyph(glyph, angle):
    for contour in glyph:
        for p, point in enumerate(contour):
            rotate_point_around_axis(point, (Decimal(0), Decimal(0)), angle)

def rotate_segments(segments, angle):
    new_segments = []
    for segment in segments:
        new_segment = []
        for point in segment:
            new_point = rotate_point_around_axis(point, (Decimal(0), Decimal(0)), angle)
            new_segment.append(new_point)
        new_segments.append(new_segment)
    return new_segments
        
def create_segments(x, y):

    segments = []
    start = 0

    for i in range(len(y)):
        if not y[i]:
            segments.append((x[start], x[i]))
            start = i + 1

    # If there are remaining points after the last segment
    if start < len(x):
        segments.append((x[start], x[-1]))

    return segments
    
def line_shape(pen, point_a, point_b, thickness, flip_end=False):
    (x_a, y_a), (x_b, y_b) = point_a, point_b
    angle = atan2(point_b[1] - point_a[1], point_b[0] - point_a[0]) + pi/2
    x_offset, y_offset = cos(angle) * thickness, sin(angle) * thickness
    pen.moveTo((x_a + x_offset, y_a + y_offset))

    next_point = (x_b + x_offset, y_b + y_offset)
    x_offset, y_offset = cos(angle + pi) * thickness, sin(angle + pi) * thickness
    next_next_point = (x_b + x_offset, y_b + y_offset)

    if flip_end in [True, None]:
        pen.lineTo(next_next_point)
        pen.lineTo(next_point)
    else:
        pen.lineTo(next_point)
        pen.lineTo(next_next_point)

    pen.lineTo((x_a + x_offset, y_a + y_offset))
    pen.closePath()

def triangle_shape(pen, point_a, point_b, thickness):
    (x_a, y_a), (x_b, y_b) = point_a, point_b
    angle = atan2(point_b[1] - point_a[1], point_b[0] - point_a[0]) + pi/2
    x_offset, y_offset = cos(angle) * thickness, sin(angle) * thickness
    pen.moveTo((x_a + x_offset, y_a + y_offset))
    
    x_offset, y_offset = cos(angle + pi) * thickness, sin(angle + pi) * thickness
    pen.lineTo((x_a + x_offset, y_a + y_offset))
    
    pen.lineTo((x_b, y_b))
    pen.closePath()

def circle(pen, center, radius, tension=1):
    x, y = center
    pen.moveTo((x, y+radius))
    pen.curveTo((x - radius * tension, y + radius), (x - radius, y + radius * tension), (x - radius, y))
    pen.curveTo((x - radius, y - radius * tension), (x - radius * tension, y - radius), (x, y - radius))
    pen.curveTo((x + radius * tension, y - radius), (x + radius, y - radius * tension), (x + radius, y))
    pen.curveTo((x + radius, y + radius * tension), (x + radius * tension, y + radius), (x, y + radius))
    pen.closePath()

def dumbbell_shape(pen, point_a, point_b, thickness):
    circle(pen, point_a, thickness)
    circle(pen, point_b, thickness)
    line_shape(pen, point_a, point_b, thickness/5)

def get_pan_slices(glyph, step):
    contour_points = []
    for contour in glyph._contours:
        for point in contour._points:
            contour_points.append((point.x, point.y))
    bounds = glyph.bounds
    return_value = []
    if bounds is None:
        return return_value

    for i in range(0, abs(ceil(bounds[1] - bounds[3])) + 100, step):
        line_y = -50 + ceil(bounds[1]/step)*step + i
        line_points = ((bounds[0] - 10, line_y), (bounds[2]+10, line_y))
        output_intersections = set()
        for contour in glyph:
            segments = contour.segments
            for s, segment in enumerate(segments):
                last_point = segments[s-1][-1]
                segment_points = [last_point, *segment]
                segment_points = [(point.x, point.y) for point in segment_points]
                intersections = segmentSegmentIntersections(line_points, segment_points)
                for intersection in intersections:
                    if 0 <= intersection.t1 <= 1 and 0 <= intersection.t2 <= 1:
                        output_intersections.add(tuple(map(lambda x:round(x, 3), intersection.pt)))

        output_intersections = sorted(output_intersections, key=lambda x:x[0])
        points_are_inside = []

        if len(output_intersections) % 2 == 0:
            for i in range(0, len(output_intersections), 2):
                point_from = output_intersections[i]
                point_to = output_intersections[i+1]
                return_value.append((point_from, point_to))

        else:
            points_are_inside = []
            for point_index in range(1, len(output_intersections)):
                point_is_inside = False
                prev_point = output_intersections[point_index - 1]
                point = output_intersections[point_index]
                middle = interpolate_point(prev_point, point, .5)
                if point in contour_points:
                    point_index = contour_points.index(point)
                    if point in contour_points and (contour_points[point_index - 1] == prev_point or contour_points[(point_index + 1) % len(contour_points)] == prev_point):
                        point_is_inside = True
                    else:
                        point_is_inside = glyph.pointInside(middle)
                else:
                    point_is_inside = glyph.pointInside(middle)
                points_are_inside.append(point_is_inside)
                
            if len(points_are_inside) == len(output_intersections):
                for segment in create_segments(output_intersections, points_are_inside):
                    return_value.append((segment[0], segment[-1]))
    return return_value



def pan_glyph(output_glyph, slices, thickness, shape, min_length=0, flip_end=False):
    output_pen = output_glyph.getPen()
    def shape_func(pt_from, pt_to, thickness, **kwargs):
        length = hypot(pt_to[1]-pt_from[1], pt_to[0]-pt_from[0])
        if length > min_length:
            if shape == "line":
                line_shape(output_pen, pt_from, pt_to, thickness, flip_end, **kwargs)
            elif shape == "triangle":
                triangle_shape(output_pen, pt_from, pt_to, thickness, **kwargs)
            elif shape == "dumbbell":
                dumbbell_shape(output_pen, pt_from, pt_to, thickness, **kwargs)
            else:
                raise NotImplementedError

    for from_point, to_point in slices:
        shape_func(from_point, to_point, thickness)
    #glyph.draw(input_glyph.getPen())

def pan(input_font, glyph_names_to_process=None):
    Font._get_dispatcher = lambda x:None
    Glyph._get_dispatcher = lambda x:None
    Point._get_dispatcher = lambda x:None

    font_20 = Font()
    font_80 = Font()
    font_20_flipped = Font()
    font_80_flipped = Font()
    font_20.info.unitsPerEm = input_font.info.unitsPerEm
    font_80.info.unitsPerEm = input_font.info.unitsPerEm
    masters = {
        5: [font_20, font_20_flipped],
        80: [font_80, font_80_flipped]
    }
    for glyph_name in glyph_names_to_process:        
        glyph_removed_overlap = Glyph()
        glyph = input_font[glyph_name]
        BooleanGlyph(glyph).union(BooleanGlyph()).draw(glyph_removed_overlap.getPen())
        
        for angle in [0, 45, 90, 135]:
            for step in range(40, 100, 20):
                output_glyph = Glyph()
                glyph_removed_overlap.draw(output_glyph.getPen())
                rotate_glyph(output_glyph, angle)
                slices = get_pan_slices(output_glyph, step)
                slices = rotate_segments(slices, -angle)
                for half_circle_switch in [False, True]:
                    if half_circle_switch:
                        output_angle = angle + 180
                    else:
                        output_angle = angle
                    for thickness in masters.keys():
                        for flip_end in [False, True]:
                            font = masters[thickness][flip_end]
                            if output_angle == 0 and step == 40:
                                output_glyph = font.newGlyph(glyph_name)
                                output_glyph.unicodes = glyph.unicodes
                            else:
                                output_glyph = font.newGlyph(glyph_name + "_angle_" + str(output_angle) + "_step_" + str(step))
                            output_glyph.width = glyph.width
                            pan_glyph(output_glyph, [s[::-1 if half_circle_switch else 1] for s in slices], thickness, "line", min_length=80, flip_end=flip_end)
    designspace = make_designspace(masters, glyph_names_to_process)
    return compileVariableTTF(designspace)

if __name__ == "__main__":
    import cProfile, pstats
    input_font = Font("font.ufo")

    # profiler = cProfile.Profile()
    # profiler.enable()
    pan(input_font)
    # profiler.disable()
    # # stats = pstats.Stats(profiler).strip_dirs().sort_stats('tottime')  # sort by cumulative time spent in function
    # stats = pstats.Stats(profiler).sort_stats('tottime')  # sort by cumulative time spent in function
    # stats.print_stats(50)  
        