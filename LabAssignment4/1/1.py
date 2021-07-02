import numpy as np
import math
import glfw
from OpenGL.GL import *

input_list = list()

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnates
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    glColor3ub(255, 255, 255)
    
    global input_list
    for i in reversed(input_list):
        if i==glfw.KEY_Q:
            glTranslatef(-0.1, 0., 0.)
        elif i==glfw.KEY_E:
            glTranslatef(0.1, 0., 0.)
        elif i==glfw.KEY_A:
            glRotatef(10., 0., 0., 1.)
        elif i==glfw.KEY_D:
            glRotatef(-10., 0., 0., 1.)
        elif i==glfw.KEY_1:
            glLoadIdentity()
            input_list.clear()
            break;

    drawTriangle()

def key_callback(window, key, scancode, action, mods):
    global input_list
    if action==glfw.PRESS or action==glfw.REPEAT:
        input_list.append(key)
    

def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0.,.5]))
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([.5,0.]))
    glEnd()

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
