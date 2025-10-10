'''
class dedicated to read the FIP serial number
The card must have the adress 1
Return the formatted asset number as : HCBPEF001-CRXXXXXX
command to ask this class: from FIP_serial_reader_class import FesaSerialReader
J. ALBERTONE 2025
'''
import time
import pyjapc


class SerialNumberBlock:
    FIP = 1
    BACKPLANE = 9
    B1H = 17
    B1V = 25
    B2H = 41
    B2V = 49

    SN1_FIELDNAME = "fipReadSerialSeg1"
    SN2_FIELDNAME = "fipReadSerialSeg2"

    def __init__(self, device_name):
        self.device_name = device_name
        self.fip_card = None
        self.backplane = None
        self.norm_b1h = None
        self.norm_b1v = None
        self.norm_b2h = None
        self.norm_b2v = None

    def set_fip_card(self, value): self.fip_card = value
    def set_backplane(self, value): self.backplane = value
    def set_norm_b1h(self, value): self.norm_b1h = value
    def set_norm_b1v(self, value): self.norm_b1v = value
    def set_norm_b2h(self, value): self.norm_b2h = value
    def set_norm_b2v(self, value): self.norm_b2v = value


class FesaSerialReader:
    def __init__(self, device_name='bpmDev'):
        self.device_name = device_name
        self.japc = pyjapc.PyJapc(noSet=False)  # False = mode opérationnel
        self.japc.setSelector("")
        print(f"[INIT] FESA device: {self.device_name}")

    def set_fesa(self, fip_param=''):
        """
        Force  mode 'SerNumTask' in FESA
        """
        print("SET Serial number reading task with FESA for:", self.device_name)
        result = self.japc.getParam(self.device_name + fip_param)

        # Cleaning the tuple
        for param in result:
            result[param] = result[param][1]

        result['taskRequest'] = 'SerNumTask'
        self.japc.setParam(self.device_name + fip_param, result)

    def get_fesa(self, fip_param=''):
        """
        Pick up serial number
        """
        print("GET Serial numbers with FESA for:", self.device_name)
        result = self.japc.getParam(self.device_name + fip_param)
        return result

    def disconnect(self):
        """
        RBAC logout
        """
        self.japc.rbacLogout()
        print("[INFO] rbacLogout...")

    @staticmethod
    def get_sn_for_agent(serial_seg, lag_agent):
        num = ""
        for b in range(6):
            num += hex(serial_seg[b + lag_agent])[2:]
        serial_n = int(num, 16)
        return serial_n % 1000000

    def get_first_fip_card_value(self):
        """
        return first FIP card serial number and close the connection
        """
        try:
            self.set_fesa('/Config')
            time.sleep(5)
            fip_param = self.get_fesa('/SerialNumbers#fipReadSerialSeg1')

            sn_list = []
            for i, seg in enumerate(fip_param):
                serial_number = SerialNumberBlock(f"test_device_name {i+1}")
                serial_number.set_fip_card(self.get_sn_for_agent(seg, SerialNumberBlock.FIP))
                serial_number.set_backplane(self.get_sn_for_agent(seg, SerialNumberBlock.BACKPLANE))
                serial_number.set_norm_b1h(self.get_sn_for_agent(seg, SerialNumberBlock.B1H))
                serial_number.set_norm_b1v(self.get_sn_for_agent(seg, SerialNumberBlock.B1V))
                serial_number.set_norm_b2h(self.get_sn_for_agent(seg, SerialNumberBlock.B2H))
                serial_number.set_norm_b2v(self.get_sn_for_agent(seg, SerialNumberBlock.B2V))
                sn_list.append(serial_number)

            if sn_list:
                return "HCBPEF001-CR" + str(sn_list[0].fip_card)
            return None

        finally:
            # logout
            self.disconnect()
