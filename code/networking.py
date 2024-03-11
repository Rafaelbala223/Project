import socket
import time


# Codes for transmiting (Const)
START_GAME: int = 202
END_GAME:int = 221
RED_SCORE: int = 53
BLUE_SCORE: int = 43
BUFFER: int = 1024
# time in secs
GAME_TIME: int = 360
IP: str = "127.0.0.1"
SEND_ADDRESS = ("127.0.0.1", 7500)
RECEIEVE_ADDRESS = ("127.0.0.1", 7500)
SERVER_ADDRESS: str = "0.0.0.0"
SERVER_PORT: int = 7500
SERVER_RECEIVE_PORT: int = 7501



class Networking:
    
    def __init__(self) -> None:
        pass

    def setupSockets(self) -> bool:
        try:
            self.transmitSocket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receiveSocket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receiveSocket.bind((SERVER_ADDRESS, SERVER_RECEIVE_PORT))
            self.transmitSocket.bind((SERVER_ADDRESS, SERVER_PORT))
            return True
        except Exception as e:
            print(e)
            return False
        
    def sendData(self, data: bytes, destination: tuple) -> None:
        # Send data over the transmit socket
        self.transmitSocket.sendto(data, destination)

    def receiveData(self) -> bytes:
        # Receive data from the receive socket
        data, address = self.receiveSocket.recvfrom(BUFFER)
        return data, address
    
    def transmit_equipment_code(self, equipment_code: str) -> bool:
        # Enable broadcasts at the syscall level and priviledged process
        # Transmit equipment_code on port 7500 Send 
        try:
            self.transmitSocket.sendto(str.encode(str(equipment_code)), (SEND_ADDRESS))
            return True
        except Exception as e:
            print(e)
            return False
        
        