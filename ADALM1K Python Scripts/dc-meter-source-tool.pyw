#!/usr/bin/python
# ADALM1000 DC volt meter / source tool Nov 18 2015
#For Python version > = 2.7.8
from Tkinter import *
import atexit
from collections import defaultdict
from operator import add
import time
import pysmu as libpysmu

# define ADALM1000 interface
class Smu(object):
    def __init__(self):
        atexit.register(libpysmu.cleanup)
        libpysmu.setup()
        self.load_channels()

    def load_channels(self):
        self.devices = libpysmu.get_dev_info()
        self.serials = {i: v[0] for i, v in enumerate(self.devices)}
        self.devices = [x[1] for x in self.devices]

        names = (chr(x) for x in xrange(65,91))
        channels = {names.next(): (i, v) for i, d in enumerate(self.devices)
                    for k, v in d.items()}
        self.channels = {k: Channel(k, self.serials[v[0]], v[1]) for k, v in channels.items()}

        device_channels = defaultdict(list)
        for k, v in channels.items():
            device_channels[v[0]].append(Channel(k, *v))
        self.devices = {i: Device(self.serials[i], device_channels[i]) for i, v
                        in enumerate(self.devices)}

    def ctrl_transfer(self, device, bm_request_type, b_request, wValue, wIndex,
                      data, wLength, timeout):
        data = str(data)
        if bm_request_type&0x80 == 0x80:
            if data == '0':
                data = '\x00'*wLength
        else:
            wLength = 0
        ret = libpysmu.ctrl_transfer(device, bm_request_type, b_request, wValue,
                                   wIndex, data, wLength, timeout)
        if bm_request_type&0x80 == 0x80:
            return map(ord, data)
        else:
            return ret

    def __repr__(self):
        return 'Devices: ' + str(self.devices)


class Device(object):
    def __init__(self, serial, channels):
        self.serial = serial
        self.channels = channels

    def get_samples(self, n_samples):
        """query device for a list of samples from all channels

        :param n_samples: number of samples
        :type n_samples: int
        :return: list of n samples from all the device's channels
        """
        return libpysmu.get_all_inputs(self.serial, n_samples)

    @property
    def samples(self):
        """iterator for samples from the device run in continuous mode"""
        return libpysmu.iterate_inputs(self.serial)


class Channel(object):
    def __init__(self, chan, dev_serial, signals):
        self.dev = dev_serial
        self.chan = ord(chan) - 65
        self.signals = {v: i for i, v in enumerate(signals)}

    def set_mode(self, mode):
        if mode == 'v' or mode == 'V':
            libpysmu.set_mode(self.dev, self.chan, 1)
            self.mode = 1
        elif mode == 'i' or mode == 'I':
            libpysmu.set_mode(self.dev, self.chan, 2)
            self.mode = 2
        elif mode == 'd' or mode == 'D':
            libpysmu.set_mode(self.dev, self.chan, 0)
            self.mode = 0
        else:
            raise ValueError('invalid mode')

    def arbitrary(self, *args, **kwargs):
        repeat = 0
        if 'repeat' in map(str.lower, kwargs.keys()):
            repeat = 1
        wave = map(float, reduce(add, [[s]*100*n for s, n in args]))
        return libpysmu.set_output_buffer(wave, self.dev, self.chan, self.mode, repeat)
    
    def get_samples(self, n_samples):
        """query channel for samples

        :param n_samples: number of samples
        :type n_samples: int
        :return: list of n samples from the channel
        """
        return libpysmu.get_inputs(self.dev, self.chan, n_samples)

    def constant(self, val):
        """set output to a constant waveform"""
        return libpysmu.set_output_constant(self.dev, self.chan, self.mode, val)

    def square(self, midpoint, peak, period, phase, duty_cycle):
        """set output to a square waveform"""
        return libpysmu.set_output_wave(self.dev, self.chan, self.mode, 1, midpoint, peak, period, phase, duty_cycle)

    def sawtooth(self, midpoint, peak, period, phase):
        """set output to a sawtooth waveform"""
        return libpysmu.set_output_wave(self.dev, self.chan, self.mode, 2, midpoint, peak, period, phase, 42)

    def stairstep(self, midpoint, peak, period, phase):
        """set output to a stairstep waveform"""
        return libpysmu.set_output_wave(self.dev, self.chan, self.mode, 3, midpoint, peak, period, phase, 42)

    def sine(self, midpoint, peak, period, phase):
        """set output to a sinusoidal waveform"""
        return libpysmu.set_output_wave(self.dev, self.chan, self.mode, 4, midpoint, peak, period, phase, 42)

    def triangle(self, midpoint, peak, period, phase):
        """set output to a triangle waveform"""
        return libpysmu.set_output_wave(self.dev, self.chan, self.mode, 5, midpoint, peak, period, phase, 42)

    def __repr__(self):
        return 'Device: ' + str(self.dev) + '\nChannel: ' + str(self.chan) + '\nSignals: ' + str(self.signals)
