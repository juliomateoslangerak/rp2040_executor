import utime
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

NR_DIGITALS = 16


@asm_pio(
    # out_init=(PIO.OUT_LOW,) * NR_DIGITALS,
    out_init=PIO.OUT_LOW,

    # out_shiftdir=PIO.SHIFT_RIGHT,
         # in_shiftdir=PIO.SHIFT_LEFT,
         fifo_join=PIO.JOIN_TX
         )
def run_digitals():
    wrap_target()
    pull()
    mov(x, osr)  # num steps
    pull()

    jmp(not_x, "end")

    label("loop")
    jmp(x_dec, "loop")
    out(pins, 1)
    wrap()

    label("end")


def main():
    actions_table = [
        (1, 1),
        (100000, 0),
        (300000, 1),
        (100000, 0),
        (0, 0)
    ]
    sm = StateMachine(1, prog=run_digitals, freq=100000, set_base=Pin(25))

    while True:
        sm.active(1)
        for action in actions_table:
            sm.put(action[0])
            sm.put(action[1])

        utime.sleep(10)


if __name__ == '__main__':
    main()
