import os
import json
import time
import requests
import xml.etree.ElementTree as ET

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

lilt_api_url = "https://lilt.com/2"

def pretranslate_document(document_id):
    payload = {"key": os.environ["LILT_API_KEY"]}
    jsonData = { "id": document_id}
    headers = { "Content-Type": "application/json" }
    res = requests.post(lilt_api_url + "/documents/pretranslate", params=payload, data=json.dumps(jsonData), headers=headers, verify=False)
    return res.json()

def get_seguiments(docid, _type="source"):
    payload = {"key": os.environ["LILT_API_KEY"], "id": docid, "is_xliff": "true"}
    res = requests.get(lilt_api_url + "/documents/files", params=payload, verify=False)
    root = ET.fromstring(res.content)
    namespace = '{urn:oasis:names:tc:xliff:document:1.2}'
    seguiments = {}
    for child in root.findall(".//%strans-unit" % namespace):
        id = child.attrib['resname']
        try:
            section = child.find(".//%s%s" % (namespace, _type))
            seguiments[id] = section.text
        except:
            pass
    return seguiments

def get_all_documents(project_id):
    payload = {"key": os.environ["LILT_API_KEY"], "id": project_id}
    res = requests.get(lilt_api_url + "/projects", params=payload, verify=False)
    allproj = res.json()
    documents = []
    for proj in allproj:
        for doc in proj["document"]:
            documents.append(doc)
    return documents

def get_all_seguiments_by_project(project_id):
    payload = {"key": os.environ["LILT_API_KEY"], "id": project_id}
    res = requests.get(lilt_api_url + "/projects", params=payload, verify=False)
    allproj = res.json()
    all_seguiments = {}
    for proj in allproj:
        for doc in proj["document"]:
            seguiments = get_seguiments(doc["id"])
            for id in seguiments:
                all_seguiments[id] = seguiments[id]
    return all_seguiments

def get_all_translated_seguiments_by_project(project_id):
    payload = {"key": os.environ["LILT_API_KEY"], "id": project_id}
    res = requests.get(lilt_api_url + "/projects", params=payload, verify=False)
    allproj = res.json()
    all_seguiments = {}
    for proj in allproj:
        for doc in proj["document"]:
            seguiments = get_seguiments(doc["id"], _type="target")
            for id in seguiments:
                all_seguiments[id] = seguiments[id]
    return all_seguiments

def delete_document(docid):
    payload = {"key": os.environ["LILT_API_KEY"], "id": docid}
    res = requests.delete(lilt_api_url + "/documents", params=payload, verify=False)

def upload_document(filename, project_id):
    all_seguiments = get_all_seguiments_by_project(project_id)
    payload = {"key": os.environ["LILT_API_KEY"]}
    jsonData = {"name": filename, "project_id": project_id}
    headers = { "LILT-API": json.dumps(jsonData), "Content-Type": "application/octet-stream" }

    with open(filename, 'r') as fp:
        rawdata = fp.read()

    local_seguiments = json.loads(rawdata)

    for id in local_seguiments:
        all_seguiments[id] = local_seguiments[id]

    res = requests.post(lilt_api_url + "/documents/files", params=payload, data=json.dumps(all_seguiments), headers=headers, verify=False)
    document_id = res.json()["id"]

    time.sleep(2)

    pretranslate_document(document_id)

    return document_id

def download_document(filename, docid):
    payload = {"key": os.environ["LILT_API_KEY"], "id": docid, "is_xliff": "false"}
    res = requests.get(lilt_api_url + "/documents/files", params=payload, verify=False)
    seguiments = json.loads(res.content)
    for id in seguiments:
        all_seguiments[id] = seguiments[id]

    with open(filename, 'w') as outfile:
        json.dump(all_seguiments, outfile, indent=2, sort_keys=True)
