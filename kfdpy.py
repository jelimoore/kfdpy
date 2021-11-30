import serial
from enum import Enum
import time

class KFDReplyFailed(Exception):
    pass

class KFDInvalidOpcode(Exception):
    pass

class KFDWriteFailed(Exception):
    pass

class KFDSerialTooLong(Exception):
    pass

class KFDRadioTimeout(Exception):
    pass


class KFDSelfTestCodes(Enum):
    SELFTEST_PASS = 0
    SELFTEST_FAIL_DATA_SHORT_TO_GND = 1
    SELFTEST_FAIL_SENSE_SHORT_TO_GND = 2
    SELFTEST_FAIL_DATA_SHORT_TO_VCC = 3
    SELFTEST_FAIL_SENSE_SHORT_TO_VCC = 4
    SELFTEST_DATA_SENSE_SHORT = 5
    SELFTEST_SENSE_DATA_SHORT = 6

class P25MR():
    KFD_READY = b'\xC0'
    MR_READY = b'\xD0'

class KFDTool():
    READ_REQ = b'\x11'
    WRITE_REQ = b'\x12'
    ENTER_BOOTLOADER = b'\x13'
    RESET = b'\x14'
    SELF_TEST = b'\x15'
    SEND_KEY_SIG = b'\x16'
    SEND_BYTE = b'\x17'

    ERROR_REPLY = b'\x20'
    READ_REPLY = b'\x21'
    WRITE_REPLY = b'\x22'

    READ_ADAPTER_VER = b'\x01'
    READ_FW_VER = b'\x02'
    READ_UID = b'\x03'
    READ_MODEL = b'\x04'
    READ_HW_REV = b'\x05'
    READ_SN = b'\x06'

    WRITE_MODEL = b'\x01'
    WRITE_SN = b'\x02'

    ERROR_INVALID_CMD_LENGTH = b'\x01'
    ERROR_WRITE_FAILED = b'\x06'

    SERIAL_HEADER = b'\x61'
    SERIAL_FOOTER = b'\x61'

    def __init__(self, port):
        self._serial = serial.Serial(port, 115200, timeout=2)
        time.sleep(3)

    def open(self):
        self._serial.open()

    def close(self):
        self._serial.close()

    def getAdapterVer(self):
        c = self._genInfoBytes(KFDTool.READ_REQ, KFDTool.READ_ADAPTER_VER)
        self._serial.write(c)
        resp = self._serial.read(7)
        # check that the reply is what we're expecting
        result = resp[1:2]
        opcode = resp[2:3]
        
        version = ""

        if (result == KFDTool.READ_REPLY and opcode == KFDTool.READ_ADAPTER_VER):
            major = int.from_bytes(resp[3:4], "big")
            minor = int.from_bytes(resp[4:5], "big")
            patch = int.from_bytes(resp[5:6], "big")

            version = "{}.{}.{}".format(major, minor, patch)
        else:
            raise KFDReplyFailed("KFDTool replied with a bad code")

        return version

    def getFwVer(self):
        c = self._genInfoBytes(KFDTool.READ_REQ, KFDTool.READ_FW_VER)
        self._serial.write(c)
        resp = self._serial.read(7)
        # check that the reply is what we're expecting
        result = resp[1:2]
        opcode = resp[2:3]
        
        version = ""

        if (result == KFDTool.READ_REPLY and opcode == KFDTool.READ_FW_VER):
            major = int.from_bytes(resp[3:4], "big")
            minor = int.from_bytes(resp[4:5], "big")
            patch = int.from_bytes(resp[5:6], "big")

            version = "{}.{}.{}".format(major, minor, patch)
        else:
            raise KFDReplyFailed("KFDTool replied with a bad code")

        return version

    def getUID(self):
        c = self._genInfoBytes(KFDTool.READ_REQ, KFDTool.READ_UID)
        self._serial.write(c)
        resp = self._serial.read(14)
        # check that the reply is what we're expecting
        result = resp[1:2]
        opcode = resp[2:3]
        
        uid = ""

        if (result == KFDTool.READ_REPLY and opcode == KFDTool.READ_UID):
            offset = 4
            for i in range(0,9):
                uidByte = resp[offset+i:offset+i+1].hex()
                uid += "{}".format(uidByte)
        else:
            raise KFDReplyFailed("KFDTool replied with a bad code")

        return uid

    def getModel(self):
        c = self._genInfoBytes(KFDTool.READ_REQ, KFDTool.READ_MODEL)
        self._serial.write(c)
        resp = self._serial.read(5)
        # check that the reply is what we're expecting
        result = resp[1:2]
        opcode = resp[2:3]

        modelId = 0

        if (result == KFDTool.READ_REPLY and opcode == KFDTool.READ_MODEL):
            modelId = int.from_bytes(resp[3:4], "big")
        else:
            raise KFDReplyFailed("KFDTool replied with a bad code")

        return modelId

    def getHwRev(self):
        c = self._genInfoBytes(KFDTool.READ_REQ, KFDTool.READ_HW_REV)
        self._serial.write(c)
        resp = self._serial.read(6)
        # check that the reply is what we're expecting
        result = resp[1:2]
        opcode = resp[2:3]

        version = ""

        if (result == KFDTool.READ_REPLY and opcode == KFDTool.READ_HW_REV):
            major = int.from_bytes(resp[3:4], "big")
            minor = int.from_bytes(resp[4:5], "big")

            version = "{}.{}".format(major, minor)
        else:
            raise KFDReplyFailed("KFDTool replied with a bad code")

        return version

    def getSerialNumber(self):
        c = self._genInfoBytes(KFDTool.READ_REQ, KFDTool.READ_SN)
        self._serial.write(c)
        resp = self._serial.read(11)
        # check that the reply is what we're expecting
        result = resp[1:2]
        opcode = resp[2:3]
        length = resp[3:4]

        serial = ""

        if (result == KFDTool.READ_REPLY and opcode == KFDTool.READ_SN):
            if (length == b'\x00'):
                #no serial number
                return None
            offset = 4
            for i in range(0,5):
                uidByte = resp[offset+i:offset+i+1].hex()
                serial += "{}".format(uidByte)
        else:
            raise KFDReplyFailed("KFDTool replied with a bad code")

        return serial

    def writeModelInfo(self, hwid, hwrevMaj, hwrevMin):
        c = self._genInfoBytes(KFDTool.WRITE_REQ, KFDTool.WRITE_MODEL, hwid, hwrevMaj, hwrevMin)
        #print("Writing bytes: {}".format(c))
        self._serial.write(c)
        resp = self._serial.read(3)
        #print("Reply: {}".format(resp))
        result = resp[1:2]
        opcode = resp[2:3]

        if (result == KFDTool.WRITE_REPLY):
            return 1
        else:
            raise KFDWriteFailed()

    def writeSerial(self, serialNum):
        c = self._genInfoBytes(KFDTool.WRITE_REQ, KFDTool.WRITE_SN, serialNum)
        #print("Writing bytes: {}".format(c))
        self._serial.write(c)
        resp = self._serial.read(3)
        #print("Reply: {}".format(resp))
        result = resp[1:2]
        opcode = resp[2:3]

        if (result == KFDTool.WRITE_REPLY):
            return 1
        else:
            raise KFDWriteFailed()

    def enterBootloader(self):
        command = KFDTool.SERIAL_HEADER + KFDTool.ENTER_BOOTLOADER + KFDTool.SERIAL_FOOTER
        self._serial.write(command)

    def reset(self):
        command = KFDTool.SERIAL_HEADER + KFDTool.RESET + KFDTool.SERIAL_FOOTER
        self._serial.write(command)

    def selfTest(self):
        command = KFDTool.SERIAL_HEADER + KFDTool.SELF_TEST + KFDTool.SERIAL_FOOTER
        self._serial.write(command)
        resp = self._serial.read(4)
        testResult = KFDSelfTestCodes(int.from_bytes(resp[2:3], "big"))
        return testResult

    def detectRadio(self):
        self._serial.flush()
        command = KFDTool.SERIAL_HEADER + KFDTool.SEND_KEY_SIG + b'\x00' + KFDTool.SERIAL_FOOTER
        self._serial.write(command)
        resp = self._serial.read(3)
        print("Resp:", resp)
        respOpcode = resp[1:2]

        if (respOpcode == b'\x26'): # keysig sent
            self._serial.flush()
            self.sendByte(P25MR.KFD_READY)
            resp = self._serial.read(3)
            print("Resp:", resp)
            respOpcode = resp[1:2]

            if (respOpcode == b'\x27'): # ready sent
                time.sleep(0.2) # wait for the buffer to fill
                resp = self._serial.read(5)
                print("Resp:", resp)
                respOpcode = resp[1:2]
                respByte = resp[3:4]
                
                if (respByte == P25MR.MR_READY):
                    return 1
                else:
                    raise KFDInvalidOpcode(resp)
            else:
                raise KFDSerialTooLong()
        else:
            raise KFDReplyFailed()
        
        # all else
        return 0


    def sendByte(self, byte):
        command = KFDTool.SERIAL_HEADER + KFDTool.SEND_BYTE + b'\x00' + byte + KFDTool.SERIAL_FOOTER
        self._serial.write(command)



    def _genInfoBytes(self, reqType, info, *args):
        command = b''
        if (reqType == KFDTool.READ_REQ):
            command = KFDTool.SERIAL_HEADER + reqType + info + KFDTool.SERIAL_FOOTER
        if (reqType == KFDTool.WRITE_REQ):
            if (info == KFDTool.WRITE_MODEL):
                hwid = int(args[0]).to_bytes(1, "big")
                hwverMin = int(args[1]).to_bytes(1, "big")
                hwverMaj = int(args[2]).to_bytes(1, "big")

                command = KFDTool.SERIAL_HEADER + reqType + info + hwid + hwverMin + hwverMaj + KFDTool.SERIAL_FOOTER
            if (info == KFDTool.WRITE_SN):
                serialString = args[0]
                #convert sn to uppercase, idk why but it gets borked sometimes if it's lower
                serialString = serialString.upper()
                #check if the wanted serial is too long
                if (len(serialString) > 6):
                    raise KFDSerialTooLong("Your serial number is too long. Try a shorter one.")
                serialBytes = serialString.encode()

                #pad the bytes out

                while (len(serialBytes) < 6):
                    serialBytes += b'\x00'

                command = KFDTool.SERIAL_HEADER + reqType + info + serialBytes + KFDTool.SERIAL_FOOTER

        return command

#basic driver/test code

def main():
    kfd = KFDTool('COM11')
    print("Adapter version: {}".format(kfd.getAdapterVer()))
    print("Firmware Version: {}".format(kfd.getFwVer()))
    print("UID: {}".format(kfd.getUID()))
    print("Model: {}".format(kfd.getModel()))
    print("Hardware Version: {}".format(kfd.getHwRev()))
    print("Serial Number: {}".format(kfd.getSerialNumber()))

if __name__ == "__main__":
    main()