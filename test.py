import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import math
plt.style.use('dark_background')

fig = plt.figure()
fi1 = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
ax2 = fig.add_subplot(1, 1, 1)
time0=time.perf_counter()
xs = []
ys = []

def animate(i):
   # data = open('stock.txt', 'r').read()
   # lines = data.split('\n')

    t=time.perf_counter()-time0

    y=t
    x=math.sin(y)

    xs.append(x)
    ys.append(float(y))

   # ax1.clear()
    ax1.plot(xs, ys, lw=3, color = 'g')

    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.title('Обновляемые графики в matplotlib')


def animate2(i):
 # data = open('stock.txt', 'r').read()
 # lines = data.split('\n')

 t = time.perf_counter() - time0

 y = t
 x = math.cos(y)

 xs.append(x)
 ys.append(float(y))

 ax2.clear()
 ax2.plot(xs, ys, lw=3, color='g')

 plt.xlabel('Дата')
 plt.ylabel('Цена')
 plt.title('Обновляемые графики в matplotlib')

ani = animation.FuncAnimation(fig, animate, interval=50)
ani2 = animation.FuncAnimation(fi1, animate2, interval=60)
plt.show()