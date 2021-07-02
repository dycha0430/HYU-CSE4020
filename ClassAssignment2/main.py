import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Obj file info
varr = np.empty((0, 3))
narr = np.empty((0, 3))
gVertexArraySeparate = np.empty((0, 3))
newVertexArraySeparate1 = np.empty((0, 3))
newVertexArraySeparate2 = np.empty((0, 3))
newVertexArraySeparate3 = np.empty((0, 3))

# True (Single mesh rendering mode) False (Animating hierarchical model rendering mode)
renderingMode = False

# False (Solid mode) True (Wireframe mode)
isWireframeMode = False

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






########### Animating hierarchical model rendering mode ##########
def createHierarchicalModelObject():
    global narr, varr, gVertexArraySeparate, newVertexArraySeparate1, newVertexArraySeparate2, newVertexArraySeparate3

    varr = np.empty((0, 3))
    narr = np.empty((0, 3))
    gVertexArraySeparate = np.empty((0, 3))
    newVertexArraySeparate1 = objRender('./island.obj')

    varr = np.empty((0, 3))
    narr = np.empty((0, 3))
    gVertexArraySeparate = np.empty((0, 3))
    newVertexArraySeparate2 = objRender('./chimp.obj')

    varr = np.empty((0, 3))
    narr = np.empty((0, 3))
    gVertexArraySeparate = np.empty((0, 3))
    newVertexArraySeparate3 = objRender('./banana.obj')

    
def drawAnimatingModel():
    # Implement
    global newVertexArraySeparate1, newVertexArraySeparate2, newVertexArraySeparate3

    t = glfw.get_time()
    glPushMatrix()
    glTranslate(3*np.sin(t), 2 + 2*np.cos(t), np.sin(2*t))

    # Island drawing
    glPushMatrix()
    objectColor = (0.333333, 0.419608, 0.184314, 1.)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    glScalef(2., 2., 2.)
    drawObj(newVertexArraySeparate1)
    glPopMatrix()



    # Monkey drawing
    glPushMatrix()
    glRotatef(t*(180/np.pi), 0, 1, 0)
    glTranslatef(1.5, .45, 0.)
    glRotatef(t*(180/np.pi), 0 ,1, 0)
    
    objectColor = (0.823529, 0.411765, 0.117647, 1.)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    glPushMatrix()
    glScalef(.015, .015, .015)
    drawObj(newVertexArraySeparate2)
    glPopMatrix()

    # Banana drawing
    glPushMatrix()
    objectColor = (1., 1., 0., 1.)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    
    glTranslatef(0., 2, 0.)
    glRotatef(5*t*(180/np.pi), 0, 1, 0)
    glScale(0.005, 0.005, 0.005)
    drawObj(newVertexArraySeparate3)
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()

##################################################################





################### Single mesh rendering mode ###################

def appendVertexArraySeparate(words):
    global gVertexArraySeparate, varr, narr
    for f in words:        
        if f == 'f': continue
        arr = f.split('/')
        gVertexArraySeparate = np.append(gVertexArraySeparate, np.array([narr[int(arr[2]) - 1]]), axis = 0)
        gVertexArraySeparate = np.append(gVertexArraySeparate, np.array([varr[int(arr[0]) - 1]]), axis = 0)

