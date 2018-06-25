import json
import pkg_resources
import pytest

from dataservice.api.common import id_service


class TestEvents:
    """
    Test that events are published to SNS with proper data
    """

    @pytest.mark.parametrize('endpoint,method', [
        ('/sequencing-experiments', 'GET'),
        ('/sequencing-centers', 'GET'),
        ('/biospecimens', 'GET'),
        ('/diagnoses', 'GET'),
        ('/phenotypes', 'GET'),
        ('/participants', 'GET'),
        ('/studies', 'GET'),
        ('/study-files', 'GET'),
        ('/investigators', 'GET'),
        ('/outcomes', 'GET'),
        ('/families', 'GET'),
        ('/family-relationships', 'GET'),
        ('/genomic-files', 'GET')
    ])
    def test_no_message(self, app, client, mocker, endpoint,
                        method, sns_topic):
        """ Test that message is sent with right path """
        mock = mocker.patch('dataservice.api.common.views.boto3.client')
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint)
        assert mock().publish.call_count == 0

    @pytest.mark.parametrize('endpoint,method,data', [
        ('/studies', 'POST', {'external_id': 'blah'}),
    ])
    def test_message(self, app, client, mocker, endpoint, method,
                     data, sns_topic):
        """ Test that message is sent with right path """
        mock = mocker.patch('dataservice.api.common.views.boto3.client')

        call_func = getattr(client, method.lower())
        resp = call_func(endpoint,
                         data=json.dumps(data),
                         headers={'Content-Type': 'application/json'})

        assert mock().publish.call_count == 1

        api_status = json.loads(client.get('/status').data.decode('utf-8'))
        api_version = api_status['_status']['version']
        api_commit = api_status['_status']['commit']

        expected = {'default': json.dumps({
            'path': endpoint,
            'method': method.lower(),
            'api_version': api_version,
            'api_commit': api_commit,
            'data': json.loads(resp.data.decode('utf-8'))
        })}

        args = mock().publish.call_args_list[0]
        message = json.loads(args[1]['Message'])
        assert message == expected
        assert args[1]['MessageStructure'] == 'json'
        assert args[1]['TopicArn'] == 'arn:aws:sns:*:123456789012:my_topic'
