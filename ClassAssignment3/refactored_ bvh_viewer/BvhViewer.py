import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pytest

from PyQt5 import QtCore # core Qt functionality, QtWidgets
from PyQt5 import QtGui # extends QtCore with GUI functionality, QtWidgets
from PyQt5 import QtOpenGL # provides QGLWidget, QtWidgets,a special OpenGL QWidget)
from PyQt5 import QtWidgets
import sys
from OpenGL.arrays import vbo


######################################################333
renderer = None
############################################################
def test_pytest():
    assert 3 == 4

############################################################
    
class Joint:
    def __init__(self):
        self.offset = []
        self.channels = []
        self.channel_num: int
        self.children = []
        self.parent: Joint
        self.isEndEffector = False

    def set_channels(self, channels):
        self.channels = channels

    def add_child(self, joint):
        self.children.append(joint)

class Skeleton:
    def __init__(self):
        self.joints = []

    def push_joint(self, joint):
        self.joints.append(joint)
    
class Motion:
    def __init__(self):
        self.skeleton = Skeleton()
        self.postures = []

    def push_joint(self, joint):
        self.skeleton.push_joint(joint)
    def push_posture(self, line):
        self.postures.append(Posture(line))

class Posture:
    def __init__(self, line):
        self.infos = []
        infos_str = line.split()
        for info in infos_str:
            self.infos.append(float(info))
    def get(self, i):
        return self.infos[i]

class BvhFile:
    def __init__(self, file_name):
        self.name = file_name
        self.motion = Motion()
        self.frame_num = 0
        self.frame_time = 0
        self.joint_num = 0
        self.joint_list = []

    def get_frame_num(self):
        return self.frame_num

    def get_posture(self, frame):
        return self.motion.postures[frame]

    def get_root(self):
        return self.motion.skeleton.joints[0]
    
    def parse(self):
        file_name = self.name.split('\\')[-1]
        extension = file_name.split('.')[-1]
        if (extension != 'bvh'):
            print("Drag and drop only .bvh file")
            return False
        f = open(self.name, 'r')
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]
        line_num = 0
        f.close()
        
        isEndEffector = False
        
        cur_joint = Joint()
        while True:
            if line_num == len(lines): break
            line = lines[line_num]
            line_num += 1
            
            words = line.split()
            if len(words)==0: continue

            if (words[0] == 'Frames:'):
                self.frame_num = int(words[1])
            elif (words[0] == 'Frame' and words[1] == 'Time:'):
                self.frame_time = float(words[2])
                for i in range(0, self.frame_num):
                    line = lines[line_num]
                    line_num += 1
                    
                    self.motion.push_posture(line)
            elif (words[0] == 'JOINT' or words[0] == 'ROOT'):
                self.joint_num += 1
                self.joint_list.append(words[1])
            elif (words[0] == '{'):
                new_joint = Joint()
                cur_joint.add_child(new_joint)
                new_joint.parent = cur_joint
                cur_joint = new_joint
            elif (words[0] == '}'):
                cur_joint = cur_joint.parent
            elif (words[0] == 'End'):
                isEndEffector = True
            elif (words[0] == 'OFFSET'):
                cur_joint.offset = [float(words[1]), float(words[2]), float(words[3])]
                if (isEndEffector):
                    cur_joint.isEndEffector = True
                    isEndEffector = False
                    self.motion.push_joint(cur_joint)
                    continue
                # If it is not end effector
                line = lines[line_num]
                line_num += 1
                words = line.split()
                if (words[0] != 'CHANNELS'):
                    print("ERROR: OFFSET 다음에 무조건 CHANNELS 나오는 것으로 생각하고 구현하였는데 예외상황 발생")
                    return
                
                cur_joint.channel_num = int(words[1])
                channels = []
                for i in range(0, cur_joint.channel_num):
                    chan_type = words[2+i].upper()
                    channels.append(chan_type)
                cur_joint.set_channels(channels)

                self.motion.push_joint(cur_joint)

        return True

    def print_info(self):
        print("File name : ", self.name.split('\\')[-1])
        print("Number of frames : ", self.frame_num)
        print("FPS (1/FrameTime) : ", 1/self.frame_time)
        print("Number of joints : ", self.joint_num)
        print("List of all joint names : ", self.joint_list)

