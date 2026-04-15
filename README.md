# pyassetmanagement

[![Stars](https://img.shields.io/github/stars/djo074/pyassetmanagement?style=social)](https://gitlab.cern.ch/bi/bp/pyassetmanagement/)
[![Forks](https://img.shields.io/github/forks/djo074/pyassetmanagement?style=social)](https://gitlab.cern.ch/bi/bp/pyassetmanagement/)


Python classes which deal with EAM, EDMS, and FESA class, for reading s/n and providing asset management.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Important Links](#important-links)
- [Footer](#footer)

## Description

The `pyassetmanagement` project provides Python classes for interacting with EAM (Enterprise Asset Management), EDMS (Engineering Document Management System), and FESA (Front-End Software Architecture) systems. It focuses on reading serial numbers and facilitating asset management tasks, particularly within the CERN environment.

## Features

- **EAM Asset Management:**
    - Check if an equipment exists in EAM based on its asset number.
    - Create a new asset in EAM with required field descriptions using the `EAM_manipulation_class.py`.
- **EDMS Document Management:**
    - Check if an EDMS document is attached to an asset.
    - Create and attach EDMS documents to equipment using SOAP requests.
    - Manage document versions and statuses (e.g., release and increment versions).
    - Upload files to EDMS and release the running version.
- **FESA Serial Number Reading:**
    - Read serial numbers from FIP (Front-end Interconnect Processor) cards using the `FIP_serial_reader_class.py`.
    - Format the asset number.
    - Force 'SerNumTask' in FESA.
- **Work Order Management:**
    - Find work orders associated with a specific serial number in EAM using the `find_WO_from_SN_class.py`.
    - Open the work order URL in a web browser.
    - Identifies WO with RA status.
- **Custom Field Updates:**
    - Update custom fields in EAM with specific values using the `update_custom_fields_class.py`.
    - Supports up to 4 custom fields.

## Tech Stack

- Python
- XML
- SOAP

## Installation

1.  Clone the repository:

    ```bash
    git clone https://gitlab.cern.ch/bi/bp/pyassetmanagement.git
    cd pyassetmanagement
    ```

2.  Install the required Python packages. This project uses `requests`, `xml.etree.ElementTree`, `urllib.parse`, `webbrowser`, `pyjapc`, `zeep` and `pathlib`.  It is advised to use a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install requests
    pip install pyjapc
    pip install zeep
    ```

## Usage

### EAM and EDMS Interaction

To interact with EAM and EDMS, use the `EAM_manipulation_class.py`. Here's an example of how to use the `EdmsDocumentManager` class:

```python
from EAM_manipulation_class import EdmsDocumentManager

username = "your_username"
password = "your_password"
equipment_code = "equipment_code"
equipment_description = "Equipment Description"
equipment_class = "Equipment Class"
equipment_category = "Equipment Category"
partCode = "Part Code"
statusCode = "Status Code"
departmentCode = "Department Code"
stateCode = "State Code"

edms_manager = EdmsDocumentManager(
    username, password, equipment_code, equipment_description,
    equipment_class, equipment_category, partCode, statusCode, departmentCode, stateCode
)

edms_id, version = edms_manager.get_equipment_info()
if edms_id and version:
    print(f"EDMS ID: {edms_id}, Version: {version}")

    # Example of uploading a file
    file_path = "path/to/your/file.txt"  # Replace with the actual file path
    edms_manager.upload_file(username, password, file_path, edms_id, version)
else:
    print("Failed to retrieve EDMS information.")
```

### FESA Serial Number Reading

To read serial numbers from FIP cards, use the `FIP_serial_reader_class.py`. Here's an example:

```python
from FIP_serial_reader_class import FesaSerialReader

fesa_reader = FesaSerialReader(device_name='bpmDev')
serial_number = fesa_reader.get_first_fip_card_value()

if serial_number:
    print(f"Serial Number: {serial_number}")
else:
    print("Failed to retrieve serial number.")
```

### Finding Work Orders

To find work orders associated with a serial number, use the `find_WO_from_SN_class.py`. Here's an example:

```python
from find_WO_from_SN_class import CernWorkOrderFinder
import getpass

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
serial_number = input("Enter asset serial number (e.g., HCBPEWN001-CR000000): ")

finder = CernWorkOrderFinder(username, password)
workordernum, url = finder.find_from_serial(serial_number)

if workordernum:
    print(f"Work Order Number: {workordernum}")
    print(f"URL: {url}")
else:
    print("No Work order found for this asset")
```

### Updating Custom Fields

To update custom fields in EAM, use the `update_custom_fields_class.py`. Here's an example:

```python
from update_custom_fields_class import EamCustomFieldsManager

username = "your_username"
password = "your_password"
custom_fieldCode_1 = "field_code_1"
custom_fieldCode_2 = "field_code_2"
custom_fieldCode_3 = "field_code_3"
custom_fieldCode_4 = "field_code_4"
custom_fieldValue_1 = "value_1"
custom_fieldValue_2 = "value_2"
custom_fieldValue_3 = "value_3"
custom_fieldValue_4 = "value_4"
equipment_code = "equipment_code"

field_manager = EamCustomFieldsManager(
    username, password,
    custom_fieldCode_1, custom_fieldCode_2, custom_fieldCode_3, custom_fieldCode_4,
    custom_fieldValue_1, custom_fieldValue_2, custom_fieldValue_3, custom_fieldValue_4
)

if field_manager.feed_custom_fields(equipment_code):
    print("Custom fields updated successfully.")
else:
    print("Failed to update custom fields.")
```

## Project Structure

```
pyassetmanagement/
├── EAM_manipulation_class.py
├── FIP_serial_reader_class.py
├── find_WO_from_SN_class.py
├── test_cern_workorder.py
├── update_custom_fields_class.py
└── README.md
```

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive messages.
4.  Submit a pull request.

## License

No license provided. All rights reserved.

## Important Links

*   [Repository URL](https://gitlab.cern.ch/bi/bp/pyassetmanagement/)

## Footer

[pyassetmanagement](https://gitlab.cern.ch/bi/bp/pyassetmanagement/) - Developed by J.Albertone.  Feel free to [fork](https://gitlab.cern.ch/bi/bp/pyassetmanagement/-/forks/new), star, and open issues!

---

<p align="center">[This Readme generated by ReadmeCodeGen.](https://www.readmecodegen.com/)</p>