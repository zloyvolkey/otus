# Патчи для CPython 2.7

## new_opcode
Добавлен опкод LOAD_OTUS, совмещающий в себе LOAD_FAST и LOAD_CONST, если у LOAD_FAST аргумент == 0

По результатам короткого теста, версия с патчем работает чуть быстрее

* Без патча:

```
[root@26605eb58341 cpython]# /tmp/python/bin/python -m timeit -s 'def fib(n): return fib(n - 1) + fib(n - 2) if n > 1 else n' 'fib(20)'
100 loops, best of 3: 10.7 msec per loop
[root@26605eb58341 cpython]# /tmp/python/bin/python -m timeit -s 'def fib(n): return fib(n - 1) + fib(n - 2) if n > 1 else n' 'fib(30)'
10 loops, best of 3: 1.31 sec per loop
```
* С патчем:
```
[root@26605eb58341 cpython]# /tmp/python/bin/python -m timeit -s 'def fib(n): return fib(n - 1) + fib(n - 2) if n > 1 else n' 'fib(20)'
100 loops, best of 3: 10.5 msec per loop
[root@26605eb58341 cpython]# /tmp/python/bin/python -m timeit -s 'def fib(n): return fib(n - 1) + fib(n - 2) if n > 1 else n' 'fib(30)'
10 loops, best of 3: 1.3 sec per loop
```




## until
Добавлен цикл until

## inc
Добавлен операторы инĸремента и деĸремента (++/--)