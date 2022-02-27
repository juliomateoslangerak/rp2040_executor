import utime
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio


@asm_pio(set_init=(PIO.OUT_LOW,) * 4,
         out_init=(PIO.OUT_LOW,) * 4,
         out_shiftdir=PIO.SHIFT_RIGHT,
         in_shiftdir=PIO.SHIFT_LEFT)
def run_digitals():
    pull()
    mov(x, osr)  # num steps

    pull()
    mov(y, osr)  # step pattern

    jmp(not_x, "end")

    label("loop")
    jmp(not_osre, "step")  # loop pattern if exhausted
    mov(osr, y)

    label("step")
    out(pins, 4)[31]

    jmp(x_dec, "loop")
    label("end")

    irq(rel(0))


sm = StateMachine(1, prog=run_digitals, freq=100000)


def main():
    led = Pin(2, Pin.OUT)
    enabled = False
    while True:
        if enabled:
            led.off()
        else:
            led.on()
        utime.sleep_ms(1000)
        enabled = not enabled


if __name__ == '__main__':
    main()