import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Obj file info
varr = np.empty((0, 3))
narr = np.empty((0, 3))
gVertexArraySeparate = np.empty((0, 3))
gVertexArraySeparate_box = np.empty((0, 3))

isExtra = 0


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
animatingMode = False

# Set if mouse button pressed
button_left_pressed = False
button_right_pressed = False

# current bvh file name
currentBVH = ""

# For motion capture
frames = 0
frameNum = 0
motionData = []
currentMotion = ""

jointNum = 0
jointList = []




###########################################################
def createHierarchicalModelObject():
    global narr, varr, gVertexArraySeparate, gVertexArraySeparate_box
    varr = np.empty((0, 3))
    narr = np.empty((0, 3))
    gVertexArraySeparate = np.empty((0, 3))
    gVertexArraySeparate_box = objRender('./cube-tri.obj')


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


###########################################################

def savingMotionData(filename):
    global motionData, frames, jointNum, jointList
    frameTime = 0.
    f = open(filename, 'r')
    while True:
        line = f.readline()
        if not line: break
        words = line.split()
        if len(words)==0: continue

        if (words[0] == 'Frames:'): frames = int(words[1])
        elif (words[0] == 'Frame' and words[1] == 'Time:'):
            frameTime = float(words[2])
            for i in range(0, frames):
                line = f.readline()
                motionData.append(line)
        elif (words[0] == 'JOINT' or words[0] == 'ROOT'):
            jointNum += 1
            jointList.append(words[1])
            


    print("File name : ", filename.split('\\')[-1])
    print("Number of frames : ", frames)
    print("FPS (1/FrameTime) : ", 1/frameTime)
    print("Number of joints : ", jointNum)
    print("List of all joint names : ", jointList)
    

def bvhRender(filename):
    global currentMotion, isExtra, gVertexArraySeparate_box
    
    num = 0
    currentMotions = currentMotion.split()
    isEnd = 0
    curJoint = ""
    
    f = open(filename, 'r')
    while True:
        line = f.readline()
        if not line: break
        words = line.split()
        if len(words)==0: continue
        
        if (words[0] == '{'): glPushMatrix()
        elif (words[0] == '}'): glPopMatrix()
        elif (words[0] == 'ROOT'): curJoint = words[1]
        elif (words[0] == 'End'): isEnd = 1
        elif (words[0] == 'JOINT'): curJoint = words[1]
        elif (words[0] == 'OFFSET'):
            if isExtra:
                glPushMatrix()
                if curJoint == 'Spine':        
                    glScalef(.03, .005, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'Head':
                    if (isEnd):
                        glTranslatef(0., .07, 0.)
                        glScalef(.03, .05, .03)
                    else:
                        glTranslatef(0., .14, 0.)
                        glScalef(.03, .18, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'RightForeArm':
                    glRotatef(-5, 0, 1, 0)
                    glScalef(.13, .03, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'RightHand':
                    if (isEnd):
                        glScalef(.05, .03, .03)
                    else:
                        glScalef(.15, .03, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'LeftForeArm':
                    glRotatef(5, 0, 1, 0)
                    glScalef(.13, .03, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'LeftHand':
                    if (isEnd):
                        glScalef(.05, .03, .03)
                    else:
                        glScalef(.15, .03, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'RightLeg':
                    glTranslatef(0., -.07, 0.)
                    glScalef(.03, .2, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'RightFoot':
                    if isEnd:
                        glRotatef(-70, 1, 0, 0)
                        glScalef(.03, .05, .03)
                    else:
                        glTranslatef(0, -.13, 0.)
                        glScalef(.03, .2, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'LeftLeg':
                    glTranslatef(0., -.07, 0.)
                    glScalef(.03, .2, .03)
                    drawObj(gVertexArraySeparate_box)
                elif curJoint == 'LeftFoot':
                    if isEnd:
                        glRotatef(-70, 1, 0, 0)
                        glScalef(.03, .05, .03)
                    else:
                        glTranslatef(0, -.13, 0.)
                        glScalef(.03, .2, .03)
                    drawObj(gVertexArraySeparate_box)
                glPopMatrix()
            else:
                glBegin(GL_LINES)
                glVertex3fv(np.array([0, 0, 0]))
                glVertex3fv(np.array([float(words[1]), float(words[2]), float(words[3])]))
                glEnd()
            glTranslatef(float(words[1]), float(words[2]), float(words[3]))
            isEnd = 0
            
                
        elif (words[0] == 'CHANNELS'):
            if not animatingMode: continue
            chanNum = int(words[1])
            Tx = Ty =  Tz = Rz = Rx = Ry = 0.
            for i in range(0, chanNum):
                chanType = words[2+i].upper()
                if chanType == 'XPOSITION':
                    Tx = float(currentMotions[num])
                    num += 1
                    glTranslatef(Tx, 0, 0)
                elif chanType == 'YPOSITION':
                    Ty = float(currentMotions[num])
                    num += 1
                    glTranslatef(0, Ty, 0)
                elif chanType == 'ZPOSITION':
                    Tz = float(currentMotions[num])
                    num += 1
                    glTranslatef(0, 0, Tz)
                elif chanType == 'XROTATION':
                    Rx = float(currentMotions[num])
                    num += 1
                    glRotatef(Rx, 1, 0, 0)
                elif chanType == 'YROTATION':
                    Ry = float(currentMotions[num])
                    num += 1
                    glRotatef(Ry, 0, 1, 0)
                elif chanType == 'ZROTATION':
                    Rz = float(currentMotions[num])
                    num += 1
                    glRotatef(Rz, 0, 0, 1)

            
    f.close()
            
    
def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) 

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

    #glScalef(3., 3., 3.)
    #glScalef(.1, .1, .1)
    #glScalef(.01, .01, .01)
    global frameNum, frameTime, motionData, currentMotion, frames, isExtra
    glColor3ub(255, 255, 0)

    if animatingMode:
        currentMotion = motionData[frameNum]
        frameNum += 1
        if frameNum >= frames: frameNum = 0
    if (currentBVH.split('\\')[-1] == 'sample-walk.bvh'):
        isExtra = 1
        bvhRender(currentBVH)
    elif (currentBVH != ""):
        glDisable(GL_LIGHTING)
        isExtra = 0
        bvhRender(currentBVH)
        
    glDisable(GL_LIGHTING)
    


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
    global projection_type, lastFrameTime, animatingMode, motionData, frameNum, currentMotion
    if key == glfw.KEY_V and action == glfw.PRESS:
        projection_type = not projection_type
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        lastFrameTime = glfw.get_time()
        frameNum = 0
        currentMotion = motionData[frameNum]
        frameNum += 1
        animatingMode = not animatingMode

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
    global currentBVH, frameNum, frameTime, motionData, currentMotion, frames, animatingMode

    frames = 0
    frameNum = 0
    frameTime = 0.
    motionData = []
    currentMotion = ""
    animatingMode = False
    jointNum = 0
    jointList = []
    
    savingMotionData(paths[0])
    currentBVH = paths[0]

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800,'bvh_File_Viewer', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_drop_callback(window, drop_callback)

    createHierarchicalModelObject() # Create obj models
    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
