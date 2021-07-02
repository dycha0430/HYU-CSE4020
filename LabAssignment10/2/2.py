import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo

gCamAng = 0.
gCamHeight = 1.

def exp(rv):
    theta = l2norm(rv)
    if (theta != 0):
        rv = normalized(rv)
    cos = np.cos(theta)
    sin = np.sin(theta)
    
    R = np.array([[cos + rv[0]*rv[0]*(1-cos), rv[0]*rv[1]*(1-cos)-rv[2]*sin, rv[0]*rv[2]*(1-cos) + rv[1]*sin],
                  [rv[1]*rv[0]*(1-cos) + rv[2]*sin, cos + rv[1]*rv[1]*(1-cos), rv[1]*rv[2]*(1-cos) - rv[0]*sin],
                  [rv[2]*rv[0]*(1-cos) - rv[1]*sin, rv[2]*rv[1]*(1-cos) + rv[0]*sin, cos + rv[2]*rv[2]*(1-cos)]])

    return R

def log(R):
    theta = np.arccos((R[0, 0] + R[1, 1] + R[2, 2] - 1) / 2)
    v1 = (R[2, 1] - R[1, 2]) / (2*np.sin(theta))
    v2 = (R[0, 2] - R[2, 0]) / (2*np.sin(theta))
    v3 = (R[1, 0] - R[0, 1]) / (2*np.sin(theta))
    vector = np.array([v1, v2, v3])

    return normalized(vector)*theta
    

def slerp(R1, R2, t):
    return R1@exp(t*log(R1.T@R2))

def l2norm(v):
    return np.sqrt(np.dot(v, v))

def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)






