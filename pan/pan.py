from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.misc.bezierTools import segmentSegmentIntersections
from math import hypot, radians, cos, sin, atan2, pi, ceil
from ufo2ft import compileVariableTTF
try:
    from .designspace import make_designspace
except:
    from designspace import make_designspace

from pathops.operations import union as skia_union
from fontPens.flattenPen import FlattenPen
from ufoLib2.objects.contour import Contour
from ufoLib2.objects.glyph import Glyph
from ufoLib2.objects.point import Point
from ufoLib2.objects.font import Font
from ufoLib2.objects.component import Component

from fontTools.pens.pointInsidePen import PointInsidePen


def pointInside(self, coordinates, evenOdd=False):
    (x, y) = coordinates
    pen = PointInsidePen(glyphSet=None, testPoint=(x, y), evenOdd=evenOdd)
    self.draw(pen)
    return pen.getResult()

setattr(Glyph, "pointInside", pointInside)

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
        for point in contour:
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

    point_objects[0] = Point(*first_point, type="line")
    point_objects[1 if flip_end in {True, None} else 2] = Point(*third_point, type="line")
    point_objects[2 if flip_end in {True, None} else 1] = Point(*second_point, type="line")
    point_objects[3] = Point(*fourth_point, type="line")

    contour = Contour()
    contour.points = point_objects
    output_glyph_contours.appendContour(contour)
    
def contour_to_segments(contour):
    segments = []
    segment = []
    for point in contour:
        segment.append(point)
        if point.type in ('line', 'curve', 'qcurve'):
            segments.append(segment)
            segment = []
    return segments


def get_pan_slices(glyph, step, shadow=False, correction_offset=.001):
    contour_points = []
    for contour in glyph:
        contour_points.extend([(point.x, point.y) for point in contour])
    bounds = glyph.getBounds()
    return_value = []
    if bounds is None:
        return return_value

    for i in range(0, abs(ceil(bounds[1] - bounds[3])) + step * 2, step):
        line_y = -step + ceil(bounds[1]/step)*step + i + correction_offset
        line_points = ((bounds[0] - 10, line_y), (bounds[2]+10, line_y))
        output_intersections = set()
        for contour in glyph:
            segments = contour_to_segments(contour)
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
        output_intersections_len = len(output_intersections)

        try:
            if shadow:
                return_value.append((output_intersections[0], output_intersections[-1]))
            else:
                return_value.extend([(output_intersections[i], output_intersections[i+1]) for i in range(0, output_intersections_len, 2)])
        except IndexError:
            pass

    return return_value

def pan_glyph(output_glyph, slices, thickness, min_length=0, flip_end=False):
    def shape_func(pt_from, pt_to, thickness, **kwargs):
        length = hypot(pt_to[1]-pt_from[1], pt_to[0]-pt_from[0])
        if length > min_length:
            line_shape(output_glyph, pt_from, pt_to, thickness, flip_end, **kwargs)

    for from_point, to_point in slices:
        shape_func(from_point, to_point, thickness)

def pan(input_font, step, glyph_names_to_process=None, shadow=False, scale_factor=1):
    font_20 = Font()
    font_80 = Font()
    font_20_flipped = Font()
    font_80_flipped = Font()
    font_20.info.unitsPerEm = input_font.info.unitsPerEm
    font_80.info.unitsPerEm = input_font.info.unitsPerEm
    masters = {
        5: [font_20, font_20_flipped],
        100: [font_80, font_80_flipped]
    }
    glyph_removed_overlap = Glyph()
    if glyph_names_to_process is None:
        glyph_names_to_process = input_font.keys()

    classes = {}

    for glyph_name in glyph_names_to_process:        
        glyph = input_font[glyph_name]
        flattened = BooleanGlyph()
        flatten_pen = FlattenPen(flattened.getPen(), approximateSegmentLength=50*scale_factor)
        glyph.draw(flatten_pen)
        skia_union(flattened, glyph_removed_overlap.getPen())
        classes[glyph_name] = []
        
        for angle in [0, 45, 90, 135]:
            output_glyph = Glyph()
            glyph_removed_overlap.draw(output_glyph.getPen())
            rotate_glyph(output_glyph, angle)
            slices = get_pan_slices(output_glyph, int(step / 2), shadow=shadow)
            slices = rotate_segments(slices, -angle)
            for half_circle_switch in [False, True]:
                if half_circle_switch:
                    output_angle = angle + 180
                else:
                    output_angle = angle
                for thickness in masters.keys():
                    for flip_end in [False, True]:
                        font = masters[thickness][flip_end]
                        angle_suffix = None
                        if output_angle == 0:
                            output_glyph = font.newGlyph(glyph_name)
                            output_glyph.unicodes = glyph.unicodes
                        else:
                            angle_suffix = f"_angle_{output_angle}"
                            output_glyph = font.newGlyph(glyph_name + angle_suffix)
                        output_glyph.width = glyph.width
                        classes[glyph_name].append(output_glyph.name)
                        pan_glyph(
                            output_glyph, [s[::-1 if half_circle_switch else 1] for s in slices],
                            thickness if thickness != 100 else step * .75,
                            min_length=step,
                            flip_end=flip_end
                            )
                        if angle_suffix:
                            renamed_components = []
                            for component in glyph.components:
                                renamed_components.append(Component(component.baseGlyph + angle_suffix, component.transformation))
                            output_glyph.components = renamed_components   
                        else:
                            output_glyph.components = glyph.components
        glyph_removed_overlap.contours = []
    

    designspace = make_designspace(masters, glyph_names_to_process)
    if len(input_font.kerning.keys()):
        kerning = {(f"public.kern1.{k[0]}",f"public.kern2.{k[1]}"):v for k,v in input_font.kerning.items()}
        for source in designspace.sources:
            source.font.kerning.update(kerning)
            if source.copyFeatures:
                for group_name, members in classes.items():
                    source.font.groups[f"public.kern1.{group_name}"] = members
                    source.font.groups[f"public.kern2.{group_name}"] = members

    return compileVariableTTF(designspace, optimizeGvar=False)


def main():
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Apply Pan filter onto UFO font.")
    parser.add_argument("input_file", type=Path, help="Path to the input font file.")
    parser.add_argument("step", type=int, help="Step")
    parser.add_argument("--output_dir", "-o", type=Path, help="Path to the output file. If not provided, the output will be saved in the same directory as the input file.")
    parser.add_argument("--glyph_names", "-g", type=str, nargs="+", help="List of glyph names to process. If not provided, all glyphs will be processed.")

    args = parser.parse_args()

    input_file = args.input_file
    step = args.step
    output_dir = args.output_dir

    ufo = Font.open(input_file)
    glyph_names = args.glyph_names if args.glyph_names else ufo.keys()

    pan_output = pan(ufo, args.step, shadow=False, glyph_names_to_process=glyph_names)
    output_file_name = f"{input_file.stem}_{step}_Pan.ttf"
    pan_output.save(output_dir/output_file_name if output_dir else input_file.parent/output_file_name)


if __name__ == "__main__":
    main()