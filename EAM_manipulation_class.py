'''
J. ALBERTONE 2025
This class is dedicated to manipulate EDMS document attached to an EAM asset:
-with the asset number, check if an equipment is existing in EAM
if not
-Create an asset with all fields description required
-loop to the beginning
if yes
-check if an EDMS document is attached to the asset
    if no
    -create an EDMS document and attached it to the equipment
    -loop to the EDMS check
    if yes
    -check the version and its status. if released: increment, if in work: released and increment
upload the file and released the running version

For testing use these adress: 
        self.url_document = "https://testedms.cern.ch/ws/DocumentServiceT"
        self.url_fileService = "https://testedms.cern.ch/ws/FileService?wsdl"
        self.url_structure = "https://testedms.cern.ch/ws/StructureService"
        self.url_cmmsx = "https://cmmsx-test.cern.ch/WSHub/SOAP"

For production use:
        self.url_document = "https://edms.cern.ch/ws/DocumentServiceT"
        self.url_fileService = "https://edms.cern.ch/ws/FileService?wsdl"
        self.url_structure = "https://edms.cern.ch/ws/StructureService"
        self.url_cmmsx = "https://cmmsx.cern.ch/WSHub/SOAP"

Selection configuration for upload path:
        selection_mode = "manual"    -> use the file_path value provided by the caller
        selection_mode = "explorer"  -> open a Windows Explorer dialog

Path type configuration:
        path_type = "file"           -> select or use a single file
        path_type = "directory"      -> select or use all files from one directory

Typical usage:
        manager.choose_upload_path(selection_mode="manual", path_type="directory", file_path=r"C:\my_folder")
        manager.choose_upload_path(selection_mode="explorer", path_type="file")
'''

from getpass import getpass
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from requests import Session
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

