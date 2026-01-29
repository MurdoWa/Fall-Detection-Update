# To install Firestore commands:
# pip install google-cloud-firestore
# pip install --upgrade firebase-admin

# Set credentials
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"

# Use the application default credentials.
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta


class FirestoreClient():
    doc_listeners = []
    doc_subs = {}

    def __init__(self, credentialsPath) -> None:
        cred = credentials.Certificate(credentialsPath)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def set_doc(self, col_name, doc_name, data):
        docRef = self.db.collection(col_name).document(doc_name)
        docRef.set(data)

    def update_doc(self, col_name, doc_name, data):
        docRef = self.db.collection(col_name).document(doc_name)

        try:
            docRef.update(data)
        except:
            self.set_doc(col_name, doc_name, data)

    #  def push_test_data(self, collectionName, docName, amount):
    #    data = {}
    #    start_timestamp = datetime(2024, 9, 24, 0, 0, 0)

    #    for i in range(amount):
    #      new_timestamp = start_timestamp + timedelta(hours = i)
    #      timestamp_string = new_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
    #      current_hour = new_timestamp.hour
    #      current_temp = round(temp_fluctuation(current_hour), 1)
    #      data[timestamp_string] = current_temp
    #
    #    self.update_doc(collectionName, docName, data)

    def subscribe_doc(self, col_name, doc_name):
        doc_ref = self.db.collection(col_name).document(doc_name)
        new_listener = doc_ref.on_snapshot(self.on_snapshot)
        self.doc_listeners.append(new_listener)

    def on_snapshot(self, doc_snapshot, changes, read_time):

        for doc in doc_snapshot:
            self.doc_subs[doc.id] = doc_snapshot
            print(doc.id)
            print(f'Document {doc.id} updated: {doc.to_dict()}')