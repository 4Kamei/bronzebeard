# Echo characters over serial USART (requires a USB to TTL serial cable)

CLOCK_FREQ = 8000000  # default GD32BF103 clock freq
USART_BAUD = 115200   # desired USART baud rate

RCU_BASE_ADDR     = 0x40021000  # GD32VF103 Manual: Section 5.3
RCU_APB2EN_OFFSET = 0x18  # GD32VF103 Manual: Section 5.3.7

GPIO_BASE_ADDR_A = 0x40010800  # GD32VF103 Manual: Section 7.5 (green and blue LEDs)
GPIO_CTL0_OFFSET = 0x00  # GD32VF103 Manual: Section 7.5.1 (pins 0-7)
GPIO_CTL1_OFFSET = 0x04  # GD32VF103 Manual: Section 7.5.2 (pins 8-15)

# GD32VF103 Manual: Section 7.3
GPIO_MODE_IN        = 0b00
GPIO_MODE_OUT_50MHZ = 0b11

# GD32VF103 Manual: Section 7.3
GPIO_CTL_IN_FLOATING       = 0b01
GPIO_CTL_OUT_ALT_PUSH_PULL = 0b10

USART_BASE_ADDR_0 = 0x40013800  # GD32VF103 Manual: Section 16.4
USART_STAT_OFFSET = 0x00  # GD32VF103 Manual: Section 16.4.1
USART_DATA_OFFSET = 0x04  # GD32VF103 Manual: Section 16.4.2
USART_BAUD_OFFSET = 0x08  # GD32VF103 Manual: Section 16.4.3
USART_CTL0_OFFSET = 0x0c  # GD32VF103 Manual: Section 16.4.4


# jump to "main" since programs execute top to bottom
# we do this to enable writing helper funcs at the top
j main


# Func: rcu_init
# Arg: a0 = RCU base addr
# Arg: a1 = RCU config
# Ret: none
rcu_init:
    # store config
    sw a1, RCU_APB2EN_OFFSET(a0)

    ret


# Func: gpio_init
# Arg: a0 = GPIO port base addr
# Arg: a1 = GPIO pin number
# Arg: a2 = GPIO config (4 bits)
# Ret: none
gpio_init:
    # advance to CTL0
    addi t0, a0, GPIO_CTL0_OFFSET

    # if pin number is less than 8, CTL0 is correct
    slti t1, a1, 8
    bnez t1, gpio_init_config

    # else we need CTL1 and then subtract 8 from the pin number
    addi t0, t0, 4
    addi a1, a1, -8

gpio_init_config:
    # multiply pin number by 4 to get shift amount
    addi t1, zero, 4
    mul a1, a1, t1

    # load current config
    lw t1, 0(t0)

    # align and clear existing pin config
    li t2, 0b1111
    sll t2, t2, a1
    not t2, t2
    and t1, t1, t2

    # align and apply new pin config
    sll a2, a2, a1
    or t1, t1, a2

    # store updated config
    sw t1, 0(t0)

    ret


# Func: usart_init
# Arg: a0 = USART base addr
# Arg: a1 = USART clkdiv
# Ret: none
usart_init:
    # store clkdiv
    sw a1, USART_BAUD_OFFSET(a0)

    # enable USART (enable RX, enable TX, enable USART)
    li t0, 0b0010000000001100
    sw t0, USART_CTL0_OFFSET(a0)

    ret


# Func: getc
# Arg: a0 = USART base addr
# Ret: a1 = character received (a1 here for simpler getc + putc loops)
getc:
    lw t0 USART_STAT_OFFSET(a0)  # load status into t0
    andi t0 t0 (1 << 5)          # isolate read buffer not empty (RBNE) bit
    beqz t0 getc                 # keep looping until ready to recv
    lw a1 USART_DATA_OFFSET(a0)  # load char into a1

    ret


# Func: putc
# Arg: a0 = USART base addr
# Arg: a1 = character to send
# Ret: none
putc:
    lw t0 USART_STAT_OFFSET(a0)  # load status into t0
    andi t0 t0 (1 << 7)          # isolate transmit buffer empty (TBE) bit
    beqz t0 putc                 # keep looping until ready to send
    sw a1 USART_DATA_OFFSET(a0)  # write char from a1

    ret


main:
    # enable RCU (AFIO, GPIO port A, and USART0)
    li a0, RCU_BASE_ADDR
    li a1, 0b0100000000000101
    call rcu_init

    # enable TX pin
    li a0, GPIO_BASE_ADDR_A
    li a1, 9
    li a2, (GPIO_CTL_OUT_ALT_PUSH_PULL << 2 | GPIO_MODE_OUT_50MHZ)
    call gpio_init

    # enable RX pin
    li a0, GPIO_BASE_ADDR_A
    li a1, 10
    li a2, (GPIO_CTL_IN_FLOATING << 2 | GPIO_MODE_IN)
    call gpio_init

    # enable USART0
    li a0, USART_BASE_ADDR_0
    li a1, (CLOCK_FREQ // USART_BAUD)
    call usart_init

# main loop (read a char, write a char, repeat)
loop:
    li a0, USART_BASE_ADDR_0
    call getc
    call putc
    j loop
