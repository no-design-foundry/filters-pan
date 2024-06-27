from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor

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
axis.minimum=20
axis.maximum=100
axis.default=20
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

glyphs = "SZYX".lower()

for angle in range(45, 360, 45):
    for step in range(40, 100, 20):
        rule = RuleDescriptor()
        rule.name = f"angle_{angle}"
        rule.conditionSets.append([dict(name="angle", minimum=angle, maximum=angle+45), dict(name="step", minimum=step, maximum=step + 40)])
        for glyph in glyphs:
            
            rule.subs.append((glyph, f"{glyph}_angle_{angle}_step_{step}"))
        doc.addRule(rule)

source = SourceDescriptor()
source.path = "masters/0_False.ufoz"
source.name = "pan.ufo"
source.familyName = "Pan"
source.styleName = "Pan"
source.location = dict(angle=0, step=20, thickness=20, flipped_end=0)
doc.addSource(source)

source = SourceDescriptor()
source.path = "masters/1_False.ufoz"
source.name = "pan.ufo"
source.familyName = "Pan"
source.styleName = "Pan"
source.location = dict(angle=0, step=20, thickness=80, flipped_end=0)
doc.addSource(source)

source = SourceDescriptor()
source.path = "masters/0_True.ufoz"
source.name = "pan.ufo"
source.familyName = "Pan"
source.styleName = "Pan"
source.location = dict(angle=0, step=20, thickness=20, flipped_end=100)
doc.addSource(source)

source = SourceDescriptor()
source.path = "masters/1_True.ufoz"
source.name = "pan.ufo"
source.familyName = "Pan"
source.styleName = "Pan"
source.location = dict(angle=0, step=20, thickness=80, flipped_end=100)
doc.addSource(source)

doc.write("designspace.designspace")