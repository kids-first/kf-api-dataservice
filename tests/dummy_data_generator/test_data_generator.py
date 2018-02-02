from datetime import datetime
from dateutil import relativedelta
import uuid
import random
import csv

from dataservice.extensions import db
from dataservice import create_app
from sqlalchemy.exc import IntegrityError

from dataservice.api.participant.models import Participant
from dataservice.api.demographic.models import Demographic
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.genomic_file.models import GenomicFile
from tests.utils import FlaskTestCase


class DataGenerator(FlaskTestCase):

    def setUp(self):
        self.app = create_app("generate")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()
        self.app_context.pop()

    def _create_participant(self, total=2):
        for i in range(total):
            p = Participant(external_id='participant_{}'.format(i),
                            samples=self._create_samples(),
                            demographic=self._create_demographics(),
                            diagnoses=self._create_diagnoses())
            db.session.add(p)
        db.session.commit()

    def _create_samples(self, total=2):
        """
        Create samples with aliquots
        """
        # fields choices
        tissue_type_list = [
            'Tumor',
            'Normal',
            'Abnormal',
            'Peritumoral',
            'Unknown',
            'Not Reported']
        ref_file = open('tests/dummy_data_generator/composition.txt', 'r')
        reader = csv.reader(ref_file)
        composition_list = []
        for line in reader:
            composition_list.append(line[0])
        tumor_descriptor_list = [
            'Metastatic',
            'Primary',
            'Recurrence',
            'Xenograft',
            'NOS',
            'Unknown',
            'Not Reported']
        s_list = []
        for i in range(total):
            sample_data = {
                'external_id': 'sample_{}'.format(i),
                'tissue_type': random.choice(tissue_type_list),
                'composition': random.choice(composition_list),
                'anatomical_site': 'Brain',
                'age_at_event_days': 456,
                'tumor_descriptor': random.choice(tumor_descriptor_list)
            }
            s_list.append(Sample(**sample_data,
                                 aliquots=self._create_aliquots()))
        return s_list

    def _create_aliquots(self, total=2):
        """
        Create aliquots with sequencing experiments
        """
        dt = datetime.now()
        analyte_type_list = ['DNA', 'EBV Immortalized Normal',
                             'FFPE DNA',
                             'FFPE RNA',
                             'GenomePlex (Rubicon) Amplified DNA',
                             'Repli-G (Qiagen) DNA',
                             'Repli-G Pooled (Qiagen) DNA',
                             'Repli-G X (Qiagen) DNA',
                             'RNA',
                             'Total RNA']

        shipment_destination_list = [
            'Baylor College of Medicine',
            'Washington University',
            'HudsonAlpha',
            'Broad Institute']

        a_list = []
        for i in range(total):
            aliquot_data = {
                'external_id': 'aliquot_{}'.format(i),
                'shipment_origin': 'CORIELL',
                'shipment_destination': random.choice(shipment_destination_list),
                'analyte_type': random.choice(analyte_type_list),
                'concentration': random.randint(70,400),
                'volume': (random.randint(200,400)) / 10,
                'shipment_date': dt - relativedelta.relativedelta(
                    years=random.randint(1,2)) - relativedelta.relativedelta(
                    months=random.randint(1,12)) + 
                    relativedelta.relativedelta(days=random.randint(1,30))
                    }
            a_list.append(
                Aliquot(
                    **aliquot_data,
                    sequencing_experiments=self._create_experiments()))
        return a_list

    def _create_experiments(self, total=2):
        """
        Create sequencing experiments
        """
        ref_file = open('tests/dummy_data_generator/instrument_model.txt', 'r')
        reader = csv.reader(ref_file)
        instrument_model_list = []
        for line in reader:
            instrument_model_list.append(line[0])
        
        is_paired_end_list=[True,False]
        library_strand_list=['Unstranded',
                            'First_Stranded',
                            'Second_Stranded']
        experiment_strategy_list=['WGS',
                            'WXS',
                            'RNA-Seq',
                            'ChIP-Seq',
                            'miRNA-Seq',
                            'Bisulfite-Seq',
                            'Validation',
                            'Amplicon',
                            'Targeted Sequencing',
                            'Other']
        platform_list=['Illumina',
                        'SOLiD',
                        'LS454',
                        'Ion Torrent',
                        'Complete Genomics',
                        'PacBio',
                        'Other'
                            ]
        e_list = []
        dt = datetime.now()
        for i in range(total):

            e_data = {
                'external_id': 'sequencing_experiment_{}'.format(i),
                'experiment_date': dt - relativedelta.relativedelta(
                    years=random.randint(1,3)) + relativedelta.relativedelta(
                    months=random.randint(1,6)) + 
                    relativedelta.relativedelta(days=random.randint(1,30)),
                'experiment_strategy': random.choice(experiment_strategy_list),
                'center': 'Broad Institute',
                'library_name': 'Test_library_name_0',
                'library_strand': random.choice(library_strand_list),
                'is_paired_end': random.choice(is_paired_end_list),
                'platform': random.choice(platform_list),
                'instrument_model': random.choice(instrument_model_list),
                'max_insert_size': random.choice([300, 350, 500]),
                'mean_insert_size': random.randint(300,500),
                'mean_depth': random.randint(40,60),
                'total_reads': random.randint(400,1000),
                'mean_read_length': random.randint(400,1000)
            }
            e_list.append(
                SequencingExperiment(
                    **e_data,
                    genomic_files=self._create_genomic_files()))
        return e_list

    def _create_genomic_files(self, total=4):
        file_format_list = ['.cram', '.bam', '.vcf']
        gf_list = []
        for i in range(total):
            kwargs = {
                'file_name': 'file_{}'.format(i),
                'file_type': 'submitted aligned read',
                'file_format': random.choice(file_format_list),
                'file_url': 's3://file_{}'.format(i),
                'md5sum': str(uuid.uuid4()),
            }
            gf_list.append(GenomicFile(**kwargs))
        return gf_list

    def _create_demographics(self):
        race_list = [
            "White",
            "Black or African American",
            "Asian",
            "Native Hawaiian or Other Pacific Islander",
            "American Indian or Alaska Native",
            "Other",
            "Unavailable",
            "Not Reported",
            "not allowed to collect"]
        ethnicity_list = ["hispanic or latino",
                          "not hispanic or latino",
                          "Unknown",
                          "not reported",
                          "not allowed to collect"]
        gender_list = ['female',
                       'male',
                       'unknown',
                       'unspecified'
                       'not reported']
        data = {
            'external_id': 'demo_id',
            'race': random.choice(race_list),
            'ethnicity': random.choice(ethnicity_list),
            'gender': random.choice(gender_list)
        }
        return Demographic(**data)

    def _create_diagnoses(self, total=4):
        ref_file = open('tests/dummy_data_generator/diagnoses.txt', 'r')
        reader = csv.reader(ref_file)
        diagnosis_list = []
        for line in reader:
            diagnosis_list.append(line[0])
        progression_or_recurrence_list = ['yes', 'no', 'unknown']
        diag_list = []
        for i in range(total):

            data = {
                'external_id': 'diagnosis_{}'.format(i),
                'diagnosis': random.choice(diagnosis_list),
                'progression_or_recurrence': 
                    random.choice(progression_or_recurrence_list),
                'age_at_event_days': random.randint(0,32872)
                }
            diag_list.append(Diagnosis(**data))
        return diag_list

    def test_create_and(self):
        self._create_participant(total=4)
        p = Participant.query.all()
        self.assertEqual(Participant.query.count(), 4)