class Renderer:
    def __init__ (self, bvh_file):
        self.bvh_file = bvh_file
        self.cur_frame = 0
        self.animating_mode = False
        self.current_posture = Posture("")
        self.posture_idx = 0
        # Projection type : Perspective(True), Orthogonal(False)
        self.projection_type = True
        self.target = np.array([0., 0., 0.])
        self.u = np.array([1, 0, 0])
        self.v = np.array([0, 1, 0])
        self.w = np.array([0, 0, 1])
        self.azimuth = 45.
        self.elevation = 36.
        self.button_left_pressed = False
        self.button_right_pressed = False
        self.cur_xpos = 0
        self.cur_ypos = 0
        self.zooming = 0
        self.aspect = 1.0
        self.viewport_w = 800
        self.viewport_h = 800

    def set_viewport_size(self, width, height):
        self.viewport_w = width
        self.viewport_h = height
        self.aspect = float(width / height)

    def get_bvh(self):
        return self.bvh_file

    def set_bvh(self, bvh_file):
        self.bvh_file = bvh_file
        self.cur_frame = 0

    def show_next_frame(self):
        if self.animating_mode:
            self.cur_frame += 1
            if self.cur_frame >= self.bvh_file.frame_num: self.cur_frame = 0

    def start_or_stop_animation(self):
        self.animating_mode = not self.animating_mode

    def flip_projection(self):
        self.projection_type = not self.projection_type

    def change_orbit(self, xpos, ypos):
        self.azimuth += self.cur_xpos - xpos
        self.elevation -= self.cur_ypos - ypos

    def change_panning(self, xpos, ypos):
        self.target += 0.008*(self.cur_xpos - xpos)*self.u
        self.target += 0.008*(ypos - self.cur_ypos)*self.v

    def set_cur_pos(self, xpos, ypos):
        self.cur_xpos = xpos
        self.cur_ypos = ypos

    def zoom(self, yoffset):
        # zoom in 하면 (0, 1), zoom out하면 (0, -1)
        self.zooming += yoffset
        
    def drawGrid(self):
        glBegin(GL_LINES)
        glColor3ub(211, 211, 211) # light gray
        line = 15
        for i in range(-line, line):
            glVertex3fv(np.array([i, 0, -line]))
            glVertex3fv(np.array([i, 0, line]))
            glVertex3fv(np.array([-line, 0, i]))
            glVertex3fv(np.array([line, 0, i]))
        glEnd()

    def drawFrameRecursively(self, joint):
        glPushMatrix()
        glBegin(GL_LINES)
        glVertex3fv(np.array([0, 0, 0]))
        glVertex3fv(np.array([joint.offset[0], joint.offset[1], joint.offset[2]]))
        glEnd()
        glTranslatef(joint.offset[0], joint.offset[1], joint.offset[2])
        for chanType in joint.channels:
            if chanType == 'XPOSITION':
                Tx = float(self.current_posture.get(self.posture_idx))
                self.posture_idx += 1
                glTranslatef(Tx, 0, 0)
            elif chanType == 'YPOSITION':
                Ty = float(self.current_posture.get(self.posture_idx))
                self.posture_idx += 1
                glTranslatef(0, Ty, 0)
            elif chanType == 'ZPOSITION':
                Tz = float(self.current_posture.get(self.posture_idx))
                self.posture_idx += 1
                glTranslatef(0, 0, Tz)
            elif chanType == 'XROTATION':
                Rx = float(self.current_posture.get(self.posture_idx))
                self.posture_idx += 1
                glRotatef(Rx, 1, 0, 0)
            elif chanType == 'YROTATION':
                Ry = float(self.current_posture.get(self.posture_idx))
                self.posture_idx += 1
                glRotatef(Ry, 0, 1, 0)
            elif chanType == 'ZROTATION':
                Rz = float(self.current_posture.get(self.posture_idx))
                self.posture_idx += 1
                glRotatef(Rz, 0, 0, 1)
        
        for child in joint.children:
            self.drawFrameRecursively(child)
        glPopMatrix()
        
    def renderBvh(self):
        self.current_posture = self.bvh_file.get_posture(self.cur_frame)
        
        self.posture_idx = 0
        root = self.bvh_file.get_root()
        self.drawFrameRecursively(root)

    def init(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) 
        glLoadIdentity()

        glViewport(0, 0, self.viewport_w, self.viewport_h)
        if self.projection_type:
            gluPerspective(45, self.aspect, 2, 200.0)
        else:
            glOrtho(-10, 10, -10, 10, -20, 20)
            
        distance = 10
        r_azimuth = np.radians(self.azimuth)
        r_elevation = np.radians(self.elevation)
        tmp = distance*np.cos(r_elevation)
        camera = np.array([self.target[0] + tmp*np.sin(r_azimuth), self.target[1] + distance*np.sin(r_elevation), self.target[2] + tmp*np.cos(r_azimuth)])
        Ma = np.array([[np.cos(r_azimuth), 0., np.sin(r_azimuth)],
                       [0., 1., 0.],
                       [-np.sin(r_azimuth), 0., np.cos(r_azimuth)]])
        Me = np.array([[1., 0., 0.],
                      [0., np.cos(r_elevation), np.sin(r_elevation)],
                      [0., -np.sin(r_elevation), np.cos(r_elevation)]])
        M = Ma @ Me
        self.u = M @ np.array([1., 0., 0.])
        self.v = M @ np.array([0., 1., 0.])
        self.w = M @ np.array([0., 0., 1.])
        self.u = self.u / np.sqrt(np.dot(self.u, self.u))
        self.v = self.v / np.sqrt(np.dot(self.v, self.v))
        self.w = self.w / np.sqrt(np.dot(self.w, self.w))
        camera -= self.zooming*self.w


        Mv = np.array([[self.u[0], self.u[1], self.u[2], -np.dot(self.u, camera)],
                       [self.v[0], self.v[1], self.v[2], -np.dot(self.v, camera)],
                       [self.w[0], self.w[1], self.w[2], -np.dot(self.w, camera)],
                       [0, 0, 0, 1]])
        glMultMatrixf(Mv.T)
        
        renderer.drawGrid()
        glEnable(GL_NORMALIZE)
