'''
J. ALBERTONE 2025
This class allows to find in EAM if a work order exists for the
asset corresponding.
If yes, it picks up the URL of the WO and open it in a browser
You can use this class at the really beggining of your testbench procedure
in order to avoid loosing time in a test if the board has for example a broken
component.

'''


import requests
import xml.etree.ElementTree as ET
import urllib.parse
import webbrowser


class CernWorkOrderFinder:
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://cmmsx.cern.ch"
        self.soap_url = f"{self.base_url}/WSHub/SOAP"

    def find_from_serial(self, serial_number: str, open_browser: bool = True):
        """
        Searchs a WO with RA status (running or active status) for the given s/n
        a tuple (workordernum, url) is returned or (None, None) if no WO.
        Opens the browser if  open_browser=True.
        
        """
        payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:wsh="http://cern.ch/cmms/infor/wshub">
            <soapenv:Body>
                <wsh:getGridResult>
                    <gridRequest>
                        <gridName>WSJOBS</gridName>
                        <gridFilters>
                            <gridFilter>
                                <fieldName>equipment</fieldName>
                                <fieldValue>{serial_number}</fieldValue>
                                <joiner>AND</joiner>
                                <operator>EQUALS</operator>
                            </gridFilter>
                            <gridFilter>
                                <fieldName>workorderstatus</fieldName>
                                <fieldValue>RA</fieldValue>
                                <joiner>AND</joiner>
                                <operator>EQUALS</operator>
                            </gridFilter>
                        </gridFilters>
                    </gridRequest>
                    <credentials>
                        <username>{self.username}</username>
                        <password>{self.password}</password>
                    </credentials>
                </wsh:getGridResult>
            </soapenv:Body>
        </soapenv:Envelope>
        """

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'Cookie': 'ROUTEID-10080=.1; ROUTEID-10880=.1'
        }

        try:
            response = requests.post(self.soap_url, headers=headers, data=payload, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ conneciton error : {e}")
            return None, None

        # Analyse SOAP answer
        try:
            root = ET.fromstring(response.text)
            workordernum_element = root.find('.//cell[@n="279"][@order="1"][@t="workordernum"]')

            if workordernum_element is not None and workordernum_element.text:
                workordernum = workordernum_element.text.strip()
                workorder_url = f"{self.base_url}/SSO/eamlight/workorder/{urllib.parse.quote(workordernum)}"

                print(f"✅ Work Order Number: {workordernum}")
                print(f"🌐 URL: {workorder_url}")

                if open_browser:
                    webbrowser.open(workorder_url)

                return workordernum, workorder_url

        except ET.ParseError as e:
            print(f"❌ Parsing XML error : {e}")

        print("⚠️ No Work order found for this asset")
        return None, None


if __name__ == "__main__":
    import getpass

    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    serial_number = input("Enter asset serial number (e.g., HCBPEWN001-CR000000): ")

    finder = CernWorkOrderFinder(username, password)
    finder.find_from_serial(serial_number)
