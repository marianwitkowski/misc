import pexpect
from ti_utils import *


# scan BT modules with command hcitool lescan for obtain sensor tag's MAC ADDRESS
MAC_ADDRESS = "BC:6A:29:C3:33:11"

TIMEOUT = 60

###############################################
print("open gatttool console...")
con = pexpect.spawn(f'/usr/bin/gatttool -b {MAC_ADDRESS} --interactive')
con.expect('\[LE\]>', timeout=TIMEOUT)

print(f"connect to {MAC_ADDRESS}...")
con.sendline('connect')
con.expect('\[LE\]>', timeout=TIMEOUT)
wait()

###############################################
print("="*60)
print(f"activate temp detector...")
con.sendline('char-write-cmd 0x29 01')
con.expect('\[LE\]>', timeout=TIMEOUT)
wait()

con.sendline('char-write-cmd 0x26 0100')
con.expect('\[LE\]>', timeout=TIMEOUT)
wait()

###############################################
print("="*60)
print(f"activate humidity detector...")
con.sendline('char-write-cmd 0x3C 01')
con.expect('\[LE\]>', timeout=TIMEOUT)
wait()

###############################################
print("="*60)
print(f"activate gyroscope detector...")
con.sendline('char-write-cmd 0x5B 07')
con.expect('\[LE\]>', timeout=TIMEOUT)
wait()

con.sendline('char-write-cmd 0x58 0100')
con.expect('\[LE\]>', timeout=TIMEOUT)
wait()

###############################################
while True:
    print("="*60)
    print(f"read temperature...")
    con.sendline('char-read-hnd 0x25')
    con.expect('descriptor: .*? \r', timeout=TIMEOUT)
    values = con.after.decode("utf-8").split()
    objT, ambT = floatfromhex(values[2] + values[1]) , floatfromhex(values[4] + values[3])
    calc_temperature(objT, ambT)
    print()

    print(f"read humidity...")
    con.sendline('char-read-hnd 0x38')
    con.expect('descriptor: .*? \r', timeout=TIMEOUT)
    values = con.after.decode("utf-8").split()
    tmpT, humT = floatfromhex(values[2] + values[1]), floatfromhex(values[4] + values[3])
    calc_hum(tmpT, humT)
    print()


    print(f"read gyroscope...")
    con.sendline('char-read-hnd 0x57')
    con.expect('descriptor: .*? \r', timeout=TIMEOUT)
    values = con.after.decode("utf-8").split()
    x, y, z = floatfromhex(values[2] + values[1]), floatfromhex(values[4] + values[3]), floatfromhex(values[6] + values[5])
    print(values)
    calc_gyro(x, y, z)

    time.sleep(5)