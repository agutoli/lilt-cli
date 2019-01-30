import os
import json
import time
import datetime
import requests
import xml.etree.ElementTree as ET

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

lilt_api_url = "https://lilt.com/2"

def get_project(project_id):
    payload = {"key": os.environ["LILT_API_KEY"], "id": project_id}
    res = requests.get(lilt_api_url + "/projects", params=payload, verify=False)
    return res.json()[0]

def get_document_by_name(name, project_id):
    project = get_project(project_id)
    document = None
    for doc in project["document"]:
        if name == doc['name']:
            print('Updating document "%s"' % name)
            document = doc
            break
    return document

def create_segment(document_id, term):
    payload = { "key": os.environ["LILT_API_KEY"] }
    body = { "document_id": document_id, "source": term, "target": term }
    headers = { "Content-Type": "application/json" }
    res = requests.post(lilt_api_url + "/segments", params=payload, data=json.dumps(body), headers=headers)
    return res.json()

def create_document(project_id, name):
    payload = { "key": os.environ["LILT_API_KEY"]}
    data = { "name": name, "project_id": project_id }
    headers = { "Content-Type": "application/json" }
    res = requests.post(lilt_api_url + "/documents", params=payload, data=json.dumps(data), headers=headers)
    return res.json()

def get_segments(document_id, is_confirmed, is_reviewed):
    payload = { "key": os.environ["LILT_API_KEY"], "id": document_id }
    res = requests.get(lilt_api_url + "/documents?with_segments=true", params=payload, verify=False)
    segments = res.json()['segments']

    has_filter = is_confirmed != None or is_reviewed != None

    if not has_filter:
        return segments

    filtered_segments = []
    for segment in segments:
        if is_confirmed != None and segment['is_confirmed'] == is_confirmed:
            filtered_segments.append(segment)
        elif is_reviewed != None and segment['is_reviewed'] == is_reviewed:
            filtered_segments.append(segment)
    return filtered_segments

def upload_segments(filename, project_id):
    document = get_document_by_name(filename, project_id)

    if not document:
        print('Creating document "%s"' % filename)
        document = create_document(project_id, filename)

    segments = get_segments(document['id'], None, None)

    sources = []
    for segment in segments:
        sources.append(segment['source'])

    with open(filename, 'r') as fp:
        rawdata = fp.read()

    file_segments = json.loads(rawdata)
    for segment in file_segments:
        if not (segment in sources):
            create_segment(document['id'], segment)
    return

def download_document(filename, project_id, is_confirmed, is_reviewed):
    document = get_document_by_name(filename, project_id)
    if not document:
        return None
    segments = get_segments(document['id'], is_confirmed, is_reviewed)
    return json.dumps(segments, indent=2, sort_keys=True)
