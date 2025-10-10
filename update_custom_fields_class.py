'''
J. ALBERTONE 2025
This class allows to write data in custom fields in EAM
You can write up to 4 custom fields.
For this you need to know the code of the field (go to eam.cern.ch) and
the format (text, number, binary, date etc..)

for testing  use this adress:
"https://cmmsx-test.cern.ch/WSHub/SOAP"

for production:
"https://test.cern.ch/WSHub/SOAP"

'''
import requests
import xml.etree.ElementTree as ET


class EamCustomFieldsManager:
    def __init__(
        self,
        username,
        password,
        custom_fieldCode_1,
        custom_fieldCode_2,
        custom_fieldCode_3,
        custom_fieldCode_4,
        custom_fieldValue_1,
        custom_fieldValue_2,
        custom_fieldValue_3,
        custom_fieldValue_4
    ):
        self.username = username
        self.password = password
        self.url = "https://cmmsx-test.cern.ch/WSHub/SOAP"

        # custom fields
        self.CustomFieldCode_1 = custom_fieldCode_1
        self.CustomFieldCode_2 = custom_fieldCode_2
        self.CustomFieldCode_3 = custom_fieldCode_3
        self.CustomFieldCode_4 = custom_fieldCode_4

        self.CustomFieldValue_1 = custom_fieldValue_1
        self.CustomFieldValue_2 = custom_fieldValue_2
        self.CustomFieldValue_3 = custom_fieldValue_3
        self.CustomFieldValue_4 = custom_fieldValue_4

    def feed_custom_fields(self, equipment_code):
        payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:wsh="http://cern.ch/cmms/infor/wshub">
            <soapenv:Header/>
            <soapenv:Body>
                <wsh:updateEquipment>
                    <equipment>
                        <code>{equipment_code}</code>
                        <customFields>
                            <customField>
                                <code>{self.CustomFieldCode_1}</code>
                                <value>{self.CustomFieldValue_1}</value>
                            </customField>
                            <customField>
                                <code>{self.CustomFieldCode_2}</code>
                                <value>{self.CustomFieldValue_2}</value>
                            </customField>
                            <customField>
                                <code>{self.CustomFieldCode_3}</code>
                                <value>{self.CustomFieldValue_3}</value>
                            </customField>
                            <customField>
                                <code>{self.CustomFieldCode_4}</code>
                                <value>{self.CustomFieldValue_4}</value>
                            </customField>
                        </customFields>
                    </equipment>
                    <credentials>
                        <username>{self.username}</username>
                        <password>{self.password}</password>
                    </credentials>
                </wsh:updateEquipment>
            </soapenv:Body>
        </soapenv:Envelope>
        """

        headers = {'Content-Type': 'text/xml; charset=utf-8'}

        try:
            response = requests.post(self.url, headers=headers, data=payload)
            response.raise_for_status()

            if "faultcode" in response.text.lower():
                root = ET.fromstring(response.content)
                faultstring_element = root.find('.//faultstring')
                if faultstring_element is not None:
                    print("SOAP Fault:", faultstring_element.text)
                return False

            return True

        except requests.RequestException as e:
            print("Erreur HTTP:", e)
            return False
