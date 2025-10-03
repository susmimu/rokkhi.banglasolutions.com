import _thread as th
import time


first_thread_status = True
second_thread_status = True


def first_thread(delay):
    while first_thread_status:
        print('I am first_thread')
        time.sleep(delay)
    
    print('first_thread finished')


def second_thread(delay):
    while second_thread_status:
        print('I am second_thread')
        time.sleep(delay)
        
    print('second_thread finished')


print("Starting first_thread...")
th.start_new_thread(first_thread, (3,))

print("Starting second_thread...")
th.start_new_thread(second_thread, (3,))


print("Starting main loop...")
counter = 1

while True:
    print("counter:", counter)
    counter += 1
    
    if counter > 10:
        first_thread_status = False
    if counter > 20:
        second_thread_status = False
    if counter > 30:
        break
    
    time.sleep(1)

print("Main loop finished")
