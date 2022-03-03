from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep


@asm_pio(
         # set_init=PIO.OUT_LOW,
         out_init=(PIO.OUT_LOW,) * 32,
         out_shiftdir=PIO.SHIFT_LEFT,
         fifo_join=PIO.JOIN_TX,
)
def prog():
    wrap_target()
    pull()
    mov(x, osr)
    jmp(not_x, 'end')
    pull()
    out(pins, 32)
    label('loop')
    jmp(x_dec, 'loop')
    wrap()
    label('end')
    mov(pins, null)


sm = StateMachine(1, prog, freq=2000, out_base=Pin(0))

sm.active(1)
for _ in range(3):
    sm.put(1000)
    sm.put(0b00000010000000000000000000000001)  # 1000 0100 0010 0001 1000010000100001
    sm.put(1000)
    sm.put(0b00000000000000000000000000000000)  # 1000 0100 0010 0001 1000010000100001
    sm.put(1000)
    sm.put(0b00000010000000000000000000000001)  # 1000 0100 0010 0001 1000010000100001
    sm.put(1000)
    sm.put(0b00000000000000000000000000000000)  # 1000 0100 0010 0001 1000010000100001
    sm.put(0)
    sm.put(0b00000000000000000000000000000000)  # 1000 0100 0010 0001 1000010000100001
sleep(20)
sm.active(0)
