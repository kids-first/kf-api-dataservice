import copy
import json
import re

import pytest

from tests.conftest import (ENDPOINT_ENTITY_MAP, ENTITY_PARAMS,
                            _add_foreign_keys)

CONSTRAINT_ERR_RE = re.compile(
    'could not create (\w+)\. one with \(.+\) = \(.+\) already exists\.'
)


class TestErrors:
    """ Test general error handling """

    @pytest.mark.parametrize('endpoint', ['/diagnoses', '/outcomes'
                                          ])
    @pytest.mark.parametrize('kf_id', [
        '', 'AABB1122', 'blah', 'blah blah'
    ])
    def test_fk_not_exists(self, client, endpoint, kf_id):
        """ Test integrity errors where the foreign key does not exist """
        # Create participant
        kwargs = {
            'participant_id': kf_id
        }
        # Send post request
        response = client.post(endpoint,
                               data=json.dumps(kwargs),
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 400

        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        if len(kf_id) <= 11:
            message = '"{}" does not exist'.format(kwargs['participant_id'])
            assert message in response['_status']['message']
        else:
            message = 'Longer than maximum length 11'
            assert message in response['_status']['message']

    @pytest.mark.parametrize('endpoint', [
        '/sequencing-centers',
        '/biospecimen-genomic-files',
        '/biospecimen-diagnoses',
        '/family-relationships',
        '/cavatica-task-genomic-files',
        '/read-group-genomic-files'
    ])
    def test_uniqueness_constraints(self, client, entities, endpoint):
        """ Test integrity error from uniqueness violations """
        # _add_foreign_keys is destructive to ENTITY_PARAMS['fields'][endpoint]
        # state used by other tests, so deepcopy it here to prevent side
        # effects.
        inputs = ENTITY_PARAMS['fields'][endpoint].copy()
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]
        _add_foreign_keys(inputs, entity)
        response = client.post(
            endpoint, data=json.dumps(inputs),
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 400
        response = json.loads(response.data.decode("utf-8"))
        assert CONSTRAINT_ERR_RE.match(response['_status']['message'])