def objRender(filename):
    global varr, narr
    totalFaces = 0
    numFacesWith3Vertices = 0
    numFacesWith4Vertices = 0
    numFacesWithManyVertices = 0
    
    f = open(filename, 'r')
    while True:
        line = f.readline()
        if not line: break
        words = line.split()
        if len(words)==0: continue
        #print("line : ", line, " words : ", words)
        if (words[0] == 'v'):
            vertex = []
            for v in words:
                if v == 'v': continue
                vertex.append(float(v))

            varr = np.append(varr, np.array([vertex]), axis = 0)
        elif (words[0] == 'vn'):
            normal = []
            for n in words:
                if n == 'vn': continue
                normal.append(float(n))

            narr = np.append(narr, np.array([normal]), axis = 0)              
        elif (words[0] == 'f'):
            face = np.array([])
            totalFaces += 1
            if len(words) == 4: numFacesWith3Vertices += 1
            elif len(words) == 5: numFacesWith4Vertices += 1
            elif len(words) > 5: numFacesWithManyVertices += 1

            if len(words) >= 4: splitToTriangle(words)
            else: appendVertexArraySeparate(words)

    if not renderingMode:
        print("FIle name : ", filename.split('\\')[-1])
        print("Total number of faces : ", totalFaces)
        print("Number of faces with 3 vertices : ", numFacesWith3Vertices)
        print("Number of faces with 4 vertices : ", numFacesWith4Vertices)
        print("Number of faces with more than 4 vertices : ", numFacesWithManyVertices)
    else: print("Rendering hierarchical model...")
    global gVertexArraySeparate
    return gVertexArraySeparate

def splitToTriangle(words):
    vertices = words[1:]
    for i in range(1, len(vertices)-1):
        triangleFace = [vertices[0], vertices[i], vertices[i+1]]
        appendVertexArraySeparate(triangleFace)
    
def drawObj(vertexArraySeparate):
    if vertexArraySeparate.size == 0: return
    arr = vertexArraySeparate
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_DOUBLE, 6*arr.itemsize, arr)
    glVertexPointer(3, GL_DOUBLE, 6*arr.itemsize, ctypes.c_void_p(arr.ctypes.data + 3*arr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(arr.size/6))

##############################################################

def drawGrid():
    glBegin(GL_LINES)
    glColor3ub(211, 211, 211) # light gray
    for i in range(-10, 11):
        glVertex3fv(np.array([i, 0, -10]))
        glVertex3fv(np.array([i, 0, 10]))
        glVertex3fv(np.array([-10, 0, i]))
        glVertex3fv(np.array([10, 0, i]))
    glEnd()

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    if isWireframeMode: glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    else: glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )


    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    global projection_type
    
    if projection_type:
        gluPerspective(45, 1, 3,20)
    else:
        glOrtho(-10, 10, -10, 10, -20, 20)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
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

    drawGrid()

    # Lighting
    glEnable(GL_LIGHTING)   # try to uncomment: no lighting
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)

    glEnable(GL_NORMALIZE)

    lightPos = (3., 4., 5., 1.)
    lightPos2 = (-5., -4., -5., 0.)
    lightPos3 = (-3., -4., 5., 0.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos2)
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos3)
    
    lightColor = (1., 1., 1., 1.)
    lightColor2 = (.5, 0., 0., 1.)
    lightColor3 = (0., 0., 1., 1.) 
    ambientLightColor = (.1, .1, .1, 1.)
    ambientLightColor2 = (.1, 0., 0., 1.)
    ambientLightColor3 = (0., 0., .1, 1.) 
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor2)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor2)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor2)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, lightColor3)
    glLightfv(GL_LIGHT2, GL_SPECULAR, lightColor3)
    glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLightColor3)

    objectColor = (1., 1., 0., 1.)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    global gVertexArraySeparate
    if not renderingMode: drawObj(gVertexArraySeparate)
    else: drawAnimatingModel()

    glDisable(GL_LIGHTING)

def key_callback(window, key, scancode, action, mods):
    global projection_type, renderingMode, isWireframeMode
    if key == glfw.KEY_V and action == glfw.PRESS:
        projection_type = not projection_type
    if key == glfw.KEY_H and action ==glfw.PRESS:
        renderingMode = True
        createHierarchicalModelObject()
    if key == glfw.KEY_Z and action == glfw.PRESS:
        isWireframeMode = not isWireframeMode

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

def drop_callback(window, paths):
    global varr, narr, gVertexArraySeparate, renderingMode

    renderingMode = False
    varr = np.empty((0, 3))
    narr = np.empty((0, 3))
    gVertexArraySeparate = np.empty((0, 3))
    objRender(paths[0])

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800,'Class Assignment2', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_drop_callback(window, drop_callback)

    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
