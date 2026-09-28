machine = monitor.Machine
bus = machine["sysbus"]
timer = machine['sysbus.timer2']

DMA_CCR = 0x40020008
DMA_CNDTR = 0x4002000C
DMA_CPAR = 0x40020010
DMA_CMAR = 0x40020014
DMAMUX_CCR = 0x40020800

DAC_DHR12R2 = 0x50001014

DMA_CCR_EN = 1 << 0
DMA_CCR_TCIE = 1 << 1
DMA_CCR_DIR = 1 << 4
DMA_CCR_MINC = 1 << 7
DMA_CCR_PSIZE = 1 << 8
DMA_CCR_MSIZE = 1 << 10

transfers = 0

def sonar_dma_transfer():
    global transfers

    ccr = bus.ReadDoubleWord(DMA_CCR)
    if not (ccr & DMA_CCR_EN):
        return

    dmamux = bus.ReadDoubleWord(DMAMUX_CCR)
    if (dmamux & 0xFF) != 0x67:
        return

    cndtr = bus.ReadDoubleWord(DMA_CNDTR)
    if cndtr == 0:
        return

    cmar = bus.ReadDoubleWord(DMA_CMAR)
    cpar = bus.ReadDoubleWord(DMA_CPAR)

    sample = bus.ReadWord(cmar)
    bus.WriteWord(cpar, sample)

    if ccr & DMA_CCR_MINC:
        bus.WriteDoubleWord(DMA_CMAR, cmar + 2)

    bus.WriteDoubleWord(DMA_CNDTR, cndtr - 1)

    transfers += 1

    if transfers <= 5 or transfers % 1000 == 0:
        print "SONAR DMA transfer %d: sample=%d CNDTR=%d" % (
            transfers,
            sample,
            cndtr - 1
        )

timer.LimitReached += sonar_dma_transfer

print "AUV sonar TIM2 -> DMA -> DAC bridge installed"
