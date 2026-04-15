from getpass import getpass
from pathlib import Path

from EAM_manipulation_class import EdmsDocumentManager


def main():
    print("=== Test upload_file() sur la base CERN de test ===")

    username = input("Username: ").strip()
    password = getpass("Password: ")
    equipment_code = input("Equipment code (asset parent): ").strip()
    edms_id = int(input("EDMS document id: ").strip())
    version = int(input("Document version: ").strip())

    selection_mode = "explorer"
    path_type = "file"
    file_path = r"Z:\Python_projects\EAM_soap_api\pyassetmanagement"

    manager = EdmsDocumentManager(
        username=username,
        password=password,
        equipment_code=equipment_code,
        equipment_description="Upload test",
        equipment_class="BP06",
        equipment_category="HCBPEF_001",
        partCode="HCBPEF001",
        statusCode="IST",
        departmentCode="BIBPM",
        stateCode="GOOD",
        operational=False,
    )

    selected_path = manager.choose_upload_path(
        selection_mode=selection_mode,
        path_type=path_type,
        file_path=file_path,
    )

    print(f"CMMSX test URL: {manager.url_cmmsx}")

    if not selected_path:
        print("Aucun fichier ou repertoire selectionne.")
        return

    print(f"Target path: {Path(selected_path).resolve()}")

    try:
        manager.upload_file(
            username=username,
            password=password,
            filePath=selected_path,
            edms_id=edms_id,
            version=version,
        )
        print("Upload test completed.")
    except FileNotFoundError as exc:
        print(f"File error: {exc}")
    except Exception as exc:
        print(f"Upload error: {exc}")


if __name__ == "__main__":
    main()