def createVertexAndIndexArrayIndexed():
    varr = np.array([
            ( -0.5773502691896258 , 0.5773502691896258 ,  0.5773502691896258 ),
            ( -1 ,  1 ,  1 ), # v0
            ( 0.8164965809277261 , 0.4082482904638631 ,  0.4082482904638631 ),
            (  1 ,  1 ,  1 ), # v1
            ( 0.4082482904638631 , -0.4082482904638631 ,  0.8164965809277261 ),
            (  1 , -1 ,  1 ), # v2
            ( -0.4082482904638631 , -0.8164965809277261 ,  0.4082482904638631 ),
            ( -1 , -1 ,  1 ), # v3
            ( -0.4082482904638631 , 0.4082482904638631 , -0.8164965809277261 ),
            ( -1 ,  1 , -1 ), # v4
            ( 0.4082482904638631 , 0.8164965809277261 , -0.4082482904638631 ),
            (  1 ,  1 , -1 ), # v5
            ( 0.5773502691896258 , -0.5773502691896258 , -0.5773502691896258 ),
            (  1 , -1 , -1 ), # v6
            ( -0.8164965809277261 , -0.4082482904638631 , -0.4082482904638631 ),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    iarr = np.array([
            (0,2,1),
            (0,3,2),
            (4,5,6),
            (4,6,7),
            (0,1,5),
            (0,5,4),
            (3,6,2),
            (3,7,6),
            (1,2,6),
            (1,6,5),
            (0,7,3),
            (0,4,7),
            ])
    return varr, iarr

def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([3.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,3.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,3.]))
    glEnd()

def render(t):
    global gCamAng, gCamHeight
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1,10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3.,4.,5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1.,1.,1.,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    objectColor = (1.,1.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    ############################# Frame 0
    objectColor = (1.,0.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    R1_0 = np.identity(4)
    xang = np.radians(20)
    yang = np.radians(30)
    zang = np.radians(30)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R1_0[:3, :3] = Rx @ Ry @ Rz
    J1_0 = R1_0
    
    glPushMatrix()
    glMultMatrixf(J1_0.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R2_0 = np.identity(4)
    xang = np.radians(15)
    yang = np.radians(30)
    zang = np.radians(25)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R2_0[:3, :3] = Rx @ Ry @ Rz
    
    T1 = np.identity(4)
    T1[0][3] = 1.

    J2_0 = R1_0 @ T1 @ R2_0

    glPushMatrix()
    glMultMatrixf(J2_0.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    ##################################### Frame 20
    objectColor = (1.,1.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    R1_20 = np.identity(4)
    xang = np.radians(45)
    yang = np.radians(60)
    zang = np.radians(40)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R1_20[:3, :3] = Rx @ Ry @ Rz
    J1_20 = R1_20
    
    glPushMatrix()
    glMultMatrixf(J1_20.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R2_20 = np.identity(4)
    xang = np.radians(25)
    yang = np.radians(40)
    zang = np.radians(40)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R2_20[:3, :3] = Rx @ Ry @ Rz
    
    T1 = np.identity(4)
    T1[0][3] = 1.

    J2_20 = R1_20 @ T1 @ R2_20

    glPushMatrix()
    glMultMatrixf(J2_20.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    ################################### Frame 40
    objectColor = (0.,1.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    R1_40 = np.identity(4)
    xang = np.radians(60)
    yang = np.radians(70)
    zang = np.radians(50)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R1_40[:3, :3] = Rx @ Ry @ Rz
    J1_40 = R1_40
    
    glPushMatrix()
    glMultMatrixf(J1_40.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R2_40 = np.identity(4)
    xang = np.radians(40)
    yang = np.radians(60)
    zang = np.radians(50)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R2_40[:3, :3] = Rx @ Ry @ Rz
    
    T1 = np.identity(4)
    T1[0][3] = 1.

    J2_40 = R1_40 @ T1 @ R2_40

    glPushMatrix()
    glMultMatrixf(J2_40.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    #################################### Frame 60
    objectColor = (0.,0.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    R1_60 = np.identity(4)
    xang = np.radians(80)
    yang = np.radians(85)
    zang = np.radians(70)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R1_60[:3, :3] = Rx @ Ry @ Rz
    J1_60 = R1_60
    
    glPushMatrix()
    glMultMatrixf(J1_60.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R2_60 = np.identity(4)
    xang = np.radians(55)
    yang = np.radians(80)
    zang = np.radians(65)
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    R2_60[:3, :3] = Rx @ Ry @ Rz
    
    T1 = np.identity(4)
    T1[0][3] = 1.

    J2_60 = R1_60 @ T1 @ R2_60

    glPushMatrix()
    glMultMatrixf(J2_60.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    ######################################## END
    t = glfw.get_time()
    t = (t*50 % 61)
    
    objectColor = (1.,1.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    if t >= 0 and t < 20:
        M1 = np.identity(4)

        T1 = np.identity(4)
        T1[0][3] = 1.
        
        glPushMatrix()
        Ri = slerp(R1_0[:3, :3], R1_20[:3, :3], t/20)
        M1[:3, :3] = Ri
        glMultMatrixf(M1.T)
        
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()


        M2 = np.identity(4)
        glPushMatrix()
        Rj = slerp(R2_0[:3, :3], R2_20[:3, :3], t/20)
        M2[:3, :3] = Rj
        M3 = M1 @ T1 @ M2
        glMultMatrixf(M3.T)
        
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
    elif t >= 20 and t < 40:

        M1 = np.identity(4)

        T1 = np.identity(4)
        T1[0][3] = 1.
        
        glPushMatrix()
        Ri = slerp(R1_20[:3, :3], R1_40[:3, :3], (t-20)/20)
        M1[:3, :3] = Ri
        glMultMatrixf(M1.T)
        
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()


        M2 = np.identity(4)
        glPushMatrix()
        Rj = slerp(R2_20[:3, :3], R2_40[:3, :3], (t-20)/20)
        M2[:3, :3] = Rj
        M3 = M1 @ T1 @ M2
        glMultMatrixf(M3.T)
        
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
    elif t >= 40 and t < 61:
        M1 = np.identity(4)

        T1 = np.identity(4)
        T1[0][3] = 1.
        glPushMatrix()
        Ri = slerp(R1_40[:3, :3], R1_60[:3, :3], (t-40)/20)
        M1[:3, :3] = Ri
        glMultMatrixf(M1.T)
        
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()


        M2 = np.identity(4)
        glPushMatrix()
        Rj = slerp(R2_40[:3, :3], R2_60[:3, :3], (t-40)/20)
        M2[:3, :3] = Rj
        M3 = M1 @ T1 @ M2
        glMultMatrixf(M3.T)
        
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
        

    glDisable(GL_LIGHTING)


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key==glfw.KEY_2:
            gCamHeight += .1
        elif key==glfw.KEY_W:
            gCamHeight += -.1

gVertexArrayIndexed = None
gIndexArray = None

def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640,640,'2019056799', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        t = glfw.get_time()
        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

