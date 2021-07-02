import numpy as np
import math
import glfw
from OpenGL.GL import *

def render(th):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()

    glColor3ub(255, 255, 255)
    # calculate matrix M1, M2 using th 
    # your implementation
    M1 = np.array([[np.cos(th), np.sin(th), 0.],
                   [-np.sin(th), np.cos(th), 0.],
                   [0., 0., 1.]])
    M1 = M1 @ np.array([[1., 0., .5],
                       [0., 1., 0.],
                       [0., 0., 1.]])
    M2 = np.array([[np.cos(th), np.sin(th), 0.],
                   [-np.sin(th), np.cos(th), 0.],
                   [0., 0., 1.]])
    M2 = M2 @ np.array([[1., 0., 0,],
                       [0., 1., .5],
                       [0., 0., 1.]])
     
    # draw point p
    glBegin(GL_POINTS)
    # your implementation
    p1 = M1 @ np.array([.5, 0., 1.])
    p2 = M2 @ np.array([0., .5, 1.])
    glVertex2f(p1[0], p1[1])
    glVertex2f(p2[0], p2[1])
    
    glEnd()
    # draw vector v
    glBegin(GL_LINES)
    # your implementation
    v1 = M1 @ np.array([.5, 0., 0.])
    v2 = M2 @ np.array([0., .5, 0.])
    glVertex2f(0., 0.)
    glVertex2f(v1[0], v1[1])
    glVertex2f(0., 0.)
    glVertex2f(v2[0], v2[1])
    glEnd()
    

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(480, 480, "2019056799", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        t = glfw.get_time()
        th = t

        render(t)
        glfw.swap_buffers(window)

    glfw.terminate()
    

if __name__ == "__main__":
    main()