# define button actions
def Analog_in():

    while (True):       # Main loop
        if RUNstatus.get() == 1:
            #
            try:
                InOffA = float(eval(CHAVOffsetEntry.get()))
            except:
                CHAVOffsetEntry.delete(0,END)
                CHAVOffsetEntry.insert(0, InOffA)
            try:
                InGainA = float(eval(CHAVGainEntry.get()))
            except:
                CHAVGainEntry.delete(0,END)
                CHAVGainEntry.insert(0, InGainA)
            try:
                InOffB = float(eval(CHBVOffsetEntry.get()))
            except:
                CHBVOffsetEntry.delete(0,END)
                CHBVOffsetEntry.insert(0, InOffB)
            try:
                InGainB = float(eval(CHBVGainEntry.get()))
            except:
                CHBVGainEntry.delete(0,END)
                CHBVGainEntry.insert(0, InGainB)
            #
            try:
                CurOffA = float(eval(CHAIOffsetEntry.get()))
            except:
                CHAIOffsetEntry.delete(0,END)
                CHAIOffsetEntry.insert(0, CurOffA)
            try:
                CurGainA = float(eval(CHAIGainEntry.get()))
            except:
                CHAIGainEntry.delete(0,END)
                CHAIGainEntry.insert(0, CurGainA)
            try:
                CurOffB = float(eval(CHBIOffsetEntry.get()))
            except:
                CHBIOffsetEntry.delete(0,END)
                CHBIOffsetEntry.insert(0, CurOffB)
            try:
                CurGainB = float(eval(CHBIGainEntry.get()))
            except:
                CHBIGainEntry.delete(0,END)
                CHBIGainEntry.insert(0, CurGainB)
            #
            try:
                chatestv = float(eval(CHATestVEntry.get()))
            except:
                CHATestVEntry.delete(0,END)
                CHATestVEntry.insert(0, chatestv)
            try:
                chbtestv = float(eval(CHBTestVEntry.get()))
            except:
                CHBTestVEntry.delete(0,END)
                CHBTestVEntry.insert(0, chbtestv)
            try:
                chatesti = float(eval(CHATestIEntry.get()))/1000
            except:
                CHATestIEntry.delete(0,END)
                CHATestIEntry.insert(0, chatesti*1000)
            try:
                chbtesti = float(eval(CHBTestIEntry.get()))/1000
            except:
                CHBTestIEntry.delete(0,END)
                CHBTestIEntry.insert(0, chbtesti*1000)
            # 
            DCVA0 = DCVB0 = DCIA0 = DCIB0 = 0.0 # initalize measurment variable
            # Get A0 and B0 data
            if CHAstatus.get() == 0:
                CHA.set_mode('d')
            else:
                if CHAmode.get() == 0:
                    CHA.set_mode('v')
                    CHA.constant(chatestv)
                else:
                    CHA.set_mode('i')
                    CHA.constant(chatesti)
            if CHBstatus.get() == 0:
                CHB.set_mode('d')
            else:
                if CHBmode.get() == 0:
                    CHB.set_mode('v')
                    CHB.constant(chbtestv)
                else:
                    CHB.set_mode('i')
                    CHB.constant(chbtesti)
            ADsignal1 = Both.get_samples(210) # get samples for both channel A0 and B0
            # get_samples returns a list of values for voltage [0] and current [1]
            for index in range(200): # calculate average
                SPA = ADsignal1[0][index+10] # skip over first 10 readings
                SPB = ADsignal1[1][index+10]
                VAdata = (float(SPA[0]) - InOffA) * InGainA
                VBdata = (float(SPB[0]) - InOffB) * InGainB
                IAdata = ((float(SPA[1])*1000) - CurOffA) * CurGainA
                IBdata = ((float(SPB[1])*1000) - CurOffB) * CurGainB
                DCVA0 += VAdata # Sum for average CA voltage 
                DCVB0 += VBdata # Sum for average CB voltage
                DCIA0 += IAdata # Sum for average CA current 
                DCIB0 += IBdata # Sum for average CB current

            DCVA0 = DCVA0 / 200.0 # calculate average
            DCVB0 = DCVB0 / 200.0 # calculate average
            DCIA0 = DCIA0 / 200.0 # calculate average
            DCIB0 = DCIB0 / 200.0 # calculate average
            VAString = "CA V " + ' {0:.4f} '.format(DCVA0) # format with 4 decimal places
            VBString = "CB V " + ' {0:.4f} '.format(DCVB0) # format with 4 decimal places
            labelA0.config(text = VAString) # change displayed value
            labelB0.config(text = VBString) # change displayed value
            if CHAstatus.get() == 0:
                IAString = "CA mA ----"
            else:
                IAString = "CA mA " + ' {0:.2f} '.format(DCIA0)
            if CHBstatus.get() == 0:
                IBString = "CB mA ----"
            else:
                IBString = "CB mA " + ' {0:.2f} '.format(DCIB0)
            
            labelAI.config(text = IAString) # change displayed value
            labelBI.config(text = IBString) # change displayed value

