# from matrix_lite import led
# led.length
# led.set('blue') # color name
# # led.set('#0000ff') # hex values
# # led.set({'r':0, 'g':0, 'b':255, 'w':0 }) # object
# # led.set((0,0,255,0)) # tuple
from matrix_lite import led
import time

everloop = ['black'] * led.length
# everloop[0] = {'b':100}

# while True:
#     # pops the led from position 0 and appends it. Effectively rotating the list of values
#     everloop.append(everloop.pop(0))
#     led.set(everloop)
#     time.sleep(0.050)
    
def listening_led(theta):
    
    return True