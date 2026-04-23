import requests
import json

class OpenEHRUploader:
    """Upload compositions to openEHR server (EHRbase)"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "openEHR-VERSION": "1.0.4"
        }
    
    def get_or_create_ehr(self, patient_id: str) -> str:
        """Get existing EHR or create new one for patient"""
        
        # Try to get existing EHR
        response = requests.get(
            f"{self.base_url}/ehr",
            params={"subject_id": patient_id, "subject_namespace": "patients"},
            headers=self.headers,
            auth=self.auth
        )
        
        if response.status_code == 200:
            return response.json()['ehr_id']['value']
        
        # Create new EHR
        ehr_status = {
            "_type": "EHR_STATUS",
            "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
            "name": {"value": "EHR Status"},
            "subject": {
                "_type": "PARTY_SELF",
                "external_ref": {
                    "id": {
                        "_type": "GENERIC_ID",
                        "value": patient_id,
                        "scheme": "patients"
                    },
                    "namespace": "patients",
                    "type": "PERSON"
                }
            },
            "is_modifiable": True,
            "is_queryable": True
        }
        
        response = requests.post(
            f"{self.base_url}/ehr",
            json=ehr_status,
            headers=self.headers,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()['ehr_id']['value']
    
    def upload_composition(self, ehr_id: str, composition: dict) -> str:
        """Upload composition and return composition ID"""
        
        response = requests.post(
            f"{self.base_url}/ehr/{ehr_id}/composition",
            json=composition,
            headers=self.headers,
            auth=self.auth
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(
                f"Upload failed: {response.status_code} - {response.text}"
            )
        
        return response.json().get('uid', {}).get('value', 'unknown')