#
            time.sleep(0.2)
    # Update tasks and screens by TKinter
        root.update_idletasks()
        root.update()            
def BSaveCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global DevID

    devidstr = DevID[17:31]
    filename = devidstr + "_O.cal"
    CalFile = open(filename, "w")
    #
    CalFile.write('CHAVGainEntry.delete(0,END)\n')
    CalFile.write('CHAVGainEntry.insert(4, ' + CHAVGainEntry.get() + ')\n')
    CalFile.write('CHBVGainEntry.delete(0,END)\n')
    CalFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
    CalFile.write('CHAVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAVOffsetEntry.insert(4, ' + CHAVOffsetEntry.get() + ')\n')
    CalFile.write('CHBVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')
    #
    CalFile.write('CHAIGainEntry.delete(0,END)\n')
    CalFile.write('CHAIGainEntry.insert(4, ' + CHAIGainEntry.get() + ')\n')
    CalFile.write('CHBIGainEntry.delete(0,END)\n')
    CalFile.write('CHBIGainEntry.insert(4, ' + CHBIGainEntry.get() + ')\n')
    CalFile.write('CHAIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAIOffsetEntry.insert(4, ' + CHAIOffsetEntry.get() + ')\n')
    CalFile.write('CHBIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBIOffsetEntry.insert(4, ' + CHBIOffsetEntry.get() + ')\n')
    #
    CalFile.close()

def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global DevID

    devidstr = DevID[17:31]
    filename = devidstr + "_O.cal"
    try:
        CalFile = open(filename)
        for line in CalFile:
            exec( line.rstrip() )
        CalFile.close()
    except:
        print("Cal file for this device not found")
    
