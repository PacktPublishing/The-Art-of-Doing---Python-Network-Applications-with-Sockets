import threading
#Threading allows us to speed up programs by executing multiple tasks at the SAME time.
#Each task will run on its own thread
#Each thread can run simultanelously and share data with each other.

#Every thread when you start it must do SOMETHING, which we can define with a function.
#Our threads will then target these functions.
#When we start the threads, the target functions will be run.

def function1():
    for i in range(10):
        print("ONE ")


def function2():
    for i in range(10):
        print("TWO ")


def function3():
    for i in range(10):
        print("THREE ")

#If we call these functions, we see the first function call MUST complete betfore the next
#They are exectued linearly
#function1()
#function2()
#function3()

#WE can execute these functions concurrently using threads!  We must have a target for a thread.
t1 = threading.Thread(target=function1)
t2 = threading.Thread(target=function2)
t3 = threading.Thread(target=function3)

#t1.start()
#t2.start()
#t3.start()

#Threads can only be run once.  If you want to reuse, you must redfine.
t1 = threading.Thread(target=function1)
t1.start()

#If you want to 'pause' the main programin until a thread is done you can!
t1 = threading.Thread(target=function1)
t1.start()
t1.join() #This pauses the main program until the thread is complete
print("Threading rules!")