###########################################################
            
    
def render():
    global renderer
    renderer.init()
    
    if (renderer.get_bvh().name != ""):
        glDisable(GL_LIGHTING)
        renderer.renderBvh()
        
    glDisable(GL_LIGHTING)


##################################################################
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

    def paintGL(self):
        render()

    def resizeGL(self, width, height):
        global renderer
        renderer.set_viewport_size(width, height)
    
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self) # call the init for the parent class

        self.resize(800, 800)
        self.setWindowTitle('BVH Viewer')
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.glWidget = GLWidget(self)
        self.time_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.time_input = QtWidgets.QLineEdit()
        self.initGUI()
        
        timer = QtCore.QTimer(self)
        timer.setInterval(10) # period, in milliseconds
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

        self.frame_timer = QtCore.QTimer(self)
        self.frame_timer.timeout.connect(self.update_frame)


    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        gui_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(gui_layout)
        self.setCentralWidget(central_widget)
        gui_layout.addWidget(self.glWidget)

        play_btn = QtWidgets.QPushButton("Play/Stop", self)
        play_btn.clicked.connect(self.play_btn_clicked)
        gui_layout.addWidget(play_btn)

        self.time_slider.setRange(0, 1)
        self.time_slider.valueChanged.connect(lambda val: self.set_frame(val))
        gui_layout.addWidget(self.time_slider)

        self.time_input.returnPressed.connect(self.set_frame_by_input)
        gui_layout.addWidget(self.time_input)

    def show_alert(self, message):
        QtWidgets.QMessageBox.question(self, 'Error', message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.NoButton)

    def set_frame_by_input(self):
        global renderer
        val = self.time_input.text()
        
        if not val.isdigit():
            self.show_alert("Enter decimal number")
            return
        val = int(val)
        if val < 0:
            self.show_alert("Enter positive number")
            return
        elif val >= renderer.get_bvh().get_frame_num():
            self.show_alert("Frame number cannot exceed bvh file's frame number")
            return
        self.set_frame(val)
        
    def play_btn_clicked(self):
        global renderer
        renderer.start_or_stop_animation()
    def set_frame(self, val):
        renderer.cur_frame = val
        
    def keyPressEvent(self, event):
        global renderer
        
        if event.key() == QtCore.Qt.Key_R:
            renderer.start_or_stop_animation()
        elif event.key() == QtCore.Qt.Key_V:
            renderer.flip_projection()
            
    def wheelEvent(self, event):
        yoffset = 0.005 * event.angleDelta().y()
        global renderer
        renderer.zoom(yoffset)
        

    def mousePressEvent(self, event):
        global renderer
        xpos = event.x()
        ypos = event.y()
        if event.buttons() & QtCore.Qt.RightButton:
            renderer.button_right_pressed = True
            renderer.set_cur_pos(xpos, ypos)
        elif event.buttons() & QtCore.Qt.LeftButton:
            renderer.button_left_pressed = True
            renderer.set_cur_pos(xpos, ypos)

    def mouseReleaseEvent(self, event):
        global renderer
        renderer.button_right_pressed = False
        renderer.button_left_pressed = False
    
    def mouseMoveEvent(self, event):
        global renderer
        xpos = event.x()
        ypos = event.y()
        if renderer.button_left_pressed:
            renderer.change_orbit(xpos, ypos)
            renderer.set_cur_pos(xpos, ypos)
        elif renderer.button_right_pressed:
            renderer.change_panning(xpos, ypos)
            renderer.set_cur_pos(xpos, ypos)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        global renderer

        renderer.animating_mode = False
        renderer.get_bvh().joint_num = 0
        renderer.get_bvh().joint_list = []

        file_name =  [u.toLocalFile() for u in event.mimeData().urls()][0]
        renderer.set_bvh(BvhFile(file_name))
        success = renderer.get_bvh().parse()
        if not success: return
        self.time_slider.setRange(0, renderer.get_bvh().get_frame_num()-1)
        self.frame_timer.stop()
        self.frame_timer.setInterval(int(renderer.get_bvh().frame_time * 1000))
        self.frame_timer.start()

    def update_frame(self):
        global renderer
        self.time_slider.setValue(renderer.cur_frame)
        self.time_input.setText(str(renderer.cur_frame))
        renderer.show_next_frame()
        
        
        
##################################################################
def main():
    global renderer
    bvh_file = BvhFile("")
    renderer = Renderer(bvh_file)

    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
