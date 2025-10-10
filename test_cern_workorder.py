from find_WO_from_SN_class import CernWorkOrderFinder
import getpass


def main():
    print("=== Class test: CernWorkOrderFinder ===")
    
    # collect credentials and asset s/n
    username = input("🔑 Username: ")
    password = getpass.getpass("🔒 Password: ")
    serial_number = input("🔍 Serial number of the equipment (ie: HCBPEWN001-CR000000): ")

    # search object creation
    finder = CernWorkOrderFinder(username, password)

    # call method
    workordernum, url = finder.find_from_serial(serial_number)

    # display resulsts
    print("\n=== results ===")
    if workordernum:
        print(f"✅ Work Order found : {workordernum}")
        print(f"🌐 URL opened in browser : {url}")
    else:
        print("⚠️ No Work order found for this asset.")


if __name__ == "__main__":
    main()