# setup main window
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root = Tk()
root.title("ALM1000 Meter-Source (11-18-2015)")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, img)
#
RUNstatus = IntVar(0)
CHAstatus = IntVar(0)
CHBstatus = IntVar(0)
CHAmode = IntVar(0)
CHBmode = IntVar(0)
#
buttons = Frame( root )
buttons.grid(row=0, column=0, columnspan=2, sticky=W)
rb1 = Radiobutton(buttons, text="Stop", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", variable=RUNstatus, value=1 )
rb2.pack(side=LEFT)
b1 = Button(buttons, text='Save', command=BSaveCal)
b1.pack(side=LEFT)
b2 = Button(buttons, text='Load', command=BLoadCal)
b2.pack(side=LEFT)
#
frame1 = Frame(root, borderwidth=5, relief=RIDGE)
frame1.grid(row=1, column=0, sticky=W) # 
frame2 = Frame(root, borderwidth=5, relief=RIDGE)
frame2.grid(row=1, column=1, sticky=W) # 
frame3 = Frame(root, borderwidth=5, relief=RIDGE)
frame3.grid(row=1, column=2, sticky=W) # 
frame4 = Frame(root, borderwidth=5, relief=RIDGE)
frame4.grid(row=1, column=3, sticky=W) # 
#
labelAV = Label(frame1, font = "Arial 16 bold")
labelAV.grid(row=0, column=0, columnspan=2, sticky=W)
labelAV.config(text = "CA Meter")

labelA0 = Label(frame1, font = "Arial 16 bold")
labelA0.grid(row=1, column=0, columnspan=2, sticky=W)
labelA0.config(text = "CA-V 0.0000")

labelAI = Label(frame1, font = "Arial 16 bold")
labelAI.grid(row=2, column=0, columnspan=2, sticky=W)
labelAI.config(text = "CA-I 0.00")
# input probe wigets
calAlab = Label(frame1, text="CH A Gain/Offset calibration")
calAlab.grid(row=3, column=0, sticky=W)
# Input Probes sub frame 
ProbeAV = Frame( frame1 )
ProbeAV.grid(row=4, column=0, sticky=W)
gainavlab = Label(ProbeAV, text="VA")
gainavlab.pack(side=LEFT)
CHAVGainEntry = Entry(ProbeAV, width=6) #
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,1.0)
CHAVOffsetEntry = Entry(ProbeAV, width=6) # 
CHAVOffsetEntry.pack(side=LEFT)
CHAVOffsetEntry.delete(0,"end")
CHAVOffsetEntry.insert(0,0.0)
#
ProbeAI = Frame( frame1 )
ProbeAI.grid(row=5, column=0, sticky=W)
gainailab = Label(ProbeAI, text=" IA ")
gainailab.pack(side=LEFT)
CHAIGainEntry = Entry(ProbeAI, width=6) #
CHAIGainEntry.pack(side=LEFT)
CHAIGainEntry.delete(0,"end")
CHAIGainEntry.insert(0,1.0)
CHAIOffsetEntry = Entry(ProbeAI, width=6) # 
CHAIOffsetEntry.pack(side=LEFT)
CHAIOffsetEntry.delete(0,"end")
CHAIOffsetEntry.insert(0,0.0)
#
labelAV = Label(frame2, font = "Arial 16 bold")
labelAV.grid(row=0, column=0, columnspan=2, sticky=W)
labelAV.config(text = "CB Meter")

labelB0 = Label(frame2, font = "Arial 16 bold")
labelB0.grid(row=1, column=0, columnspan=2, sticky=W)
labelB0.config(text = "CB-V 0.0000")

labelBI = Label(frame2, font = "Arial 16 bold")
labelBI.grid(row=2, column=0, columnspan=2, sticky=W)
labelBI.config(text = "CB-I 0.00")
# input probe wigets
calBlab = Label(frame2, text="CH B Gain/Offset calibration")
calBlab.grid(row=3, column=0, sticky=W)
#
ProbeBV = Frame( frame2 )
ProbeBV.grid(row=4, column=0, sticky=W)
gainbvlab = Label(ProbeBV, text="VB")
gainbvlab.pack(side=LEFT)
CHBVGainEntry = Entry(ProbeBV, width=6) # )
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,1.0)
CHBVOffsetEntry = Entry(ProbeBV, width=6) # 
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,0.0)
#
ProbeBI = Frame( frame2 )
ProbeBI.grid(row=5, column=0, sticky=W)
gainbilab = Label(ProbeBI, text=" IB ")
gainbilab.pack(side=LEFT)
CHBIGainEntry = Entry(ProbeBI, width=6) # )
CHBIGainEntry.pack(side=LEFT)
CHBIGainEntry.delete(0,"end")
CHBIGainEntry.insert(0,1.0)
CHBIOffsetEntry = Entry(ProbeBI, width=6) # 
CHBIOffsetEntry.pack(side=LEFT)
CHBIOffsetEntry.delete(0,"end")
CHBIOffsetEntry.insert(0,0.0)
#
labelAS = Label(frame3, font = "Arial 16 bold")
labelAS.grid(row=0, column=0, columnspan=2, sticky=W)
labelAS.config(text = "CA Source")

