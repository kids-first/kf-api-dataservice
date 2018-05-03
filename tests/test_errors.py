import json
import pytest


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
