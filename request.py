from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

def Get_TCP_Pose(robot_client):
    request = robot_client.read_holding_registers(0x00F0, 12, 2)  

    if request.isError():
        print("request error!")
        return

    decoder_x = BinaryPayloadDecoder.fromRegisters(request.registers[:2], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_y = BinaryPayloadDecoder.fromRegisters(request.registers[2:4], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_z = BinaryPayloadDecoder.fromRegisters(request.registers[4:6], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_rx = BinaryPayloadDecoder.fromRegisters(request.registers[6:8], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_ry = BinaryPayloadDecoder.fromRegisters(request.registers[8:10], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_rz = BinaryPayloadDecoder.fromRegisters(request.registers[10:], Endian.BIG, wordorder=Endian.LITTLE)

    x  = decoder_x.decode_32bit_int() * 0.001
    y  = decoder_y.decode_32bit_int() * 0.001
    z  = decoder_z.decode_32bit_int() * 0.001
    rx = decoder_rx.decode_32bit_int() * 0.001
    ry = decoder_ry.decode_32bit_int() * 0.001
    rz = decoder_rz.decode_32bit_int() * 0.001

    return x , y , z , rx, ry, rz

def Get_Pose_Flag(robot_client):
    request = robot_client.read_holding_registers(0x031F, 1, 2)  
    if request.isError():
        print("request error!")
        return
    pose_flag = request.registers[0]
    return pose_flag