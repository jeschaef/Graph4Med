import json
import random
from datetime import date, datetime

import pandas as pd
from faker import Faker
from neomodel import db

from connect import *
from model import *
from model import _Neodash_Dashboard
from utils import read_resource, read_csv

# Specify Neo4J url for neomodel
db.set_connection(f"bolt://{neo4j_user}:{neo4j_password}@{neo4j_server}")

# Logger
log = logging.getLogger()


def hash_patient_id(id):
    """Hash a patient id (created by synthea) to a smaller integer"""
    return abs(hash(id) % 1000000)


class Control:
    """Handle the deletion and creation of the Neo4J database.
    """

    def __init__(self) -> None:
        """Constructor"""
        pass


    def deleteData(self):
        """Delete all the nodes and relationships.
        """
        log.info('Deleting all nodes and relationships...')
        query = 'MATCH (n) WHERE NOT n:_Neodash_Dashboard DETACH DELETE n'
        db.cypher_query(query)

    def create_nodes(self):
        """Create nodes and their relationships in neo4j
        """
        log.info('Creating nodes ...')
        self.create_patients()
        self.create_families()
        self.create_projects()
        self.create_diagnoses()
        self.create_orders()
        self.create_materials()
        self.create_analysis()
        self.create_fusions_rnaseq()
        self.create_fusions_array_cgh()
        self.merge_fusions()
        self.create_results()

    @db.transaction
    def create_patients(self, n=100):
        """Create one Patient node with attributes
        [patient_id, name, birthday, gender] per patient.
        """
        log.info('Creating patient nodes ...')

        # Load patient data from csv
        patients = read_csv('patients.csv', nrows=n)
        patients['NAME'] = patients['LAST'] + ', ' + patients['FIRST']
        patients['BIRTHDATE'] = pd.to_datetime(patients['BIRTHDATE'])

        # Generate patients from records
        for idx, row in patients.iterrows():
            p = Patient(patient_id=hash_patient_id(row['Id']),
                        name=row['NAME'],
                        birthday=row['BIRTHDATE'].date(),
                        gender=row['GENDER'])
            p.save()

        num_patients = len(Patient.nodes)
        log.info(f'Created {num_patients} Patients')

    @db.transaction
    def create_families(self):
        """Create some Family nodes and link some patient
        to the family he/she belongs to.
        """
        log.info('Creating family nodes ...')

        # Iterate over patients
        for p in Patient.nodes.all():
            # Get/create a family
            id = int(random.uniform(0, 0.8 * len(Patient.nodes)))
            fam = Family.get_or_create({'family_id': id})[0]

            # Create relationship between family and patient
            p.in_family.connect(fam)

    @db.transaction 
    def create_projects(self):
        """Create some project nodes (attributes [name]) and link
        patients to the projects they attended.
        """
        log.info('Creating project nodes ...')

        for p in Patient.nodes.all():

            # Get/create a project
            id = int(random.uniform(0, 0.1 * len(Patient.nodes)))
            prj = Project.get_or_create({'name': f'Project #{id}'})[0]

            # Create relationship between project and patient
            p.in_project.connect(prj)

    @db.transaction
    def create_diagnoses(self, limit=80):
        """Create all Diagnosis nodes and he had with attributes [diagnosis_id, icd, name].
        Link each patient to his diagnoses where the relationship contains the properties
        [date (of diagnosis), age_at_diagnosis, addition].
        """
        log.info('Creating diagnosis nodes ...')

        conds = read_csv('conditions.csv')
        conds = conds.drop(['STOP', 'ENCOUNTER'], axis=1)

        fake = Faker()

        # Create diagnoses nodes
        for i, ((code, name), group) in enumerate(conds.groupby(['CODE', 'DESCRIPTION']), start=1):

            if i >= limit:
                break

            diag = Diagnosis(name=name, icd=code)
            diag.save()

            # Link patients
            for _, row in group.iterrows():
                try:
                    p = Patient.nodes.get(patient_id=hash_patient_id(row['PATIENT']))
                except Patient.DoesNotExist:
                    continue

                # Create structured relationship between diagnosis and patient (n:m)
                today = date.today()
                age = today.year - p.birthday.year - ((today.month, today.day) < (p.birthday.month, p.birthday.day))
                args = {
                    'date': datetime.strptime(row['START'], "%Y-%m-%d"),
                    'age_at_diagnosis': int(random.random() * age),
                    'addition': fake.pystr()}
                p.has_diagnoses.connect(diag, args)
                diag.has_patients.connect(p, args)


        # Create ALL-Diagnosis
        diag = Diagnosis(name='Lymphatische Vorläuferneoplasien_B lymphoblastische Leukämie', icd='1234567')
        diag.save()

        # Link all patients
        for p in Patient.nodes.all():
            # Create structured relationship between diagnosis and patient (n:m)
            today = date.today()
            age = today.year - p.birthday.year - ((today.month, today.day) < (p.birthday.month, p.birthday.day))
            args = {
                'date': datetime.strptime(row['START'], "%Y-%m-%d"),
                'age_at_diagnosis': int(random.random() * age),
                'addition': fake.pystr()}
            p.has_diagnoses.connect(diag, args)
            diag.has_patients.connect(p, args)

        num_diag = len(Diagnosis.nodes)
        log.info(f'Created {num_diag} Diagnoses')

    @db.transaction
    def create_orders(self):
        """Create an Order node for each order and connect
        orders and patients with a relationship.
        """
        log.info('Creating order nodes ...')

        fake = Faker()

        # For each patient add each of his orders
        for p in Patient.nodes:

            for i in range(random.randint(1,2)):

                # Create an Order
                study_id = random.randint(0, 10)
                o = Order(order_id=f'{p.patient_id}#{i}',
                        date=fake.date_between(),
                        type=f'OrderType #{random.randint(0, 4)}',
                        study_id=f'Study #{study_id}',
                        study_name=f'Study #{study_id}')
                o.save()

                # Create order-patient relationship (n:1)
                o.for_patient.connect(p)
                p.has_orders.connect(o)

        num_orders = len(Order.nodes)
        log.info(f'Created {num_orders} Orders')

    @db.transaction
    def create_materials(self):
        """Create a Material node for each material and submaterial.
        Connect it to the corresponding patient where it comes from
        """
        log.info('Creating material nodes ...')

        # Iterate over all patients
        for p in Patient.nodes:

            # Create 3 main materials for each patient
            materials = [None, None, None]
            for i in range(3):

                # Create a material
                m = Material(material_id=f"{p.patient_id}#Mat{i}",
                             description="DNA,RNA,etc.",
                             type_id=f"Type {i}")
                m.save()

                p.has_materials.connect(m)
                m.of_patient.connect(p)
                materials[i] = m

            # Create 0-2 submaterials for each material
            for m2 in materials:
                for i in range(random.randint(0, 2)):
                    m = Material(material_id=f"{m2.material_id}-{i}",
                                 description=f"{m2.description}",
                                 type_id=f"{m2.type_id}-Sub{i}")
                    m.save()
                    m.created_from.connect(m2)
        
        num_materials = len(Material.nodes)
        log.info(f'Created {num_materials} Materials')

    @db.transaction
    def create_analysis(self):
        """Create an Analysis node for each analysis instance with the attributes 
        [analysis_id, qsv_question,qsv_analysis_assessment, analytical_result]. 
        Create analysis-order relationships between the analysis and the corresponding order (n:1)
        and connect each analysis to the specific type of analysis.

        """
        log.info('Creating analysis nodes...')

        fake = Faker()

        # Iterate over all orders
        for o in Order.nodes:

            # Create 0-1 RNASeqAnalysis nodes from records
            if random.random() > 0.5:
                a = RNASeqAnalysis(analysis_id=f"{o.order_id}#RNASeq",
                            analytical_result=fake.pystr(),
                            qsv_question=fake.pystr(),
                            qsv_analysis_assessment=fake.pystr())
                a.save()

                # Create analysis-order relationships (n:1)
                a.for_order.connect(o)
                o.has_analyses.connect(a)

                # Create analysis-material relationship (1:n)
                p = o.for_patient.single()
                materials = p.has_materials.all()
                m = random.choice(materials)    # choose material randomly

                # Check if there is a more specific submaterial
                m2 = m.created_from.get_or_none()
                if m2 is not None:
                    m = m2

                a.on_material.connect(m)
                m.used_in_analyses.connect(a)

            # Create 0-1 ArrayCGHAnalysis nodes from records
            if random.random() > 0.5:
                a = ArrayCGHAnalysis(analysis_id=f"{o.order_id}#ArrayCGH",
                            analytical_result=fake.pystr(),
                            qsv_question=fake.pystr(),
                            qsv_analysis_assessment=fake.pystr())
                a.save()

                # Create analysis-order relationships (n:1)
                a.for_order.connect(o)
                o.has_analyses.connect(a)

                # Create analysis-material relationship (1:n)
                p = o.for_patient.single()
                materials = p.has_materials.all()
                m = random.choice(materials)  # choose material randomly

                # Check if there is a more specific submaterial
                m2 = m.created_from.get_or_none()
                if m2 is not None:
                    m = m2

                a.on_material.connect(m)
                m.used_in_analyses.connect(a)

            # Create 0-1 karyotype analysis nodes
            if random.random() > 0.5:
                a = KaryotypeAnalysis(analysis_id=f"{o.order_id}#ArrayCGH",
                            analytical_result=fake.pystr(),
                            qsv_question=fake.pystr(),
                            qsv_analysis_assessment=fake.pystr())
                a.save()

                # Create analysis-order relationships (n:1)
                a.for_order.connect(o)
                o.has_analyses.connect(a)

                # Create analysis-material relationship (1:n)
                p = o.for_patient.single()
                materials = p.has_materials.all()
                m = random.choice(materials)  # choose material randomly

                # Check if there is a more specific submaterial
                m2 = m.created_from.get_or_none()
                if m2 is not None:
                    m = m2

                a.on_material.connect(m)
                m.used_in_analyses.connect(a)

        num_analyses = len(Analysis.nodes)
        log.info(f'Created {num_analyses} Analyses')

    @db.transaction
    def create_fusions_rnaseq(self):
        log.info('Creating fusions RNASeq...')

        fake = Faker()

        # RNASeq fusions
        fusions = read_csv('fusions.csv')
        for _, row in fusions.iterrows():
            f = Fusion(name=row['fusion_gene'])
            f.save()

        # Relate analyses to fusions
        for a in RNASeqAnalysis.nodes:

            # Add 0-2 fusions
            samples = fusions.sample(n=random.randint(0,2))
            for _, s in samples.iterrows():
                f = Fusion.get_or_create({'name':s['fusion_gene']})[0]
                a.showed_fusions.connect(f, {'text': fake.pystr()})
        num_fusions = len(Fusion.nodes)
        log.info(f'Created {num_fusions} Fusions (RNASeq)')

    @db.transaction
    def create_fusions_array_cgh(self):
        log.info('Creating fusions Array CGH...')

        fake = Faker()

        # CGH Array fusions
        f = Fusion.nodes.get(name='P2RY8-CRLF2')
        log.info(f'Created {0} new Fusions (Array CGH)')

        # Hypo-/Hyperdiploidy & Normal (Aneuploidy)
        hypo = Aneuploidy(name='Hypodiploidy')
        hypo.save()
        hyper = Aneuploidy(name='Hyperdiploidy')
        hyper.save()

        # Relate analyses to fusions and hypo/hyperdiploidy
        num_analyses = int(len(ArrayCGHAnalysis.nodes) / 3)
        samples = random.sample(ArrayCGHAnalysis.nodes.all(), num_analyses)
        for a in samples:
            a.showed_fusions.connect(f, {'text': fake.pystr()})

            # Update analysis with chromosomes
            chromosomes = random.choice(['<44 Chr.', '<45 Chr.', '>50 Chr.', '45-50 Chr.', '46,XX', '46,XY'])
            a.chromosomes = chromosomes
            a.save()

            # Assign hypo-/hyperdiploidy relation
            if chromosomes in ['<44 Chr.', '<45 Chr.']:
                a.has_aneuploidy.connect(hypo)
            elif chromosomes in ['>50 Chr.']:
                a.has_aneuploidy.connect(hyper)
            

    @db.transaction
    def merge_fusions(self):
        """Merge fusions nodes with different names that refer to+
        the same mutation, e.g. "CRLF2-P2RY8" and "P2RY8-CRLF2".
        """
        log.info("Merging fusion nodes...")

        # Prepare queries
        queries = [
            read_resource('cypher/delete_wrong_fusions.cypher'),
            read_resource('cypher/merge_double_single_dash_1.cypher'),
            read_resource('cypher/merge_double_single_dash_2.cypher'),
            read_resource('cypher/merge_gene_name_inverted.cypher'),
            read_resource('cypher/merge_bcr_abl.cypher'),
            read_resource('cypher/merge_crlf2_p2ry8.cypher'),
            read_resource('cypher/merge_etv6_runx1.cypher'),
            read_resource('cypher/merge_tcf3_pbx1.cypher'),
            read_resource('cypher/merge_kmt2a_group.cypher'),
            read_resource('cypher/merge_pax5_group.cypher'),
            read_resource('cypher/merge_znf384_group.cypher'),
            read_resource('cypher/merge_mef2d_group.cypher'),
        ]

        for q in queries:
            # log.info(f'Running query: {q}')

            results, meta = db.cypher_query(q)
            # log.debug(f'Executed query: {results}, {meta}')

    @db.transaction
    def create_results(self):
        log.info('Creating result nodes ...')

        fake = Faker()

        # Link each analysis to one result
        for a in Analysis.nodes:
            r = Result(name=fake.pystr())
            r.save()

            a.has_results.connect(r, {
                'result_id': f'{a.analysis_id}#Res',
                'description': fake.pystr(),
                'value': fake.pystr(),
            })

        # Output number of result nodes
        num_results = len(Result.nodes)
        log.info(f'Created {num_results} Results')


    @db.transaction
    def add_dashboard(self):
        log.info('Adding dashboard ...')

        # Load json
        res = read_resource('dashboard.json')
        dashboard_json = json.loads(res)

        # Query random patient id
        patient_id = Patient.nodes[0].patient_id
        dashboard_json['settings']['parameters']['neodash_patient_patient_id'] = patient_id

        # Create node
        d = _Neodash_Dashboard(title='ALL Dashboard',
                               date=datetime.now(),
                               user='neo4j',
                               version='2.0',
                               content=dashboard_json)
        d.save()
        log.info('Added neodash dashboard node')
