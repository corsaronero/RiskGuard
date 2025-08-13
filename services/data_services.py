
import requests
import cdsapi

class DataServices:
    def __init__(self, url):
        self.url = url


    def getData(self):
        
        try:
            response = requests.get(self.url) #verify=False
            # Check for successful status code
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: HTTP {response.status_code} - {response.reason}")
                return None

        except requests.exceptions.SSLError as e:
            print("SSL Error:", e)
            return None

        except requests.exceptions.ConnectionError as e:
            print("Connection Error:", e)
            return None

        except requests.exceptions.Timeout as e:
            print("Timeout Error:", e)
            return None

        except requests.exceptions.RequestException as e:
            print("General Request Exception:", e)
            return None

        except Exception as e:
            print("Unexpected Error:", e)
            return None

    def getLicences(self):
        
        try:
            key = cdsapi.Client().key
            token = key
            headers = {
                "PRIVATE-TOKEN": token, 
                "Accept": "application/json"
            }
            response = requests.get(self.url, headers=headers)

            # Check for successful status code
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: HTTP {response.status_code} - {response.reason}")
                return None

        except requests.exceptions.ConnectionError as e:
            print("Connection Error:", e)
            return None

        except requests.exceptions.Timeout as e:
            print("Timeout Error:", e)
            return None

        except requests.exceptions.RequestException as e:
            print("General Request Exception:", e)
            return None

        except Exception as e:
            print("Unexpected Error:", e)
            return None


    def putLicences(self, licence_id, revision):
    
        try:
            key = cdsapi.Client().key
            token = key
            headers = {
                "PRIVATE-TOKEN": token, 
                "Accept": "application/json"
            }
            payload = {"revision": revision}
            urlNewLicence = self.url + licence_id
            response = requests.put(urlNewLicence, json=payload, headers=headers)

            # Check for successful status code
            if response.status_code in [200, 201]:
                print("SERVICE", response)
                return response.json()
            else:
                print(f"Error: HTTP {response.status_code} - {response.reason}")
                return None

        except Exception as e:
            print("Unexpected Error:", e)
            return None


    def postEstimateData(self, data):
        headers = {
            'Content-Type': 'application/json'  # Content type is set to JSON
        }
        try:
            
            response = requests.post(self.url, json=data, headers=headers)
            print("SEND", response.status_code)
            # Check if the request was successful (200 OK or 201 Created)
            if response.status_code in (200, 201):
                return response.json()  # Return the JSON response content
            else:
                print("Error:", response.status_code, response.text)
                return None

        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            return None


    def postConstraintsData(self, data):
        headers = {
            'Content-Type': 'application/json'  # Set content type to JSON
        }
        try:
            response = requests.post(self.url, json=data, headers=headers)
            
            if response.status_code in (200, 201):  # 201 for successful resource creation
                return response.json()
            else:
                print("Error:", response.status_code, response.text)
                return None
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            return None


