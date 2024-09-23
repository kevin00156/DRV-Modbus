from enum import Enum

class eRobotCommand(Enum):
    # JOG function commands (1~12: External Axis 1+, Axis 1-…Axis 6+, Axis 6-)
    External_Axis_1_Positive = 1
    External_Axis_1_Negative = 2
    External_Axis_2_Positive = 3
    External_Axis_2_Negative = 4
    External_Axis_3_Positive = 5
    External_Axis_3_Negative = 6
    External_Axis_4_Positive = 7
    External_Axis_4_Negative = 8
    External_Axis_5_Positive = 9
    External_Axis_5_Negative = 10
    External_Axis_6_Positive = 11
    External_Axis_6_Negative = 12
    
    # (25~32: Robot J1+, J1-…J4+, J4-)
    Robot_J1_Positive = 25
    Robot_J1_Negative = 26
    Robot_J2_Positive = 27
    Robot_J2_Negative = 28
    Robot_J3_Positive = 29
    Robot_J3_Negative = 30
    Robot_J4_Positive = 31
    Robot_J4_Negative = 32
    
    # (201~212: X+, X-, Y+, Y-, Z+, Z-, RX+, RX-, RY+, RY-, RZ+…)
    X_Positive = 201
    X_Negative = 202
    Y_Positive = 203
    Y_Negative = 204
    Z_Positive = 205
    Z_Negative = 206
    RX_Positive = 207
    RX_Negative = 208
    RY_Positive = 209
    RY_Negative = 210
    RZ_Positive = 211
    RZ_Negative = 212
    
    # (401~412: External Axis 1+, Axis 1-... Axis 6+...=>Continue_JOG)
    Continue_JOG_External_Axis_1_Positive = 401
    Continue_JOG_External_Axis_1_Negative = 402
    Continue_JOG_External_Axis_2_Positive = 403
    Continue_JOG_External_Axis_2_Negative = 404
    Continue_JOG_External_Axis_3_Positive = 405
    Continue_JOG_External_Axis_3_Negative = 406
    Continue_JOG_External_Axis_4_Positive = 407
    Continue_JOG_External_Axis_4_Negative = 408
    Continue_JOG_External_Axis_5_Positive = 409
    Continue_JOG_External_Axis_5_Negative = 410
    Continue_JOG_External_Axis_6_Positive = 411
    Continue_JOG_External_Axis_6_Negative = 412
    
    # (425~432: J1+, J1-...J4+,J4- => Continue_JOG)
    Continue_JOG_Robot_J1_Positive = 425
    Continue_JOG_Robot_J1_Negative = 426
    Continue_JOG_Robot_J2_Positive = 427
    Continue_JOG_Robot_J2_Negative = 428
    Continue_JOG_Robot_J3_Positive = 429
    Continue_JOG_Robot_J3_Negative = 430
    Continue_JOG_Robot_J4_Positive = 431
    Continue_JOG_Robot_J4_Negative = 432
    
    # (601~612: X+, X-, Y+, Y-, Z+, Z-, RX+, RX-, RY+, RY-, RZ+... => Continue_JOG)
    Continue_JOG_X_Positive = 601
    Continue_JOG_X_Negative = 602
    Continue_JOG_Y_Positive = 603
    Continue_JOG_Y_Negative = 604
    Continue_JOG_Z_Positive = 605
    Continue_JOG_Z_Negative = 606
    Continue_JOG_RX_Positive = 607
    Continue_JOG_RX_Negative = 608
    Continue_JOG_RY_Positive = 609
    Continue_JOG_RY_Negative = 610
    Continue_JOG_RZ_Positive = 611
    Continue_JOG_RZ_Negative = 612
    
    # (1400: Robot homing to mechanical origin in Z->RZ->Y->X sequence)
    Robot_Homing_To_Origin_Z_RZ_Y_X = 1400
    
    # (1401~1411: Robot and external axis homing to mechanical origin)
    Robot_J1_Homing_To_Origin = 1401
    Robot_J2_Homing_To_Origin = 1402
    Robot_J3_Homing_To_Origin = 1403
    Robot_J4_Homing_To_Origin = 1404
    Robot_All_Joints_Homing_To_Origin = 1405
    External_Axis_1_Homing_To_Origin = 1406
    External_Axis_2_Homing_To_Origin = 1407
    External_Axis_3_Homing_To_Origin = 1408
    External_Axis_4_Homing_To_Origin = 1409
    External_Axis_5_Homing_To_Origin = 1410
    External_Axis_6_Homing_To_Origin = 1411
    
    # (301~307: Robot movement commands)
    Robot_Go_MovP = 301
    Robot_Go_MovL = 302
    Robot_Go_MultiMoveJ = 305
    Robot_Go_MArchP = 306
    Robot_Go_MArchL = 307
    
    # (312~321: J1, J2... J4 and external axes Goto commands)
    Robot_J1_Goto = 312
    Robot_J2_Goto = 313
    Robot_J3_Goto = 314
    Robot_J4_Goto = 315
    External_Axis_1_Goto = 316
    External_Axis_2_Goto = 317
    External_Axis_3_Goto = 318
    External_Axis_4_Goto = 319
    External_Axis_5_Goto = 320
    External_Axis_6_Goto = 321
    
    # (1000: Motion Stop)
    Motion_Stop = 1000