chaonbutton = Frame( frame3 )
chaonbutton.grid(row=1, column=0, columnspan=2, sticky=W)
rbaoff = Radiobutton(chaonbutton, text="CHA off", variable=CHAstatus, value=0 )
rbaoff.pack(side=LEFT)
rbaon = Radiobutton(chaonbutton, text="CHA on", variable=CHAstatus, value=1 )
rbaon.pack(side=LEFT)

chaivbutton = Frame( frame3 )
chaivbutton.grid(row=2, column=0, columnspan=2, sticky=W)
rbav = Radiobutton(chaivbutton, text="CHA V", variable=CHAmode, value=0 )
rbav.pack(side=LEFT)
rbai = Radiobutton(chaivbutton, text="CHA I", variable=CHAmode, value=1 )
rbai.pack(side=LEFT)

TestVA = Frame( frame3 )
TestVA.grid(row=3, column=0, sticky=W)
chatestvlab = Label(TestVA, text="CA-V")
chatestvlab.pack(side=LEFT)
CHATestVEntry = Entry(TestVA, width=6) #
CHATestVEntry.pack(side=LEFT)
CHATestVEntry.delete(0,"end")
CHATestVEntry.insert(0,0.0)

TestIA = Frame( frame3 )
TestIA.grid(row=4, column=0, sticky=W)
chatestilab = Label(TestIA, text="CA-I")
chatestilab.pack(side=LEFT)
CHATestIEntry = Entry(TestIA, width=6) #
CHATestIEntry.pack(side=LEFT)
CHATestIEntry.delete(0,"end")
CHATestIEntry.insert(0,0.0)
#
labelBS = Label(frame4, font = "Arial 16 bold")
labelBS.grid(row=0, column=0, columnspan=2, sticky=W)
labelBS.config(text = "CB Source")

chbonbutton = Frame( frame4 )
chbonbutton.grid(row=1, column=0, columnspan=2, sticky=W)
rbboff = Radiobutton(chbonbutton, text="CHB off", variable=CHBstatus, value=0 )
rbboff.pack(side=LEFT)
rbbon = Radiobutton(chbonbutton, text="CHB on", variable=CHBstatus, value=1 )
rbbon.pack(side=LEFT)

chbivbutton = Frame( frame4 )
chbivbutton.grid(row=2, column=0, columnspan=2, sticky=W)
rbbv = Radiobutton(chbivbutton, text="CHB V", variable=CHBmode, value=0 )
rbbv.pack(side=LEFT)
rbbi = Radiobutton(chbivbutton, text="CHB I", variable=CHBmode, value=1 )
rbbi.pack(side=LEFT)

TestVB = Frame( frame4 )
TestVB.grid(row=3, column=0, sticky=W)
chbtestvlab = Label(TestVB, text="CB-V")
chbtestvlab.pack(side=LEFT)
CHBTestVEntry = Entry(TestVB, width=6) #
CHBTestVEntry.pack(side=LEFT)
CHBTestVEntry.delete(0,"end")
CHBTestVEntry.insert(0,0.0)

TestIB = Frame( frame4 )
TestIB.grid(row=4, column=0, sticky=W)
chbtestilab = Label(TestIB, text="CB-I")
chbtestilab.pack(side=LEFT)
CHBTestIEntry = Entry(TestIB, width=6) #
CHBTestIEntry.pack(side=LEFT)
CHBTestIEntry.delete(0,"end")
CHBTestIEntry.insert(0,0.0)

# Setup ADAML1000
devx = Smu()
DevID = devx.serials[0]
print(DevID)
CHA = devx.channels['A']    # Open CHA
CHA.set_mode('d')           # Put CHA in Hi Z mode
CHB = devx.channels['B']    # Open CHB
CHB.set_mode('d')           # Put CHB in Hi Z mode
Both = devx.devices[0]
ADsignal1 = []              # Ain signal array channel
# start main loop
root.update()
# Start sampling
Analog_in()
#
