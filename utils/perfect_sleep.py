import time

# we had to use this busy wait operation because time.sleep() is not accurate enough for our purposes
def perfect_sleep(duration):
	target = time.perf_counter() + duration
	while True:
		if time.perf_counter() >= target: break