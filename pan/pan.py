from defcon import Font, Glyph, Point, Contour
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.misc.bezierTools import segmentSegmentIntersections
from math import hypot, radians, cos, sin, atan2, pi, ceil, degrees
from fontTools.pens.qu2cuPen import Qu2CuPen
from decimal import Decimal
from ufo2ft import compileVariableTTF
try:
    from .designspace import make_designspace
except:
    from designspace import make_designspace

from pathops.operations import union as skia_union
from fontPens.flattenPen import FlattenPen
from fontTools.pens.pointPen import BasePointToSegmentPen

def interpolate(a, b, t=.5):
    return a + t * (b - a)


def interpolate_point(point_a, point_b, t=.5):
    return [interpolate(a, b, t) for a, b in zip(point_a, point_b)]
    

def rotate_point_around_axis(point, axis_coos, angle_degrees):
    angle_radians = radians(angle_degrees)
    # Translate point back to origin:
    try:
        translated_x = point.x - axis_coos[0]
        translated_y = point.y - axis_coos[1]
    except AttributeError:
        translated_x = point[0] - axis_coos[0]
        translated_y = point[1] - axis_coos[1]
    
    # Rotate point
    angle_cos = cos(angle_radians)
    angle_sin = sin(angle_radians)
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
            rotate_point_around_axis(point, (0, 0), angle)

def rotate_segments(segments, angle):
    segments_len = len(segments)
    new_segments = [None] * segments_len
    for segment_index in range(segments_len):
        new_segment = [rotate_point_around_axis(point, (0, 0), angle) for point in segments[segment_index]]
        new_segments[segment_index] = new_segment
    return new_segments
        
def create_segments(x, y):
    segments = []
    start = 0
    for i in range(len(y)):
        if not y[i]:
            segments.append((x[start], x[i]))
            start = i + 1
    if start < len(x):
        segments.append((x[start], x[-1]))
    return segments
    
def line_shape(output_glyph_contours, point_a, point_b, thickness, flip_end=False):
    # it was 10% to not use pen here
    (x_a, y_a), (x_b, y_b) = point_a, point_b
    angle = atan2(y_b - y_a, x_b - x_a) + pi / 2
    x_offset = cos(angle) * thickness
    y_offset = sin(angle) * thickness

    first_point = (x_a + x_offset, y_a + y_offset)
    second_point = (x_b + x_offset, y_b + y_offset)
    third_point = (x_b - x_offset, y_b - y_offset)
    fourth_point = (x_a - x_offset, y_a - y_offset)
    point_objects = [None] * 4

    point_objects[0] = Point(first_point, segmentType="line")
    point_objects[1 if flip_end in {True, None} else 2] = Point(third_point, segmentType="line")
    point_objects[2 if flip_end in {True, None} else 1] = Point(second_point, segmentType="line")
    point_objects[3] = Point(fourth_point, segmentType="line")

    contour = Contour()
    contour._points = point_objects
    output_glyph_contours.append(contour)
    

