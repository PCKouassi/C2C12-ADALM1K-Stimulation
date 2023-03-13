from pysmu import Session

session = Session()
devx = session.devices[0]
print(devx.serial)

if not session.devices:
    print ('no device found')
    exit()
#
devx = session.devices[0]


# assign digital pins
PIO_0 = 28
PIO_1 = 29
PIO_2 = 47
PIO_3 = 3 
# set PIO0 low
devx.ctrl_transfer(0x40, 0x50, PIO_0, 0, 0, 0, 100)

# To set a pin to output a high ( logic 1 ):
# set PIO1 high
devx.ctrl_transfer(0x40, 0x51, PIO_1, 0, 0, 0, 100)