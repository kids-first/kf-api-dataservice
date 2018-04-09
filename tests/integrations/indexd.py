"""
Quick end-to-end integration test of indexd and the dataservice
Must have indexd running at $INDEXD_URL
Must provide $INDEXD_USER and $INDEXD_PASS
Must have dataservice running at $DATASERVICE_URL
"""

import os
import requests
from collections import OrderedDict

ds_api = os.environ['DATASERVICE_URL']
indexd_api = os.environ['INDEXD_URL']
auth = (os.environ['INDEXD_USER'], os.environ['INDEXD_PASS'])

data = OrderedDict()
data['/studies'] = { "external_id": "test" }
data['/participants'] = {
    "external_id": "test",
    "study_id": "</studies>",
    "is_proband": True
}
data['/samples'] = { "participant_id": "</participants>" }
data['/aliquots'] = {
    "analyte_type": "string",
    "sample_id": "</samples>",
}
data['/sequencing-experiments'] = {
    "external_id": "BLAH",
    "experiment_strategy": "WGS",
    "aliquot_id": "</aliquots>",
    "center": "baylor",
    "instrument_model": "Hi-Seq",
    "is_paired_end": True,
    "platform": "Illumina",
}
data['/genomic-files'] = {
    "controlled_access": True,
    "data_type": "aligned reads",
    "file_format": "bam",
    "file_name": "hg38.bam",
    "hashes": {"md5": "5dbc559537514d309b36064501b7d0e8"},
    "is_harmonized": True,
    "latest_did": "string",
    "metadata": {"acl": "cbttc"},
    "sequencing_experiment_id": "</sequencing-experiments>",
    "reference_genome": "hg38",
    "size": 10,
    "urls": ["s3://mybucket/key"]
}


for endpoint, body in data.items():
    for k, v in body.items():
        if isinstance(v, str) and v[0] == "<" and v[-1] == ">":
            fk = v[1:-1]
            data[endpoint][k] = data[fk]['kf_id']

    resp = requests.post(ds_api+endpoint, json=body)
    data[endpoint]['kf_id'] = resp.json()['results']['kf_id']


# Get the genomic file by kf_id
kf_id = data['/genomic-files']['kf_id']
resp = requests.get(ds_api+'/genomic-files/'+kf_id)
latest_did = resp.json()['results']['latest_did']
v1_did = latest_did
gf = resp.json()['results']

# Check fields against indexd
resp = requests.get(indexd_api+latest_did)
doc = resp.json()

keys = ['file_name',  'size', 'urls', 'metadata']
for k in keys:
    assert gf[k] == doc[k]


# Check that we can update the genomic_file
gf = { 
    "controlled_access": True,
    "data_type": "aligned reads",
    "file_name": "hg37.bam",
    "hashes": {"md5": "5dbc559537514d309b36064501b7d0a9"},
    "metadata": {"acl": "cbttc,admin"},
    "reference_genome": "hg37",
    "size": 1000,
    "urls": ["s3://new/key"]
}
resp = requests.patch(ds_api+'/genomic-files/'+kf_id, json=gf)
assert latest_did != resp.json()['results']['latest_did']
latest_did = resp.json()['results']['latest_did']
v2_did = latest_did


# Check new fields
resp = requests.get(indexd_api+latest_did)
doc = resp.json()

for k in keys:
    assert gf[k] == doc[k]

# Check that baseid is the same
baseid1 = requests.get(indexd_api+v1_did).json()['baseid']
baseid2 = requests.get(indexd_api+v2_did).json()['baseid']
assert baseid1 == baseid2

# Try deleting
# delete from indexd first
rev = requests.get(indexd_api+v2_did).json()['rev']
resp = requests.delete(indexd_api+v2_did+'?rev='+rev, auth=auth)
resp = requests.get(indexd_api+v2_did)
assert resp.status_code == 404
resp = requests.get(ds_api+'/genomic-files/'+kf_id)
assert resp.status_code == 404
