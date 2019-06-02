import multiprocessing as mp
import time

import logs.Log_Color as Logs

Logs.log_start("start")


def foo(a, b):
    Logs.log_info("a= " + str(a) + " a+b= " + str(a + b))


start_time = time.time()
p = 0
y = 0
for i in range(0, 1000):
    y += 1
    p = mp.Process(target=foo, args=(i, y))
    p.start()

    # f(i, y)

p.join()

Logs.log_info(time.time() - start_time)
# 0.0036513805389404297  poor Python
# 0.6507318019866943     with MP
