import json
import pytest


class TestErrors:
    """ Test general error handling """

    @pytest.mark.parametrize('endpoint', [
        '/demographics', '/diagnoses', '/samples'
    ])
    @pytest.mark.parametrize('kf_id', [
        '', 'AABB1122', 'blah', 'blah blah'
    ])
    def test_fk_not_exists(self, client, endpoint, kf_id):
        """ Test integrity errors where the foreign key does not exist """
        # Create demographic data
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
        if len(kf_id) <= 8:
            message = '"{}" does not exist'.format(kwargs['participant_id'])
            assert message in response['_status']['message']
        else:
            message = 'Longer than maximum length 8'
            assert message in response['_status']['message']

    def test_unique_demographic(self, client, entities):
        """ Test integrity errors trying to break one-one with many-many """
        inputs = entities['/participants']
        inputs.update({'external_id': 'test'})

        # Create participant
        response = client.post('/participants',
                               data=json.dumps(inputs),
                               headers={'Content-Type': 'application/json'})

        response = json.loads(response.data.decode("utf-8"))
        kf_id = response['results']['kf_id']

        kwargs = {'participant_id': kf_id}
        # Send post request
        response = client.post('/demographics',
                               data=json.dumps(kwargs),
                               headers={'Content-Type': 'application/json'})
        # Try to create another demographic on the same participant
        response = client.post('/demographics',
                               data=json.dumps(kwargs),
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 400

        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        message = '{} "{}" may only have one {}'.format('participant',
                                                        kf_id, 'demographic')
        assert message in response['_status']['message']
