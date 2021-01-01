import time


def wait():
    time.sleep(0.7)
    return

def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t

def calc_hum(rawT, rawH):
    t = -46.85 + 175.72/65536.0 * rawT
    rawH = float(int(rawH) & ~0x0003); # clear bits [1..0] (status bits)
    rh = -6.0 + 125.0/65536.0 * rawH # RH= -6 + 125 * SRH/2^16
    print(f"Hum: {rh:.1f}")


def calc_temperature(objT, ambT):
    m_tmpAmb = ambT/128.0
    Vobj2 = objT * 0.00000015625
    Tdie2 = m_tmpAmb + 273.15
    S0 = 6.4E-14            
    a1 = 1.75E-3
    a2 = -1.678E-5
    b0 = -2.94E-5
    b1 = -5.7E-7
    b2 = 4.63E-9
    c2 = 13.4
    Tref = 298.15
    S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
    Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
    fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
    tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
    tObj = (tObj - 273.15)
    print(f"Temp: {tObj:.2f} C")


tosignedbyte = lambda n: float(n-0x100) if n>0x7f else float(n)

def calc_gyro(rawX, rawY, rawZ):
    accel = lambda v: tosignedbyte(v) / 64.0  # Range -2G, +2G
    xyz = [accel(rawX), accel(rawY), accel(rawZ)]
    mag = (xyz[0]**2 + xyz[1]**2 + xyz[2]**2)**0.5
    print(f"Gyroscope: {xyz}")