def get_pan_slices(glyph, step):
    contour_points = []
    for contour in glyph._contours:
        contour_points.extend([(point.x, point.y) for point in contour])
    bounds = glyph.bounds
    return_value = []
    if bounds is None:
        return return_value

    for i in range(0, abs(ceil(bounds[1] - bounds[3])) + step * 2, step):
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
                if segment_points[0][-1] == line_y:
                    output_intersections.add(segment_points[0])
                if segment_points[-1][-1] == line_y:
                    output_intersections.add(segment_points[-1])
                for intersection in intersections:
                    if 0 <= intersection.t1 <= 1 and 0 <= intersection.t2 <= 1:
                        output_intersections.add(tuple(map(lambda x:round(x, 3), intersection.pt)))

        output_intersections = sorted(output_intersections, key=lambda x:x[0])
        points_are_inside = []

        output_intersections_len = len(output_intersections)
        contour_points_len = len(contour_points)
        if output_intersections_len % 2 == 0:
            return_value.extend([(output_intersections[i], output_intersections[i+1]) for i in range(0, output_intersections_len, 2)])

        else:
            points_are_inside = []
            for point_index in range(1, output_intersections_len):
                point_is_inside = False
                prev_point = output_intersections[point_index - 1]
                point = output_intersections[point_index]
                middle = interpolate_point(prev_point, point, .5)
                if point in contour_points:
                    point_index = contour_points.index(point)
                    if point in contour_points and (contour_points[point_index - 1] == prev_point or contour_points[(point_index + 1) % contour_points_len] == prev_point):
                        point_is_inside = True
                    else:
                        point_is_inside = glyph.pointInside(middle)
                else:
                    point_is_inside = glyph.pointInside(middle)
                points_are_inside.append(point_is_inside)
                
            if len(points_are_inside) == (output_intersections_len - 1):
                for segment in create_segments(output_intersections, points_are_inside):
                    return_value.append((segment[0], segment[-1]))
            else:
                raise NotImplementedError
                # print(output_intersections)
                # return_value.append((output_intersections[0], output_intersections[-1]))
    return return_value



def pan_glyph(output_glyph, slices, thickness, min_length=0, flip_end=False):
    def shape_func(pt_from, pt_to, thickness, **kwargs):
        length = hypot(pt_to[1]-pt_from[1], pt_to[0]-pt_from[0])
        if length > min_length:
            line_shape(output_glyph._contours, pt_from, pt_to, thickness, flip_end, **kwargs)

    for from_point, to_point in slices:
        shape_func(from_point, to_point, thickness)

def pan(input_font, glyph_names_to_process, scale_factor, min_length):
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
    glyph_removed_overlap = Glyph()
    for glyph_name in glyph_names_to_process:        
        glyph = input_font[glyph_name]
        flattened = BooleanGlyph()
        flatten_pen = FlattenPen(flattened.getPen(), approximateSegmentLength=50)
        glyph.draw(flatten_pen)
        skia_union(flattened, glyph_removed_overlap.getPen())

        
        for angle in [0, 45, 90, 135]:
            for step in range(40, 100, 20):
                output_glyph = Glyph()
                glyph_removed_overlap.draw(output_glyph.getPen())
                rotate_glyph(output_glyph, angle)
                slices = get_pan_slices(output_glyph, int(step * scale_factor))
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
                            pan_glyph(output_glyph, [s[::-1 if half_circle_switch else 1] for s in slices], thickness, min_length=min_length, flip_end=flip_end)
        glyph_removed_overlap._contours = []
    designspace = make_designspace(masters, glyph_names_to_process)
    return compileVariableTTF(designspace, optimizeGvar=False)

if __name__ == "__main__":
    import cProfile, pstats
    from defcon.objects.base import BaseObject
    from datetime import datetime

    BaseObject.addObserver = lambda *args, **kwargs: None
    BaseObject.postNotification = lambda *args, **kwargs: None
    BaseObject.removeObserver = lambda *args, **kwargs: None
    BaseObject.beginSelfNotificationObservation = lambda *args, **kwargs: None
    BaseObject.endSelfContourNotificationObservation = lambda *args, **kwargs: None
    BaseObject.dirty = lambda : None
    BaseObject.dispatcher = None

    PROFILE = True

    input_font = Font("../font.ufo")
    if PROFILE:
        profiler = cProfile.Profile()
        profiler.enable()
    start = datetime.now()
    pan(input_font, ["A", "B", "C", "D", "E"], is_quadratic=True)
    print((datetime.now() - start).total_seconds())
    if PROFILE:
        profiler.disable()
        # stats = pstats.Stats(profiler).strip_dirs().sort_stats('tottime')  # sort by cumulative time spent in function
        stats = pstats.Stats(profiler).sort_stats('tottime')  # sort by cumulative time spent in function
        stats.print_stats(50)  
        