import threading

def task(thread_number):
    print(f"Task {thread_number} is running")

# Create and start 5 threads
threads = []
for i in range(5):
    thread = threading.Thread(target=task, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All threads completed")