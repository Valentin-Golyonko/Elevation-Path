import multiprocessing as mp
import time


def f(x, y):
    print("x= " + str(x) + " x+y= " + str(x + y))


start_time = time.time()
p = 0
y = 0
for i in range(0, 1000):
    y += 1
    # p = mp.Process(target=f, args=(i, y))
    # p.start()

    f(i, y)

# p.join()

print(time.time() - start_time)
# 0.0036513805389404297  poor Python
# 0.6507318019866943     with MP
