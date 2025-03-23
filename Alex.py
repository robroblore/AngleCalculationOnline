import math as m
import matplotlib.pyplot as plt
import time
import multiprocessing


def g(h):
    """Return gravity."""
    Gc = 6.6743 * (10 ** -11)  # Gravitational constant [m^3/(kg*s^2)]
    Er = 6371000  # Earth radius [m]
    Em = 5.972 * (10 ** 24)  # Earth mass [kg]
    return (Gc * Em) / ((h + Er) ** 2)


def T(h, T0=288.15):
    """Return temperature."""
    if h <= 11000:  # Troposphere
        Lr = -0.0065  # Temperature lapse rate [k/m]
        return T0 + h * Lr
    elif h <= 20000:  # Tropopause
        Lr = 0
        BT = 216.65  # Base temperature for this layer  [k]
        return BT + h * Lr
    elif h <= 32000:  # Stratosphere
        Lr = 0.001
        BT = 216.65
        return BT + (h - 20000) * Lr
    elif h <= 47000:  # Stratosphere
        Lr = 0.0028
        BT = 228.65
        return BT + (h - 32000) * Lr
    elif h <= 51000:  # Stratopause
        Lr = 0
        BT = 270.65
        return BT + (h - 47000) * Lr
    elif h <= 71000:  # Mesosphere
        Lr = -0.0028
        BT = 270.65
        return BT + (h - 51000) * Lr
    elif h <= 86000:  # Mesosphere
        Lr = -0.002
        BT = 214.65
        return BT + (h - 71000) * Lr
    return 0


def p(h):
    """Return pressure."""
    p0 = 101325  # Sea level standard atmospheric pressure [Pa]
    MM = 0.0289652  # Molar mass of dry air [kg/mol]
    Rc = 8.31446  # ideal (universal) gas constant [J/mol*K]
    try:
        return p0 * m.exp((-g(h) * MM * h) / (Rc * T(h)))
    except:
        return 0


def rho(h):
    """Return density of air."""
    MM = 0.0289652  # Molar mass of dry air [kg/mol]
    Rc = 8.31446  # ideal (universal) gas constant [J/mol*K]
    try:
        return (p(h) * MM) / (T(h) * Rc)
    except ZeroDivisionError:
        return 0


def dv(h):
    """Return dynamic viscosity."""
    Sc = 110.4  # Sutherland's constant [k]
    m0 = 1.71 * 10 ** -5  # Dynamic viscosity at 0°C [kg/m*s]
    t0 = 273.15  # Reference temperature [k]
    return m0 * (t0 + Sc / T(h) + Sc) * (T(h) / t0) ** (3 / 2)


def Reynolds(D, v, h):
    """Return reynolds number."""
    return (rho(h) * abs(v) * D) / dv(h)


def vsound(h):
    """Return the speed of sound."""
    gm = 1.401  # Heat capacity index [-]
    Rs = 287.052874  # Specific gas constant for dry air [J/kg*k]
    return (gm * Rs * T(h)) ** (1 / 2)


def Drag_coefficient(v, h, shape, D):
    """Return the drag coefficient."""
    M = abs(v) / vsound(h)  # Mach number (number of times the speed of sound)[-]
    if M >= 1:
        return 1 / (2 + (2 * M) / 5)
    elif shape == "blunt":
        return (24 / Reynolds(D, v, h)) * (0.15 * Reynolds(D, v, h) ** 0.687 + 1)
    elif shape == "conic":
        return (1.2 / Reynolds(D, v, h) ** (1 / 2))


def fd(h, v, rA, shape, D):
    """Return force of drag."""
    Rho = rho(h)
    try:
        Cd = Drag_coefficient(v, h, shape, D)
    except ZeroDivisionError:
        return 0
    return (1 / 2) * (Rho) * v ** 2 * Cd * rA * (v / abs(v))


def wind(vr, yr, terrain, y, G):
    if terrain == "flat":
        alpha = 0.11
        if yr == 0:
            z0 = 0.0151
            vpl = vr * ((y + z0) / (yr + z0)) ** alpha  # Wind using power law
        else:
            vpl = vr * (y / yr) ** alpha
    if terrain == "rough":
        alpha = 1 / 7
        if yr == 0:
            z0 = 0.55
            vpl = vr * ((y + z0) / (yr + z0)) ** alpha
        else:
            vpl = vr * (y / yr) ** alpha
    try:
        vgo = vr + G * m.log(p(yr) / p(y))  # Wind using Geostrophic Wind Approx.
    except ZeroDivisionError:
        vgo = 0
    S = 1 / (1 + m.exp(-0.0005 * (y - 1000)))  # Smoothing function
    v = vpl * (1 - S) + vgo * S
    return v


def sim(vi, yi, theta, M, rA, ymin, dt, shape, D, G, vwind, terrain, wa):
    """Make the simulation."""
    xc, yc = [], []
    y = yi
    x = 0
    v = vi
    vx = m.cos(theta * (m.pi / 180)) * v
    vy = m.sin(theta * (m.pi / 180)) * v
    c = 0
    while y >= 0 and dt * c < 10e4:
        vwx = wind(vwind, yi, terrain, y, G) * m.cos(m.radians(wa))
        theta = m.atan(vy / vx)
        ady = m.sin(theta) * fd(y, v, rA, shape, D) / M
        adr = m.cos(theta) * fd(y, v, rA, shape, D) / M
        wdr = fd(y, vwx, rA, shape, D) / M
        adx = adr + wdr
        if theta > 0:  # If projectile is rising, acceleration drag y downwards
            ady *= -1
        else:
            ""  # Else upwards
        ag = g(y)
        vy += (ady - ag) * dt
        vx -= adx * dt
        v = (vx ** 2 + vy ** 2) ** (1 / 2)
        y += vy * dt
        x += vx * dt
        xc.append(x)
        yc.append(y)
        c += 1
    t = dt * c
    return xc, yc, t


