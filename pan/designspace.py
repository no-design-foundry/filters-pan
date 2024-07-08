from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor

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
    axis.name="step"
    axis.minimum=40
    axis.maximum=100
    axis.default=40
    axis.tag="STEP"
    axis.labelNames={"en": "Step"}
    axis.axisOrdering=1
    doc.addAxis(axis)

    axis = AxisDescriptor()
    axis.name="thickness"
    axis.minimum=20
    axis.maximum=80
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
        for step in range(40, 100, 20):
            if angle == 0 and step == 40:
                pass
            else:
                rule = RuleDescriptor()
                rule.name = f"angle_{angle}_{step}"
                rule.conditionSets.append([dict(name="angle", minimum=angle, maximum=angle+45), dict(name="step", minimum=step, maximum=step + 20)])
                for glyph_name in glyph_names:
                        rule.subs.append((glyph_name, f"{glyph_name}_angle_{angle}_step_{step}"))
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
    source.font = masters[80][0]
    source.name = "pan.ufo"
    source.familyName = "Pan"
    source.styleName = "Pan"
    source.location = dict(angle=0, step=40, thickness=80, flipped_end=0)
    doc.addSource(source)

    source = SourceDescriptor()
    source.font = masters[5][1]
    source.name = "pan.ufo"
    source.familyName = "Pan"
    source.styleName = "Pan"
    source.location = dict(angle=0, step=40, thickness=20, flipped_end=100)
    doc.addSource(source)

    source = SourceDescriptor()
    source.font = masters[80][1]
    source.name = "pan.ufo"
    source.familyName = "Pan"
    source.styleName = "Pan"
    source.location = dict(angle=0, step=40, thickness=80, flipped_end=100)
    doc.addSource(source)

    return doc