from neomodel import StructuredNode, Relationship, RelationshipTo, RelationshipFrom
from neomodel import cardinality
from neomodel.properties import StringProperty, IntegerProperty, DateProperty, UniqueIdProperty, DateTimeProperty, \
    JSONProperty
from neomodel.relationship import StructuredRel

# Relationship names
REL_PATIENT_FAMILY = 'InFamily'
REL_PATIENT_PROJECT = 'InProject'
REL_PATIENT_DIAGNOSIS = 'HasDiagnosis'
REL_PATIENT_ORDER = 'HasOrder'
REL_PATIENT_MATERIAL = 'HasMaterial'
REL_ORDER_ANALYSIS = 'HasAnalysis'
REL_ANALYSIS_ANALYSISTYPE = 'OfType'
REL_ANALYSIS_RESULT = 'HasResult'
REL_ANALYSIS_MATERIAL = 'OnMaterial'
REL_ANALYSIS_FUSION = 'HasFusion'
REL_ANALYSIS_ANEUPLOIDY = 'HasAneuploidy'
REL_MATERIAL_MATERIAL = 'CreatedFrom'


# Structured relationships with properties
class DiagnosisPatientRel(StructuredRel):
    """Structured relationship between a patient and a diagnosis.
    Specifies the date at which the diagnosis was made, the 
    age of the patient at this time and the diagnosis addition (opt.)
    """
    date = DateProperty()
    age_at_diagnosis = IntegerProperty()
    addition = StringProperty()


class AnalysisFusionRel(StructuredRel):
    text = StringProperty()


class AnalysisResultRel(StructuredRel):
    result_id = StringProperty()
    description = StringProperty()
    value = StringProperty()


# Node entities
class Patient(StructuredNode):
    patient_id = IntegerProperty(unique_index=True)
    name = StringProperty()
    birthday = DateProperty()
    gender = StringProperty()

    in_family = Relationship('Family', REL_PATIENT_FAMILY)    
    in_project = Relationship('Project', REL_PATIENT_PROJECT)
    #default cardinality >=0
    has_diagnoses = RelationshipTo('Diagnosis', REL_PATIENT_DIAGNOSIS, model=DiagnosisPatientRel)     
    has_orders = RelationshipTo('Order', REL_PATIENT_ORDER) 
    has_materials = RelationshipTo('Material', REL_PATIENT_MATERIAL)


class Family(StructuredNode):
    family_id = IntegerProperty(unique_index=True)

    # For each family there must be at least one member
    has_members = Relationship('Patient', REL_PATIENT_FAMILY)


class Project(StructuredNode):
    name = StringProperty(unique_index=True)

    # For each project there must be at least one participant
    has_participants = Relationship('Patient', REL_PATIENT_PROJECT)


class Diagnosis(StructuredNode):
    icd = StringProperty()
    name = StringProperty(unique_index=True)

    has_patients = RelationshipFrom('Patient', REL_PATIENT_DIAGNOSIS, model=DiagnosisPatientRel)


class Order(StructuredNode):
    order_id = StringProperty(unique_index=True)
    date = DateProperty()
    type = StringProperty()
    study_id = StringProperty()
    study_name = StringProperty()

    for_patient = RelationshipFrom('Patient', REL_PATIENT_ORDER, cardinality=cardinality.One)
    has_analyses = RelationshipTo('Analysis', REL_ORDER_ANALYSIS)


class Analysis(StructuredNode):
    # __abstract_node__ = True
    analysis_id = StringProperty(unique_indx=True)
    qsv_question = StringProperty()
    qsv_analysis_assessment = StringProperty()
    analytical_result = StringProperty()

    for_order = RelationshipFrom('Order', REL_ORDER_ANALYSIS, cardinality=cardinality.One)
    has_results = Relationship('Result', REL_ANALYSIS_RESULT, model=AnalysisResultRel)
    on_material = Relationship('Material', REL_ANALYSIS_MATERIAL)


class ArrayCGHAnalysis(Analysis):
    chromosomes = StringProperty()

    showed_fusions = Relationship('Fusion', REL_ANALYSIS_FUSION, model=AnalysisFusionRel)
    has_aneuploidy = Relationship('Aneuploidy', REL_ANALYSIS_ANEUPLOIDY)


class RNASeqAnalysis(Analysis):
    showed_fusions = Relationship('Fusion', REL_ANALYSIS_FUSION, model=AnalysisFusionRel)


class KaryotypeAnalysis(Analysis):
    pass


class Fusion(StructuredNode):
    name = StringProperty(unique_index=True)

    found_in = Relationship('Analysis', REL_ANALYSIS_FUSION, model=AnalysisFusionRel)


class Aneuploidy(StructuredNode):
    name = StringProperty(unique_index=True)
    found_in = Relationship('ArrayCGHAnalysis', REL_ANALYSIS_ANEUPLOIDY)


class Result(StructuredNode):
    name = StringProperty(unique_index=True)

    for_analyses = Relationship('Analysis', REL_ANALYSIS_RESULT, model=AnalysisResultRel)


class Material(StructuredNode):
    material_id = StringProperty(unique_idx=True)
    type_id = StringProperty()
    description = StringProperty()

    of_patient = RelationshipFrom('Patient', REL_PATIENT_MATERIAL)
    created_from = RelationshipTo('Material', REL_MATERIAL_MATERIAL)
    used_in_analyses = Relationship('Analysis', REL_ANALYSIS_MATERIAL)


class _Neodash_Dashboard(StructuredNode):
    uuid = UniqueIdProperty()
    title = StringProperty()
    date = DateTimeProperty()
    user = StringProperty()
    version = StringProperty()
    content = JSONProperty()