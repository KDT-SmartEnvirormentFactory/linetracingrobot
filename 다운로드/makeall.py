import time
import lgpio

from motor_l9110s import L9110SMotor      # 네가 만든 모터 클래스 파일/이름 그대로
from TCRT_5000 import TCRT5000  # 센서 클래스

h = lgpio.gpiochip_open(0)

# 센서(GPIO)
L_IR_GPIO = 22
R_IR_GPIO = 23

# 모터(GPIO) - L9110S
L_MA = 18
L_MB = 19
R_MA = 12
R_MB = 13

L_IR = TCRT5000(h, L_IR_GPIO)
R_IR = TCRT5000(h, R_IR_GPIO)

Lm = L9110SMotor(h, L_MA, L_MB, pwm_hz=500)
Rm = L9110SMotor(h, R_MA, R_MB, pwm_hz=500)

BASE = 15      # 기본 속도(0~100)
TURN = 10      # 회전 보정(0~100)
LOOP_DT = 0.01

def drive(left_speed, right_speed):
    # forward만 사용(라인트레이서 기본)
    if left_speed <= 0:
        Lm.stop()
    else:
        Lm.forward(left_speed)

    if right_speed <= 0:
        Rm.stop()
    else:
        Rm.forward(right_speed)

try:
    while True:
        l = L_IR.read()
        r = R_IR.read()

        # 센서 논리: 네 아두이노 예제 그대로(0,0 전진 / 1,0 좌 / 0,1 우 / 1,1 정지)
        if l == 0 and r == 0:
            drive(BASE, BASE)
        elif l == 1 and r == 0:
            drive(0, min(100, BASE + TURN))
        elif l == 0 and r == 1:
            drive(min(100, BASE + TURN), 0)
        else:
            drive(0, 0)

        time.sleep(LOOP_DT)

finally:
    Lm.stop()
    Rm.stop()
    lgpio.gpiochip_close(h)

