from defcon import Font, Glyph
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.misc.bezierTools import segmentSegmentIntersections
from math import hypot

THICKNESS=16
ANGLE=-1480
STEPS=23

size(2000, 1000)

def interpolate(a, b, t=.5):
    return a + t * (b - a)


def interpolate_point(point_a, point_b, t=.5):
    return [interpolate(a, b, t) for a, b in zip(point_a, point_b)]
    

def rotate_point_around_axis(point, axis_coos, angle_degrees):
    angle_radians = radians(angle_degrees)
    
    # Translate point back to origin:
    translated_x = point.x - axis_coos[0]
    translated_y = point.y - axis_coos[1]
    
    # Rotate point
    rotated_x = translated_x * cos(angle_radians) - translated_y * sin(angle_radians)
    rotated_y = translated_x * sin(angle_radians) + translated_y * cos(angle_radians)
    
    # Translate point back to its original location
    final_x = rotated_x + axis_coos[0]
    final_y = rotated_y + axis_coos[1]
    
    point.x = final_x
    point.y = final_y



def rotate_glyph(glyph, angle):
    for contour in glyph:
        for p, point in enumerate(contour):
            rotate_point_around_axis(point, (0, 0), angle)
        
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
    
def line_shape(point_a, point_b, thickness=THICKNESS):
    (x_a, y_a), (x_b, y_b) = point_a, point_b
    angle = atan2(point_b[1] - point_a[1], point_b[0] - point_a[0]) + pi/2
    x_offset, y_offset = cos(angle) * thickness, sin(angle) * thickness
    bez = BezierPath()
    bez.moveTo((x_a + x_offset, y_a + y_offset))
    bez.lineTo((x_b + x_offset, y_b + y_offset))
    
    x_offset, y_offset = cos(angle + pi) * thickness, sin(angle + pi) * thickness
    bez.lineTo((x_b + x_offset, y_b + y_offset))
    bez.lineTo((x_a + x_offset, y_a + y_offset))
    bez.closePath()
    drawPath(bez)

def triangle_shape(point_a, point_b, thickness):
    (x_a, y_a), (x_b, y_b) = point_a, point_b
    angle = atan2(point_b[1] - point_a[1], point_b[0] - point_a[0]) + pi/2
    x_offset, y_offset = cos(angle) * THICKNESS, sin(angle) * THICKNESS
    bez = BezierPath()
    bez.moveTo((x_a + x_offset, y_a + y_offset))
    
    x_offset, y_offset = cos(angle + pi) * THICKNESS, sin(angle + pi) * THICKNESS
    bez.lineTo((x_a + x_offset, y_a + y_offset))
    
    bez.lineTo((x_b, y_b))
    bez.closePath()
    drawPath(bez)   

def circle(center, radius, tension=1):
    x, y = center
    bez = BezierPath()
    bez.moveTo((x, y+radius))
    bez.curveTo((x - radius * tension, y + radius), (x - radius, y + radius * tension), (x - radius, y))
    bez.curveTo((x - radius, y - radius * tension), (x - radius * tension, y - radius), (x, y - radius))
    bez.curveTo((x + radius * tension, y - radius), (x + radius, y - radius * tension), (x + radius, y))
    bez.curveTo((x + radius, y + radius * tension), (x + radius * tension, y + radius), (x, y + radius))
    drawPath(bez)

def dumbbell_shape(point_a, point_b, thickness):
    (x_a, y_a), (x_b, y_b) = point_a, point_b
    circle(point_a, 20)
    circle(point_b, 20)
    line_shape(point_a, point_b, 4)

font = Font("MutatorSansBoldWide.ufo")
glyph = font["W"]
removed_overlap = BooleanGlyph(glyph) 
removed_overlap = removed_overlap.xor(BooleanGlyph())
glyph.clear()
removed_overlap.draw(glyph.getPen())
print(glyph)

rotate_glyph(glyph, ANGLE)

contour_points = []
for contour in glyph:
    for point in contour:
        contour_points.append((point.x, point.y))

fill(1, 0, 1)
shape = triangle_shape 

bounds = glyph.bounds  
rotate(-ANGLE)


for i in range(0, abs(ceil(bounds[1] - bounds[3])), STEPS):
    line_y = bounds[1] + i
    line_points = ((bounds[0] - 10, line_y), (bounds[2]+10, line_y))
    output_intersections = set()
    has_on_line_points = False
    for contour in glyph:
        segments = contour.segments
        for s, segment in enumerate(segments):
            last_point = segments[s-1][-1]
            segment_points = [last_point, *segment]
            segment_points = [(point.x, point.y) for point in segment_points]
            intersections = segmentSegmentIntersections(line_points, segment_points)
            if segment_points[0][-1] == i and segment_points[-1][-1] == i:
                output_intersections.add(segment_points[0])
            for intersection in intersections:
                if 0 < intersection.t1 <= 1 and 0 <= intersection.t2 <= 1:
                    output_intersections.add(tuple(map(lambda x:round(x, 3), intersection.pt)))

    output_intersections = sorted(output_intersections, key=lambda x:x[0])
    points_are_inside = []
    
    
    if len(output_intersections) % 2 == 0:
        for i in range(0, len(output_intersections), 2):
            point_from = output_intersections[i]
            point_to = output_intersections[i+1]
            shape(point_from, point_to, THICKNESS)
    else:
        points_are_inside = []
        for point_index in range(1, len(output_intersections)):
            point_is_inside = False
            prev_point = output_intersections[point_index - 1]
            point = output_intersections[point_index]
            middle = interpolate_point(prev_point, point, .5)
            if point in contour_points:
                point_index = contour_points.index(point)
                if point in contour_points and (contour_points[point_index - 1] == prev_point or contour_points[point_index + 1] == prev_point):
                    point_is_inside = True
                else:
                    point_is_inside = glyph.pointInside(middle)
            else:
                point_is_inside = glyph.pointInside(middle)
            points_are_inside.append(point_is_inside)
            
        if len(points_are_inside) == len(output_intersections):
            for segment in create_segments(output_intersections, points_are_inside):
                shape(segment[0], segment[-1], THICKNESS)