def max_values(vi, hi, dtheta, M, rA, ymin, dt, shape, D, G, vwind, terrain, wa, an_min, an_max):
    """Get the max values of a given shot, varying the angle."""
    xmax_lst = []
    ymax_lst = []
    tmax_lst = []
    angl_lst = []
    for i in range(int(an_min / dtheta), int(an_max / dtheta + 1)):
        xc, yc, t = sim(vi, hi, i * dtheta, M, rA, ymin, dt, shape, D, G, vwind, terrain, wa)
        xmax_lst.append(xc[-1])
        ymax_lst.append(max(yc))
        tmax_lst.append(t)
        angl_lst.append(i * dtheta)
    return xmax_lst, ymax_lst, tmax_lst, angl_lst


def aim(theta, xc, yi):
    """Make a dotted line where the cannon aims."""
    xa, ya = [0, xc[-1]], [yi, m.tan(m.radians(theta)) * xc[-1] + yi]  # X/Y aim
    return xa, ya


def show(xc, yc, xa, ya, t, xmax_lst, ymax_lst, tmax_lst, angl_lst, theta, axs):
    maxval = max([max(xc), max(yc)])
    limx = (0 - (1 / 20) * maxval, maxval + (1 / 20) * maxval)
    limy = maxval + (1 / 20) * maxval
    axs[0, 0].set(xlim=limx, ylim=(0, limy))
    axs[0, 0].plot(xc, yc, 'k-', label="Trajectory")
    axs[0, 0].plot(xa, ya, 'r--', label=f'Aim ({theta}°)')
    axs[0, 1].plot(angl_lst, xmax_lst, 'g-', label="Distance travelled depending on angle")
    axs[1, 0].plot(angl_lst, ymax_lst, 'b-', label="Maximum height depending on angle")
    axs[1, 1].plot(angl_lst, tmax_lst, 'r-', label="Flight time depending on angle")
    axs[0, 0].legend()
    axs[0, 1].legend()
    axs[1, 0].legend()
    axs[1, 1].legend()
    print(f'Flight time: {t}s')
    print(f'Distance travelled: {xc[-1]}m')
    print(f'Maximum height reached: {max(yc)}m')
    print(f'Maximum flight time: {max(tmax_lst)}s with angle {angl_lst[tmax_lst.index(max(tmax_lst))]}°')
    print(f'Maximum distance: {max(xmax_lst)}m with angle {angl_lst[xmax_lst.index(max(xmax_lst))]}°')
    print(f'Maximum height: {max(ymax_lst)}m with angle {angl_lst[ymax_lst.index(max(ymax_lst))]}°')


def get_infos(queue, shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa, dt, dtheta, theta_min, theta_max):
    if latitude <= 30:
        G = 2.7  # Constant used in wind speed [m/s]
    elif latitude <= 60:
        G = 2.85
    else:
        G = 3

    start = time.time()

    num_processes = multiprocessing.cpu_count()
    options = []
    for i in range(num_processes):
        nb_angles = (theta_max - theta_min) / num_processes
        option = (vi, ymin, dtheta, M, rA, ymin, dt, shape, D, G, vwind, terrain, wa)
        option += (theta_min + nb_angles * i,)
        option += (theta_min + nb_angles * (i + 1),)

        options.append(option)
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(max_values, options)
    xmax_lst, ymax_lst, tmax_lst, angl_lst = [], [], [], []
    for result in results:
        xmax_lst += result[0]
        ymax_lst += result[1]
        tmax_lst += result[2]
        angl_lst += result[3]

    # xmax_lst, ymax_lst, tmax_lst, angl_lst = max_values(vi, ymin, dtheta, M, rA, ymin, dt, shape, D, G, vwind, terrain, wa, 0, 90)
    end = time.time()
    print(f'{end - start}s')
    queue.put((xmax_lst, ymax_lst, tmax_lst, angl_lst))


def go(shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa, dt, dtheta, theta_min=0, theta_max=90):
    if latitude <= 30:
        G = 2.7  # Constant used in wind speed [m/s]
    elif latitude <= 60:
        G = 2.85
    else:
        G = 3
    xc, yc, t = sim(vi, ymin, theta, M, rA, ymin, dt, shape, D, G, vwind, terrain, wa)

    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=get_infos, args=(
    queue, shape, terrain, D, rA, M, vi, theta, ymin, latitude, vwind, wa, dt, dtheta, theta_min, theta_max))
    process.start()
    process.join()  # Wait for completion

    xmax_lst, ymax_lst, tmax_lst, angl_lst = queue.get()

    xa, ya = aim(theta, xc, ymin)
    # fig, axs = plt.subplots(2, 2)
    # show(xc, yc, xa, ya, t, xmax_lst, ymax_lst, tmax_lst, angl_lst, theta, axs)
    return xc, yc, xa, ya, t, xmax_lst, ymax_lst, tmax_lst, angl_lst, theta


if __name__ == '__main__':
    go('blunt', 'rough', 0.1, 0.0134, 30, 3000, 30, 5000, 0, 0, 0, 0.1, 1)
    plt.show()