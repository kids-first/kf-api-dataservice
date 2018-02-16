from datetime import datetime
from dateutil import relativedelta
import uuid
import random
import csv
import os

from dataservice import create_app
from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.demographic.models import Demographic
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.outcome.models import Outcome
from dataservice.api.workflow.models import (
    Workflow,
    WorkflowGenomicFile
)
from dataservice.api.phenotype.models import Phenotype


class DataGenerator(object):
    def __init__(self, config_name=None):
        if not config_name:
            config_name = os.environ.get('FLASK_CONFIG', 'default')
        self.setup(config_name)
        self.max_participants = 50
        self._sample_choices()
        self._aliquot_choices()
        self._experiment_choices()
        self._demographics_choices()
        self._diagnoses_choices()
        self._genomic_files_choices()
        self._outcomes_choices()
        self._phenotype_choices()

    def _sample_choices(self):
        """
        Provides the choices for filling sample entity
        """
        self.min_samples = 0
        self.max_samples = 5
        self.tissue_type_list = ['Tumor', 'Normal', 'Abnormal', 'Peritumoral',
                                 'Unknown', 'Not Reported']
        sref_file = open('dataservice/util/data_gen/composition.txt', 'r')
        reader = csv.reader(sref_file)
        self.composition_list = []
        for line in reader:
            self.composition_list.append(line[0])
        self.tumor_descriptor_list = [
            'Metastatic',
            'Primary',
            'Recurrence',
            'Xenograft',
            'NOS',
            'Unknown',
            'Not Reported']
        asref_file = open('dataservice/util/data_gen/anatomical_site.txt', 'r')
        reader = csv.reader(asref_file)
        self.anatomical_site_list = []
        for line in reader:
            self.anatomical_site_list.append(line[0])

    def _aliquot_choices(self):
        """
        Provides the choices for filling aliquot entity
        """
        self.min_aliquots = 0
        self.max_aliquots = 5
        at_file = open('dataservice/util/data_gen/analyte_type.txt', 'r')
        reader = csv.reader(at_file)
        self.analyte_type_list = []
        for line in reader:
            self.analyte_type_list.append(line[0])

        self.shipment_destination_list = [
            'Baylor College of Medicine',
            'Washington University',
            'HudsonAlpha',
            'Broad Institute']
        self.shipment_origin_list = ['CORIELL']

    def _experiment_choices(self):
        """
        Provides the choices for filling Sequencing Experiment entity
        """
        self.min_seq_exps = 0
        self.max_seq_exps = 3
        aref_file = open('dataservice/util/data_gen/instrument_model.txt', 'r')
        reader = csv.reader(aref_file)
        self.instrument_model_list = []
        for line in reader:
            self.instrument_model_list.append(line[0])

        self.is_paired_end_list = [True, False]
        self.library_strand_list = ['Unstranded', 'First_Stranded',
                                    'Second_Stranded']
        self.experiment_strategy_list = [
            'WGS',
            'WXS',
            'RNA-Seq',
            'ChIP-Seq',
            'miRNA-Seq',
            'Bisulfite-Seq',
            'Validation',
            'Amplicon',
            'Targeted Sequencing',
            'Other']
        self.platform_list = ['Illumina', 'SOLiD', 'LS454', 'Ion Torrent',
                              'Complete Genomics', 'PacBio', 'Other']

    def _demographics_choices(self):
        """
        Provides the choices for filling Demographics entity
        """
        self.race_list = [
            "White",
            "Black or African American",
            "Asian",
            "Native Hawaiian or Other Pacific Islander",
            "American Indian or Alaska Native",
            "Other",
            "Unavailable",
            "Not Reported",
            "not allowed to collect"]
        self.ethnicity_list = [
            "hispanic or latino",
            "not hispanic or latino",
            "Unknown",
            "not reported",
            "not allowed to collect"]
        self.gender_list = ['female', 'male', 'unknown', 'unspecified',
                            'not reported']

    def _diagnoses_choices(self):
        """
        Provides the choices for filling Diagnosis entity
        """
        self.max_diagnoses = 10
        self.min_diagnoses = 0
        dref_file = open('dataservice/util/data_gen/diagnoses.txt', 'r')
        reader = csv.reader(dref_file)
        self.diagnosis_list = []
        for line in reader:
            self.diagnosis_list.append(line[0])

    def _genomic_files_choices(self):
        """
        Provides the choices for filling Genomic File entity
        """
        self.min_gen_files = 0
        self.max_gen_files = 5
        self.file_format_list = ['.cram', '.bam', '.vcf']
        self.controlled_access_list = [True, False]
        self.data_type_list = []
        fref_file = open('dataservice/util/data_gen/data_type.txt', 'r')
        reader = csv.reader(fref_file)
        for line in reader:
            self.data_type_list.append(line[0])

    def _phenotype_choices(self):
        """
        Provides Choices for filling Phenotypes
        """
        self.min_phenotypes = 0
        self.max_phenotypes = 8
        pref_file = open('dataservice/util/data_gen/phenotype_hpo.csv', 'r')
        reader = csv.reader(pref_file)
        self.phenotype_chosen_list = []
        for row in reader:
            self.phenotype_chosen_list.append(row)
        self.observed_list = ['negative', 'positive']

    def _outcomes_choices(self):
        """
        Provides the Choices for filling Outcome Entity
        """
        self.min_outcomes = 0
        self.max_outcomes = 5
        self.vital_status_list = ['Alive', 'Dead', 'Not Reported']
        self.disease_related_list = [True, False, 'Not Reported']

    def setup(self, config_name):
        """
        Creates tables in database
        """
        self.app = create_app(config_name)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def teardown(self):
        db.session.remove()
        self.app_context.pop()

    def drop_all(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_and_publish_all(self):
        """
        Create and save all objects to db
        """
        # Create participants
        self._create_participants_and_studies(self.max_participants)
        # Create workflows
        workflows = self._create_workflows(2)
        # Link workflows and genomic files
        self._link_genomic_files_to_workflows(workflows)
        # Tear down
        self.teardown()

    def _create_studies(self, total=None):
        """
        Create study
        """
        # Create studies
        study_names = ['Structural Birth Defect Study', 'Brain Cancer Study',
                       'Breast Cancer Study']
        min_studies = 1
        max_studies = len(study_names)
        if not total:
            total = random.randint(min_studies, max_studies)

        studies = []
        for i in range(total):
            kwargs = {
                'attribution': ('https://dbgap.ncbi.nlm.nih.gov/'
                                'aa/wga.cgi?view_pdf&stacc=phs000178.v9.p8'),
                'external_id': 'phs00{}'.format(i),
                'name': random.choice(study_names),
                'version': 'v1'
            }
            s = Study(**kwargs)
            studies.append(s)
            db.session.add(s)
        db.session.commit()

        return studies

    def _create_participants_and_studies(self, total):
        """
        Creates studies and participants with samples, demographics,
        and diagnoses
        """
        # Studies
        studies = self._create_studies()

        # Participants
        for i in range(total):
            samples = self._create_samples(random.randint(self.min_samples,
                                                          self.max_samples))
            demographic = self._create_demographics(i)
            diagnoses = self._create_diagnoses(
                random.randint(self.min_samples, self.max_diagnoses))
            outcomes = self._create_outcomes(random.randint(self.min_outcomes,
                                                            self.max_outcomes))
            phenotypes = self._create_phenotypes(
                random.randint(self.min_phenotypes, self.max_phenotypes))
            p = Participant(
                external_id='participant_{}'.format(i),
                samples=samples,
                demographic=demographic,
                diagnoses=diagnoses,
                outcomes=outcomes,
                phenotypes=phenotypes,
                study_id=random.choice(studies).kf_id)
            db.session.add(p)
        db.session.commit()

    def _create_samples(self, total):
        """
        Create samples with aliquots
        """

        s_list = []
        for i in range(total):
            sample_data = {
                'external_id': 'sample_{}'.format(i),
                'tissue_type': random.choice(self.tissue_type_list),
                'composition': random.choice(self.composition_list),
                'anatomical_site': random.choice(self.anatomical_site_list),
                'age_at_event_days': random.randint(0, 32872),
                'tumor_descriptor': random.choice(self.tumor_descriptor_list)
            }
            aliquots = self._create_aliquots(random.randint(self.min_aliquots,
                                                            self.max_aliquots))
            s_list.append(Sample(**sample_data, aliquots=aliquots))
        return s_list

    def _create_aliquots(self, total):
        """
        Creates aliquots with sequencing experiments
        """
        dt = datetime.now()
        a_list = []
        for i in range(total):
            aliquot_data = {
                'external_id': 'aliquot_{}'.format(i),
                'shipment_origin': random.choice(self.shipment_origin_list),
                'shipment_destination':
                    random.choice(self.shipment_destination_list),
                'analyte_type': random.choice(self.analyte_type_list),
                'concentration': random.randint(70, 400),
                'volume': (random.randint(200, 400)) / 10,
                'shipment_date': dt - relativedelta.relativedelta(
                    years=random.randint(1, 2)) - relativedelta.relativedelta(
                    months=random.randint(1, 12)) +
                relativedelta.relativedelta(days=random.randint(1, 30))
            }
            sequencing_experiments = self._create_experiments(
                random.randint(self.min_seq_exps, self.max_seq_exps))
            a_list.append(Aliquot(
                **aliquot_data,
                sequencing_experiments=sequencing_experiments))
        return a_list

    def _create_experiments(self, total):
        """
        Creates sequencing experiments
        """

        e_list = []
        dt = datetime.now()
        for i in range(total):

            e_data = {
                'external_id': 'sequencing_experiment_{}'.format(i),
                'experiment_date': dt - relativedelta.relativedelta(
                    years=random.randint(1, 3)) + relativedelta.relativedelta(
                    months=random.randint(1, 6)) +
                relativedelta.relativedelta(days=random.randint(1, 30)),
                'experiment_strategy':
                random.choice(self.experiment_strategy_list),
                'center': 'Broad Institute',
                'library_name': 'Test_library_name_{}'.format(i),
                'library_strand': random.choice(self.library_strand_list),
                'is_paired_end': random.choice(self.is_paired_end_list),
                'platform': random.choice(self.platform_list),
                'instrument_model': random.choice(self.instrument_model_list),
                'max_insert_size': random.choice([300, 350, 500]),
                'mean_insert_size': random.randint(300, 500),
                'mean_depth': random.randint(40, 60),
                'total_reads': random.randint(400, 1000),
                'mean_read_length': random.randint(400, 1000)
            }
            genomic_files = self._create_genomic_files(
                random.randint(self.min_gen_files,
                               self.max_gen_files))
            e_list.append(SequencingExperiment(**e_data,
                                               genomic_files=genomic_files))
        return e_list

    def _create_genomic_files(self, total):
        """
        Creates genomic files
        """
        gf_list = []
        for i in range(total):
            kwargs = {
                'file_name': 'file_{}'.format(i),
                'data_type': random.choice(self.data_type_list),
                'file_format': random.choice(
                    self.file_format_list),
                'file_url': 's3://file_{}'.format(i),
                'controlled_access': random.choice(
                    self.controlled_access_list),
                'md5sum': str(
                    uuid.uuid4()),
            }
            gf_list.append(GenomicFile(**kwargs))
        return gf_list

    def _create_workflows(self, total=None):
        """
        Create workflows
        """
        min_workflows = 1
        max_workflows = 5
        if not total:
            total = random.randint(min_workflows, max_workflows)
        wf_list = []
        for i in range(total):
            data = {
                'task_id': 'task_{}'.format(i),
                'name': 'kf_alignment_{}'.format(i),
                'version': 'v1',
                'github_commit_url': (
                    'https://github.com/kids-first/'
                    'kf-alignment-workflow/commit/'
                    '0d7f93dff6463446b0ed43dc2883f60c28e6f1f4')
            }
            wf = Workflow(**data)
            db.session.add(wf)
            wf_list.append(wf)
        db.session.commit()

        return wf_list

    def _link_genomic_files_to_workflows(self, workflows):
        """
        Link all genomic files to at least 1 workflow
        """
        for gf in GenomicFile.query.all():
            is_input = not (gf.data_type.startswith('aligned'))
            n_workflows = random.randint(1, len(workflows))
            for i in range(n_workflows):
                wgf = WorkflowGenomicFile(workflow_id=workflows[i].kf_id,
                                          genomic_file_id=gf.kf_id,
                                          is_input=is_input)
                db.session.add(wgf)
        db.session.commit()

    def _create_demographics(self, i):
        """
        Create demographics
        """
        data = {
            'external_id': 'demo_id_{}'.format(i),
            'race': random.choice(self.race_list),
            'ethnicity': random.choice(self.ethnicity_list),
            'gender': random.choice(self.gender_list)
        }
        return Demographic(**data)

    def _create_diagnoses(self, total):
        """
        Creates diagnoses
        """
        diag_list = []
        for i in range(total):

            data = {
                'external_id': 'diagnosis_{}'.format(i),
                'diagnosis': random.choice(self.diagnosis_list),
                'age_at_event_days': random.randint(0, 32872)
            }
            diag_list.append(Diagnosis(**data))
        return diag_list

    def _create_outcomes(self, total):
        """
        creates outcomes
        """
        outcomes_list = []
        for i in range(total):
            # Fill disaese_related only if person is dead
            vs = random.choice(self.vital_status_list)
            if vs == 'Dead':
                dr = random.choice(self.disease_related_list)
                data = {
                    'vital_status': vs,
                    'disease_related': dr,
                    'age_at_event_days': random.randint(0, 32872)
                }
                outcomes_list.append(Outcome(**data))
                break
            else:
                data = {
                    'vital_status': vs,
                    'age_at_event_days': random.randint(0, 32872)
                }
                outcomes_list.append(Outcome(**data))
        return outcomes_list

    def _create_phenotypes(self, total):
        """
        Create phenotypes
        """
        phen_list = []
        for i in range(total):
            ph = random.choice(self.phenotype_chosen_list)
            phen = {
                'phenotype': ph[0],
                'hpo_id': ph[1],
                'observed': random.choice(self.observed_list),
                'age_at_event_days': random.randint(0, 32872)
            }
            phen_list.append(Phenotype(**phen))
        return phen_list