class EdmsDocumentManager:
    def __init__(self, username, password, equipment_code, equipment_description, equipment_class, equipment_category, partCode, statusCode, departmentCode, stateCode, operational=False):
        self.username = username
        self.password = password
        self.equipment_code = equipment_code
        
        if operational:
            self.url_document = "https://edms.cern.ch/ws/DocumentServiceT"
            self.url_fileService = "https://edms.cern.ch/ws/FileService?wsdl"
            self.url_structure = "https://edms.cern.ch/ws/StructureService"
            self.url_cmmsx = "https://cmmsx.cern.ch/WSHub/SOAP"
        else:
            self.url_document = "https://testedms.cern.ch/ws/DocumentServiceT"
            self.url_fileService = "https://testedms.cern.ch/ws/FileService?wsdl"
            self.url_structure = "https://testedms.cern.ch/ws/StructureService"
            self.url_cmmsx = "https://cmmsx-test.cern.ch/WSHub/SOAP"

        self.description = equipment_description
        self.classCode = equipment_class
        self.categoryCode = equipment_category
        self.partCode = partCode
        self.statusCode = statusCode
        self.departmentCode = departmentCode
        self.stateCode = stateCode

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.password)

    def choose_upload_path(self, selection_mode="manual", path_type="directory", file_path=""):
        if selection_mode == "explorer":
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            if path_type == "file":
                selected_path = filedialog.askopenfilename(title="Select file to upload")
            else:
                selected_path = filedialog.askdirectory(title="Select directory to upload")

            root.destroy()
            return selected_path.strip()

        return file_path.strip()
    def get_equipment_info(self):
        edms_id = None
        version = None

        # step 1 : test if the EDMS document exists
        soap_get_asset = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://webservices.edms.cern.ch">
        <soapenv:Header/>
        <soapenv:Body>
            <web:getDocuments>
            <objectType>A</objectType>
            <objectEdmsId>{self.equipment_code}</objectEdmsId>
            </web:getDocuments>
        </soapenv:Body>
        </soapenv:Envelope>
        """

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": ""
        }

        response_get_asset = self.session.post(self.url_document, data=soap_get_asset, headers=headers)
        print("Status Code (getAssetInfo):", response_get_asset.status_code)
        #print("response", response_get_asset.text)
        root = ET.fromstring(response_get_asset.text)
        found = root.findall(".//edmsId")

        try:
            exitCode = int(root.find(".//exitcode").text)
        except Exception:
            print("⚠️ Exit code unknown in the SOAP answer")
            return None, None

        print("exit code:", exitCode)

        # --- Asset NOT present: create then recall same function ---
        if exitCode in (21001, 100):
            print("Object does not exist, creation ongoing...")
            payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                    xmlns:wsh="http://cern.ch/cmms/infor/wshub">
                <soapenv:Header/>
                <soapenv:Body>
                    <wsh:createEquipment>
                        <equipment>
                            <description>{self.description}</description>
                            <code>{self.equipment_code}</code>
                            <typeCode>A</typeCode>
                            <classCode>{self.classCode}</classCode>
                            <categoryCode>{self.categoryCode}</categoryCode>
                            <statusCode>{self.statusCode}</statusCode>
                            <departmentCode>{self.departmentCode}</departmentCode>
                            <stateCode>{self.stateCode}</stateCode>
                            <partCode>{self.partCode}</partCode>
                        </equipment>
                        <credentials>
                            <password>{self.password}</password>
                            <username>{self.username}</username>
                        </credentials>
                    </wsh:createEquipment>
                </soapenv:Body>
            </soapenv:Envelope>
            """

            headers_cmmsx = {'Content-Type': 'text/xml; charset=utf-8'}
            response = requests.post(self.url_cmmsx, headers=headers_cmmsx, data=payload)
            if "faultcode" in response.text.lower():
                root = ET.fromstring(response.content)
                faultstring_element = root.find('.//faultstring')
                if faultstring_element is not None:
                    print("❌ Equipment creation failed:", faultstring_element.text)
                    print("Response text (createEquipment):", response.text)
            else:
                print("✅ Equipment created successfully.")
                # loop to get EDMS ID
                return self.get_equipment_info()

        # --- Asset present, EDMS document found ---
        elif found:
            print("equipment already existing")
            edms_id = int(found[0].text)
            print(f"✅ Document found : {edms_id}")
            #Update status and state fields in EAM Fields (State: GOOD or DEF ; Status: IMFT [in manufacturing] or IST [stored] )
            payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                    xmlns:wsh="http://cern.ch/cmms/infor/wshub">
                <soapenv:Header/>
                <soapenv:Body>
                    <wsh:updateEquipment>
                        <equipment>
                            <code>{self.equipment_code}</code>
                            <statusCode>{self.statusCode}</statusCode>
                            <stateCode>{self.stateCode}</stateCode>
                        </equipment>
                        <credentials>
                            <password>{self.password}</password>
                            <username>{self.username}</username>
                        </credentials>
                    </wsh:updateEquipment>
                </soapenv:Body>
            </soapenv:Envelope>
            """  

            headers_cmmsx = {'Content-Type': 'text/xml; charset=utf-8'}
            response = requests.post(self.url_cmmsx, headers=headers_cmmsx, data=payload)
            if "faultcode" in response.text.lower():
                root = ET.fromstring(response.content)
                faultstring_element = root.find('.//faultstring')
                if faultstring_element is not None:
                    print("❌ State and status update failed:", faultstring_element.text)
                    print("Response text (createEquipment):", response.text)
            else:
                print("✅ Equipment status and state updated successfully.")

            # read the version
            soap_get_doc = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
            <ns2:getDocument xmlns:ns2="http://webservices.edms.cern.ch">
                <username>{self.username}</username>
                <edmsId>{edms_id}</edmsId>
                <version>LATEST</version>
            </ns2:getDocument>
            </soap:Body>
            </soap:Envelope>"""
            response_get_doc = self.session.post(self.url_document, data=soap_get_doc, headers=headers)
            print("Status Code (getDocumentsInfo):", response_get_doc.status_code)

            root = ET.fromstring(response_get_doc.text)
            try:
                version = int(root.find(".//version").text)
                status = root.find(".//status").text
            except Exception:
                print("⚠️ Impossible to read the document version or status")
                return edms_id, None

            print("actual version: ", version)
            print("actual status: ", status)
            

            # document ‘in work’: release + incr version
            if status == "In Work":
                print("❌ document 'in work' : let's release it")
                soap_change_status = f"""<?xml version="1.0" encoding="UTF-8"?>
                    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Body>
                        <ns2:changeStatus xmlns:ns2="http://webservices.edms.cern.ch">
                            <username>{self.username}</username>
                            <edmsId>{edms_id}</edmsId>
                            <version>{version}</version>
                            <newStatus>released</newStatus>
                        </ns2:changeStatus>
                        </soap:Body>
                    </soap:Envelope>
                    """
                response_change_status = self.session.post(self.url_document, data=soap_change_status, headers=headers)
                print("Status Code (changeStatus):", response_change_status.status_code)
                print("🔄 Document released, now increment version to allow the uploading of files")
                version += 1
                soap_increment_version = f"""<?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                    <ns2:createDocumentVersion xmlns:ns2="http://webservices.edms.cern.ch">
                        <username>{self.username}</username>
                        <edmsId>{edms_id}</edmsId>
                        <versionParameters>
                            <versionIndex>{version}</versionIndex>
                        </versionParameters>
                    </ns2:createDocumentVersion>
                    </soap:Body>
                </soap:Envelope>
                """
                response_increment_version = self.session.post(self.url_document, data=soap_increment_version, headers=headers)
                print("Status Code (changeStatus):", response_increment_version.status_code)
                print("⬆ document incremented to version:", version)
                return edms_id, version

            else:
                print("✅ document released, let's increment the version")
                version += 1
                soap_increment_version = f"""<?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                    <ns2:createDocumentVersion xmlns:ns2="http://webservices.edms.cern.ch">
                        <username>{self.username}</username>
                        <edmsId>{edms_id}</edmsId>
                        <versionParameters>
                            <versionIndex>{version}</versionIndex>
                        </versionParameters>
                    </ns2:createDocumentVersion>
                    </soap:Body>
                </soap:Envelope>
                """
                response_increment_version = self.session.post(self.url_document, data=soap_increment_version, headers=headers)
                print("Status Code (changeStatus):", response_increment_version.status_code)
                print("⬆ document incremented to version:", version)
                return edms_id, version

        else:
            print("❌ tag <edmsId> not found. Creating document...")
            # createDocument
            soap_create = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                <ns2:createDocument xmlns:ns2="http://webservices.edms.cern.ch">
                    <username>{self.username}</username>
                    <document>
                    <context>BE-BI-MTF</context>
                    <releaseProc>DOC-OWNER</releaseProc>
                    <title>{self.equipment_code}</title>
                    <type>Report</type>
                    <equipmentCode></equipmentCode>
                    </document>
                </ns2:createDocument>
                </soap:Body>
            </soap:Envelope>"""
            response_create = self.session.post(self.url_document, data=soap_create, headers=headers)
            print("Status Code (createDocument):", response_create.status_code)
            root = ET.fromstring(response_create.text)
            created = root.findall(".//edmsId")
            print("create response:", response_create.text)
            if created:
                edms_id = created[0].text
                version = 1
                print("📄 Document created with edmsId:", edms_id)
                # attach document to concerned asset (child = doc, parent = Asset)
                soap_attach = f"""<?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                    <ns2:attach xmlns:ns2="http://webservices.edms.cern.ch">
                        <username>{self.username}</username>
                        <link>   
                        <childEdmsId>{edms_id}</childEdmsId>
                        <childType>D</childType>
                        <childVersion>1</childVersion>
                        <parentEdmsId>{self.equipment_code}</parentEdmsId>
                        <parentType>A</parentType>
                        </link>
                    </ns2:attach>
                    </soap:Body>
                </soap:Envelope> 
                """
                response_attach = self.session.post(self.url_structure, data=soap_attach, headers=headers)
                print("Status Code (AttachDocument):", response_attach.status_code)
            else:
                print("⚠️ Document created but edmsId not found in response.")
                return None, None
        
        return edms_id, version

    #upload file to EDMS
    def upload_file (self, username, password, filePath, edms_id, version): #(self, filePath, edms_id, version):
        filepath = Path(filePath)
        url_document = self.url_document
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": ""
        }
        session = Session()
        session.auth = HTTPBasicAuth(self.username, self.password)
        transport = Transport(session=session)
        client = Client(self.url_fileService, transport=transport)

        if not filepath.exists():
            raise FileNotFoundError(f"Path not found: {filePath}")

        if filepath.is_dir():
            files_to_upload = sorted(path for path in filepath.iterdir() if path.is_file())
        else:
            files_to_upload = [filepath]

        if not files_to_upload:
            raise FileNotFoundError(f"No files found in directory: {filePath}")

        for file_to_upload in files_to_upload:
            with open(file_to_upload, "rb") as f:
                file_data = f.read()

            response = client.service.putFile(
                username=self.username,
                docEdmsId=int(edms_id),
                docVersion=int(version),
                file={
                    "name": file_to_upload.name,
                    "overwriteExisting": True,
                    "content": file_data
                }
            )
            print(f"Upload executed for {file_to_upload.name}:", repr(response))

        print(f"{len(files_to_upload)} file(s) uploaded to EDMS")
        #now the file is uploaded, we can released the document 
        soap_change_status = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
            <ns2:changeStatus xmlns:ns2="http://webservices.edms.cern.ch">
                <username>{self.username}</username>
                <edmsId>{edms_id}</edmsId>
                <version>{version}</version>
                <newStatus>released</newStatus>
            </ns2:changeStatus>
            </soap:Body>
        </soap:Envelope>
        """
        response_change_status = session.post(url_document, data=soap_change_status, headers=headers)
        print("Status Code (changeStatus):", response_change_status.status_code)
        print("✅ Document released, asset ready for the next test")

        # attach (if not yet the case) document to concerned asset (child = doc, parent = Asset)
        soap_attach = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
            <ns2:attach xmlns:ns2="http://webservices.edms.cern.ch">
                <username>{self.username}</username>
                <link>   
                <childEdmsId>{edms_id}</childEdmsId>
                <childType>D</childType>
                <parentEdmsId>{self.equipment_code}</parentEdmsId>
                <parentType>A</parentType>
                </link>
            </ns2:attach>
            </soap:Body>
        </soap:Envelope> 
        """
        response_attach = self.session.post(self.url_structure, data=soap_attach, headers=headers)
        print("🔗Status Code (AttachDocument):", response_attach.status_code)





if __name__ == "__main__":
    # Test parameters
    username = input("Enter your username: ").strip()
    password = getpass("Enter your password: ")
    equipment_code = input("Enter the equipment code: ").strip()
    equipment_description = "WorldFIP Control Card"
    equipment_class = "BP06"
    equipment_category = "HCBPEF_001"
    part_code = "HCBPEF001"
    status_code = "IST"
    department_code = "BIBPM"
    state_code = "GOOD"  # Operational
    
    # Create instance of EdmsDocumentManager
    edms_manager = EdmsDocumentManager(
        username=username,
        password=password,
        equipment_code=equipment_code,
        equipment_description=equipment_description,
        equipment_class=equipment_class,
        equipment_category=equipment_category,
        partCode=part_code,
        statusCode=status_code,
        departmentCode=department_code,
        stateCode=state_code,
        operational=False  # Use test environment
    )
    
    # Test equipment info retrieval
    print("\nTesting get_equipment_info():")
    edms_id, version = edms_manager.get_equipment_info()
    
    if edms_id and version:
        print(f"\nSuccessfully retrieved equipment info:")
        print(f"EDMS ID: {edms_id}")
        print(f"Version: {version}")
        
        # Test file upload
        print("\nTesting file upload:")
        selection_mode = input("Choose upload source: [1] manual path, [2] explorer dialog: ").strip()
        path_type = "directory"
        manual_file_path = ""
        if selection_mode == "2":
            explorer_type = input("Choose in explorer: [1] file, [2] directory: ").strip()
            path_type = "file" if explorer_type == "1" else "directory"
        else:
            manual_file_path = input("Enter file or directory path: ").strip()

        selected_upload_path = edms_manager.choose_upload_path(
            selection_mode="explorer" if selection_mode == "2" else "manual",
            path_type=path_type,
            file_path=manual_file_path,
        )

        if not selected_upload_path:
            print("No file or directory selected.")
        else:
            try:
                edms_manager.upload_file(
                    username=username,
                    password=password,
                    filePath=selected_upload_path,
                    edms_id=edms_id,
                    version=version
                )
            except FileNotFoundError:
                print(f"Test path not found: {selected_upload_path}")
            except Exception as e:
                print(f"Error during file upload: {str(e)}")
    else:
        print("Failed to retrieve equipment info")





