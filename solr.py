import json
import os
import pysolr
import requests
import pandas as pd

CORE_NAME = "IRF24P1"
# External static IP
VM_IP = "35.209.223.129"
    
    
class Indexer:
    def __init__(self):
        self.solr_url = f'http://{VM_IP}:8983/solr/'
        self.connection = pysolr.Solr(self.solr_url + CORE_NAME, always_commit=True, timeout=5000000)

    def delete_core(self, core=CORE_NAME):
        pass
        # self.connection.delete_core(core)
        # print(os.system('sudo su - solr -c "/opt/solr/bin/solr delete -c {core}"'.format(core=core)))


    def create_core(self, core=CORE_NAME):
        # print(os.system(
        #     'sudo su - solr -c "/opt/solr/bin/solr create -c {core} -n data_driven_schema_configs"'.format(
        #         core=core)))
        # self.connection.create_core(core)
        try:
            requests.post(self.solr_url + "admin/cores?action=CREATE&name=" + core)
        except:
            print("Error while creating core")

    def do_initial_setup(self):
        self.delete_core()
        self.create_core()

    def create_documents(self, docs):
        print(self.connection.add(docs))

    def query(self, query='q=title:"My Document"'):
        results = self.connection.search(query)
        print(results)
        for result in results:
            print(result)

    def add_fields(self):
        data = {
            "add-field": [
                {
                    "name": "revision_id",
                    "type": "string",
                    "indexed": True,
                    "multiValued": False
                },
                {
                    "name": "title",
                    "type": "string",
                    "indexed": True,
                    "multiValued": False
                },
                {
                    "name": "summary",
                    "type": "text_en",
                    "indexed": True,
                    "multiValued": False
                },
                {
                    "name": "url",
                    "type": "string",
                    "indexed": True,
                    "multiValued": False
                },
                {
                    "name": "topic",
                    "type": "string",
                    "indexed": True,
                    "multiValued": False,
                    "custom": True
                },
            ]
        }
        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())


data = None
with open("search_results.json", "r") as file_pointer:
    data = json.load(file_pointer)
    file_pointer.close()

concat_data = []
for topic, document in data.items():
    concat_data.extend(document)

df = pd.DataFrame(concat_data)
print(df)

# Setting up the core and adding the fields

i = Indexer()
# i.do_initial_setup()
i.add_fields()

# Index the sample dataset

collection = df.to_dict('records')
# print(collection[0])
i.create_documents(collection)
# i.query('q=death')
