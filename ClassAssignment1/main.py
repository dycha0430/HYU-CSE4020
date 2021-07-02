import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Projection type : Perspective(True), Orthogonal(False)
projection_type = True

# Zooming
zooming = 0

# Orbit
azimuth = 45.
elevation = 36.
distance = 10
target = np.array([0., 0., 0.])
cur_xpos = 0
cur_ypos = 0
u = np.array([1, 0, 0])
v = np.array([0, 1, 0])
w = np.array([0, 0, 1])

# Set if mouse button pressed
button_left_pressed = False
button_right_pressed = False

def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f( 0.5, 0.5, 0.5) 
                             
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f( 0.5,-0.5,-0.5) 
                             
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
                             
    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)
 
    glVertex3f(-0.5, 0.5, 0.5) 
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5) 
    glVertex3f(-0.5,-0.5, 0.5) 
                             
    glVertex3f( 0.5, 0.5,-0.5) 
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5,-0.5)
    glEnd()

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([1.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,1.]))
    glEnd()
    
def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE ) 

    glLoadIdentity()

    global projection_type
    
    if projection_type:
        gluPerspective(45, 1, 3,20)
    else:
        glOrtho(-10, 10, -10, 10, -20, 20)
        
    global azimuth, elevation, distance, target, u, v, w, zooming
    r_azimuth = np.radians(azimuth)
    r_elevation = np.radians(elevation)
    tmp = distance*np.cos(r_elevation)
    camera = np.array([target[0] + tmp*np.sin(r_azimuth), target[1] + distance*np.sin(r_elevation), target[2] + tmp*np.cos(r_azimuth)])
    Ma = np.array([[np.cos(r_azimuth), 0., np.sin(r_azimuth)],
                   [0., 1., 0.],
                   [-np.sin(r_azimuth), 0., np.cos(r_azimuth)]])
    Me = np.array([[1., 0., 0.],
                  [0., np.cos(r_elevation), np.sin(r_elevation)],
                  [0., -np.sin(r_elevation), np.cos(r_elevation)]])
    M = Ma @ Me
    u = M @ np.array([1., 0., 0.])
    v = M @ np.array([0., 1., 0.])
    w = M @ np.array([0., 0., 1.])
    u = u / np.sqrt(np.dot(u, u))
    v = v / np.sqrt(np.dot(v, v))
    w = w / np.sqrt(np.dot(w, w))
    camera -= zooming*w


    Mv = np.array([[u[0], u[1], u[2], -np.dot(u, camera)],
                   [v[0], v[1], v[2], -np.dot(v, camera)],
                   [w[0], w[1], w[2], -np.dot(w, camera)],
                   [0, 0, 0, 1]])
    glMultMatrixf(Mv.T)
    
    
    drawFrame()
    drawGrid()
    glColor3ub(255, 255, 0)
    drawUnitCube()


def drawGrid():
    glBegin(GL_LINES)
    glColor3ub(211, 211, 211) # light gray
    for i in range(-10, 11):
        glVertex3fv(np.array([i, 0, -10]))
        glVertex3fv(np.array([i, 0, 10]))
        glVertex3fv(np.array([-10, 0, i]))
        glVertex3fv(np.array([10, 0, i]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global projection_type
    if key == glfw.KEY_V and action == glfw.PRESS:
        projection_type = not projection_type

def scroll_callback(window, xoffset, yoffset):
    # zoom in 하면 (0, 1), zoom out하면 (0, -1)
    global zooming
    zooming += yoffset

def button_callback(window, button, action, mod):
    global button_left_pressed, button_right_pressed
    if button==glfw.MOUSE_BUTTON_LEFT:
        if action==glfw.PRESS:
            button_left_pressed = True
        elif action==glfw.RELEASE:
            button_left_pressed = False
    elif button==glfw.MOUSE_BUTTON_RIGHT:
        if action==glfw.PRESS:
            button_right_pressed = True
        elif action==glfw.RELEASE:
            button_right_pressed = False


def cursor_callback(window, xpos, ypos):
    global azimuth, elevation, button_left_pressed, button_right_pressed, cur_xpos, cur_ypos
    if button_left_pressed:
        azimuth += cur_xpos - xpos
        elevation -= cur_ypos - ypos
    elif button_right_pressed:
        global target, u, v
        target += 0.008*(cur_xpos - xpos)*u
        target += 0.008*(ypos - cur_ypos)*v

    cur_xpos = xpos
    cur_ypos = ypos

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800,'basic_OpenGL_Viewer', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)

    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
