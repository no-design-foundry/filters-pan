from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor

thickness_max = 100

def make_designspace(masters, glyph_names):
    doc = DesignSpaceDocument()

    axis = AxisDescriptor()
    axis.name="angle"
    axis.minimum=0
    axis.maximum=360
    axis.default=0
    axis.tag="ANGL"
    axis.labelNames={"en": "Angle"}
    axis.axisOrdering=0
    doc.addAxis(axis)

    axis = AxisDescriptor()
    axis.name="thickness"
    axis.minimum=20
    axis.maximum=thickness_max
    axis.default=20
    axis.tag="THCK"
    axis.labelNames={"en": "Thickness"}
    axis.axisOrdering=2
    doc.addAxis(axis)

    axis = AxisDescriptor()
    axis.name="flipped_end"
    axis.minimum=0
    axis.maximum=100
    axis.default=0
    axis.tag="FLIP"
    axis.labelNames={"en": "Flipped End"}
    axis.axisOrdering=3
    doc.addAxis(axis)

    for angle in range(0, 360, 45):
        if angle == 0:
            pass
        else:
            rule = RuleDescriptor()
            rule.name = f"angle_{angle}"
            rule.conditionSets.append([dict(name="angle", minimum=angle, maximum=angle+45)])
            for glyph_name in glyph_names:
                    rule.subs.append((glyph_name, f"{glyph_name}_angle_{angle}"))
            doc.addRule(rule)

    source = SourceDescriptor()
    # source.path = "masters/0_False.ufoz"
    source.font = masters[5][0]
    source.name = "pan.ufo"
    source.familyName = "Pan"
    source.styleName = "Pan"
    source.location = dict(angle=0, step=40, thickness=20, flipped_end=0)
    source.copyLib = True
    source.copyInfo = True
    source.copyFeatures = True
    doc.addSource(source)

    source = SourceDescriptor()
    # source.path = "masters/1_False.ufoz"
    source.font = masters[thickness_max][0]
    source.name = "pan.ufo"
    source.familyName = "Pan"
    source.styleName = "Pan"
    source.location = dict(angle=0, step=40, thickness=thickness_max, flipped_end=0)
    doc.addSource(source)

    source = SourceDescriptor()
    source.font = masters[5][1]
    source.name = "pan.ufo"
    source.familyName = "Pan"
    source.styleName = "Pan"
    source.location = dict(angle=0, step=40, thickness=20, flipped_end=100)
    doc.addSource(source)

    source = SourceDescriptor()
    source.font = masters[thickness_max][1]
    source.name = "pan.ufo"
    source.familyName = "Pan"
    source.styleName = "Pan"
    source.location = dict(angle=0, step=40, thickness=thickness_max, flipped_end=100)
    doc.addSource(source)

    return doc