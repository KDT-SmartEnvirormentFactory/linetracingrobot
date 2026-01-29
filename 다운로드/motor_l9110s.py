# motor_l9110s.py
import time
import lgpio

class L9110SMotor:
    """
    L9110S 1모터 제어 클래스 (Pi5 + lgpio)
    - forward(speed):  0~100
    - backward(speed): 0~100
    - stop()
    특징:
    - kick(출발 보조)는 '정지 -> 출발' 상태에서만 1회 수행
    - 루프에서 forward()를 계속 호출해도 kick이 반복되지 않음
    """

    def __init__(self, handle, pin_a, pin_b, pwm_hz=500, kick_duty=100, kick_sec=0.05):
        self.h = handle
        self.a = pin_a
        self.b = pin_b
        self.pwm_hz = pwm_hz

        self.kick_duty = kick_duty
        self.kick_sec = kick_sec

        lgpio.gpio_claim_output(self.h, self.a, 0)
        lgpio.gpio_claim_output(self.h, self.b, 0)

        self._moving = False
        self._dir = None  # "F" or "B"

    def _clip(self, v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    def _pwm(self, pin, duty):  # duty: 0~100
        duty = self._clip(duty, 0, 100)
        lgpio.tx_pwm(self.h, pin, self.pwm_hz, duty)  # duty=0 => 출력 0%

    def stop(self):
        # 두 입력 확실히 0
        self._pwm(self.a, 0)
        self._pwm(self.b, 0)
        lgpio.gpio_write(self.h, self.a, 0)
        lgpio.gpio_write(self.h, self.b, 0)

        self._moving = False
        self._dir = None

    def _kick_if_needed(self, direction):
        # 정지 상태에서만 킥 1회
        if self._moving:
            return
        if self.kick_sec <= 0 or self.kick_duty <= 0:
            return

        try:
            if direction == "F":
                # a LOW, b kick PWM
                self._pwm(self.a, 0)
                lgpio.gpio_write(self.h, self.a, 0)
                self._pwm(self.b, self.kick_duty)
            else:
                # b LOW, a kick PWM
                self._pwm(self.b, 0)
                lgpio.gpio_write(self.h, self.b, 0)
                self._pwm(self.a, self.kick_duty)

            time.sleep(self.kick_sec)
        except KeyboardInterrupt:
            self.stop()
            raise

    def forward(self, speed):  # speed: 0~100
        speed = self._clip(speed, 0, 100)
        if speed == 0:
            self.stop()
            return

        # 방향 전환이면 정지 후 재출발(킥 1회 가능)
        if self._dir == "B":
            self.stop()

        self._kick_if_needed("F")

        # steady: a LOW, b PWM(speed)
        self._pwm(self.a, 0)
        lgpio.gpio_write(self.h, self.a, 0)
        self._pwm(self.b, speed)

        self._moving = True
        self._dir = "F"

    def backward(self, speed):  # speed: 0~100
        speed = self._clip(speed, 0, 100)
        if speed == 0:
            self.stop()
            return

        if self._dir == "F":
            self.stop()

        self._kick_if_needed("B")

        # steady: b LOW, a PWM(speed)
        self._pwm(self.b, 0)
        lgpio.gpio_write(self.h, self.b, 0)
        self._pwm(self.a, speed)

        self._moving = True
        self._dir = "B"

