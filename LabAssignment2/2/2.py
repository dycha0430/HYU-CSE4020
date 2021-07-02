import numpy as np
import glfw
from OpenGL.GL import *

current_hour = 0

def render():
    Vx = np.cos(np.linspace(0, 2*np.pi, 13))
    Vy = np.sin(np.linspace(0, 2*np.pi, 13))
    
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_LINE_LOOP)
    for i in range(0, 12):
        glVertex2f(Vx[i], Vy[i])
    glEnd()

    glBegin(GL_LINES)
    glVertex2f(0, 0)
    glVertex2f(np.cos(np.pi/2 - current_hour*np.pi/6), np.sin(np.pi/2 - current_hour*np.pi/6))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global current_hour
    if key==glfw.KEY_1:
        current_hour = 1
    elif key==glfw.KEY_2:
        current_hour = 2
    elif key==glfw.KEY_3:
        current_hour = 3
    elif key==glfw.KEY_4:
        current_hour = 4
    elif key==glfw.KEY_5:
        current_hour = 5
    elif key==glfw.KEY_6:
        current_hour = 6
    elif key==glfw.KEY_7:
        current_hour = 7
    elif key==glfw.KEY_8:
        current_hour = 8
    elif key==glfw.KEY_9:
        current_hour = 9
    elif key==glfw.KEY_0:
        current_hour = 10
    elif key==glfw.KEY_Q:
        current_hour = 11
    elif key==glfw.KEY_W:
        current_hour = 0
        

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(480, 480, "2019056799", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()
    

if __name__ == "__main__":
    main()
