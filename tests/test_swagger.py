import pytest

import dataservice


class TestSwagger:
    """
    Tests the swagger spec
    """

    @pytest.mark.parametrize('path', [
        'definitions.Participant',
        'definitions.Diagnosis',
        'definitions.DiagnosisPaginated',
        'definitions.DiagnosisResponse',
        'definitions.ParticipantResponse',
    ])
    def test_field_exists(self, swagger, path):
        """ Test swagger spec fields """

        def check_field(p, d):
            assert p[0] in d
            if len(p) > 1:
                check_field(p[1:], d[p[0]])

        check_field(path.split('.'), swagger)

    @pytest.mark.parametrize('endpoint', [
        '/diagnoses',
        '/biospecimens',
        '/participants',
    ])
    @pytest.mark.parametrize('method', [
        'get',
        'post',
    ])
    def test_path_exists(self, swagger, endpoint, method):
        """ Test swagger spec fields """
        path = '.'.join(['paths', endpoint, method])

        self.test_field_exists(swagger, path)

    @pytest.mark.parametrize('path,value', [
        ('info.title', 'Kids First Data Service'),
        ('paths./participants/{kf_id}.get.description',
         'Get Participant by id'),
        ('paths./diagnoses/{kf_id}.get.description', 'Get Diagnosis by id'),
        ('paths./biospecimens/{kf_id}.get.description',
         'Get Biospecimen by id'),
    ])
    def test_field_equals(self, swagger, path, value):
        """ Test swagger spec field values """

        def check_field(p, d):
            assert p[0] in d
            if len(p) == 1:
                assert d[p[0]] == value
                return
            check_field(p[1:], d[p[0]])

        check_field(path.split('.'), swagger)
