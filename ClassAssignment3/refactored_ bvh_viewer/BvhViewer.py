import glfw
import sys
import numpy as np
import pytest
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
# For PyQt5
from PyQt5 import QtCore
from PyQt5 import QtGui 
from PyQt5 import QtOpenGL 
from PyQt5 import QtWidgets

###########################################################
# Global renderer
viewer = None
win = None

###########################################################
# Unit test
def test_pytest():
    assert 3 == 3

# Test skeleton's joint count is correct
def test_parsed_joint_num_is_correct():
    motion = Motion("./unit_test.bvh")
    assert len(motion.skeleton.joints) == 57

# Test root joint is correct
def test_get_root():
    motion = Motion("./unit_test.bvh")
    root = motion.get_root()
    assert root.channel_num == 6
    assert root.offset == [0, 0, 0]
    assert root.isEndEffector == False
    assert len(root.children) == 3

# Test parsed joint tree is made corretly
def test_joint_tree_is_correct():
    motion = Motion("./unit_test.bvh")
    root = motion.get_root()
    first_child = root.children[0]
    assert first_child.offset == [0, 20.6881, -0.73152]
    assert len(first_child.children) == 1
    assert first_child.children[0].children[0].children[0].children[0].children[0].isEndEffector == True

# Test parsed postures count is equal to frame number of bvh file
def test_parsed_postures_count_is_correct():
    motion = Motion("./unit_test.bvh")
    assert motion.frame_num == len(motion.postures)

# Test parsed posture's data count is equal to skeleton's total channel count
def test_parsed_posture_data_count_is_correct():
    motion = Motion("./unit_test.bvh")
    assert len(motion.postures[0].values) == 132

# Test parsed posture data is correct
def test_parsed_posture_data_is_correct():
    motion = Motion("./unit_test.bvh")
    assert motion.postures[0].get_value(0) == 53.6842

###########################################################
    
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

    def get_children(self):
        return children

    def set_parent(self, parent):
        self.parent = parent

    def set_offset(self, x, y, z):
        self.offset = [x, y, z]

###########################################################
        
class Skeleton:
    def __init__(self):
        self.joints = []

    def push_joint(self, joint):
        self.joints.append(joint)

    def get_root_joint(self):
        return self.joints[0]

###########################################################
    
class Posture:
    def __init__(self, line):
        self.values = []
        values_str = line.split()
        for value in values_str:
            self.values.append(float(value))
            
    def get_value(self, idx):
        return self.values[idx]

###########################################################   
    
class Motion:
    def __init__(self, file_name):
        self.name = file_name
        self.skeleton = Skeleton()
        self.postures = []
        self.frame_num = 0
        self.frame_time = 0
        self.joint_num = 0
        self.joint_list = []
        if file_name != "":
            self.parse()

    def get_value_in_frame(self, frame, idx):
        return self.postures[frame].get_value(idx)

    def get_frame_num(self):
        return self.frame_num

    def push_joint(self, joint):
        self.skeleton.push_joint(joint)
        
    def get_posture(self, frame):
        return self.postures[frame]
    
    def get_root(self):
        return self.skeleton.get_root_joint()

    def parse(self):
        # if file extension is not bvh, return error message
        file_name = self.name.split('\\')[-1]
        extension = file_name.split('.')[-1]
        if (extension != 'bvh'):
            global win
            self.name = ""
            if win:
                win.show_alert("Drag and drop only .bvh file")
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
                    posture = Posture(line)
                    self.postures.append(posture)
            elif (words[0] == 'JOINT' or words[0] == 'ROOT'):
                self.joint_num += 1
                self.joint_list.append(words[1])
            elif (words[0] == '{'):
                new_joint = Joint()
                cur_joint.add_child(new_joint)
                new_joint.set_parent(cur_joint)
                cur_joint = new_joint
            elif (words[0] == '}'):
                cur_joint = cur_joint.parent
            elif (words[0] == 'End'):
                isEndEffector = True
            elif (words[0] == 'OFFSET'):
                cur_joint.set_offset(float(words[1]), float(words[2]), float(words[3]))
                if (isEndEffector):
                    cur_joint.isEndEffector = True
                    isEndEffector = False
                    self.push_joint(cur_joint)
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

                self.push_joint(cur_joint)

        return True

    def print_info(self):
        print("File name : ", self.name.split('\\')[-1])
        print("Number of frames : ", self.frame_num)
        print("FPS (1/FrameTime) : ", 1/self.frame_time)
        print("Number of joints : ", self.joint_num)
        print("List of all joint names : ", self.joint_list)

###########################################################
        
class CameraController:
    def __init__(self):
        # Projection type : Perspective(True), Orthogonal(False)
        self.projection_type = True
        self.target = np.array([0., 0., 0.])
        self.u = np.array([1, 0, 0])
        self.v = np.array([0, 1, 0])
        self.w = np.array([0, 0, 1])
        self.azimuth = 45.
        self.elevation = 36.
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

    def flip_projection(self):
        self.projection_type = not self.projection_type

    def change_orbit(self, xpos, ypos):
        self.azimuth += self.cur_xpos - xpos
        self.elevation -= self.cur_ypos - ypos

    def change_panning(self, xpos, ypos):
        self.target += 0.03*(self.cur_xpos - xpos)*self.u
        self.target += 0.03*(ypos - self.cur_ypos)*self.v

    def set_cur_pos(self, xpos, ypos):
        self.cur_xpos = xpos
        self.cur_ypos = ypos

    def zoom(self, yoffset):
        # zoom in 하면 (0, 1), zoom out하면 (0, -1)
        self.zooming += yoffset

    def init_viewport(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL ) 
        glLoadIdentity()

        glViewport(0, 0, self.viewport_w, self.viewport_h)
        if self.projection_type:
            gluPerspective(45, self.aspect, 2, 200)
        else:
            glOrtho(-10, 10, -10, 10, -50, 50)
            
        distance = 15
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
        
###########################################################
        
class BvhRenderer:
    def __init__ (self, bvh_motion):
        self.bvh_motion = bvh_motion
        self.cur_frame = 0
        self.rendering_frame = 0
        self.posture_idx = 0
        self.animating_mode = False
        
    def get_bvh(self):
        return self.bvh_motion

    def set_bvh(self, bvh_motion):
        self.bvh_motion = bvh_motion
        self.cur_frame = 0

    def set_next_frame(self):
        if self.animating_mode:
            self.cur_frame += 1
            if self.cur_frame >= self.bvh_motion.frame_num: self.cur_frame = 0

    def start_or_stop_animation(self):
        self.animating_mode = not self.animating_mode

    def drawFrameRecursively(self, joint):
        glPushMatrix()

        # Draw link.
        glBegin(GL_LINES)
        glVertex3fv(np.array([0, 0, 0]))
        glVertex3fv(np.array([joint.offset[0], joint.offset[1], joint.offset[2]]))
        glEnd()

        # Translate or Rotate joint offset.
        glTranslatef(joint.offset[0], joint.offset[1], joint.offset[2])
        for chanType in joint.channels:
            val = float(self.bvh_motion.get_value_in_frame(self.rendering_frame, self.posture_idx))
            self.posture_idx += 1
            if chanType == 'XPOSITION':
                glTranslatef(val, 0, 0)
            elif chanType == 'YPOSITION':
                glTranslatef(0, val, 0)
            elif chanType == 'ZPOSITION':
                glTranslatef(0, 0, val)
            elif chanType == 'XROTATION':
                glRotatef(val, 1, 0, 0)
            elif chanType == 'YROTATION':
                glRotatef(val, 0, 1, 0)
            elif chanType == 'ZROTATION':
                glRotatef(val, 0, 0, 1)
        
        for child in joint.children:
            self.drawFrameRecursively(child)
        glPopMatrix()
        
    def renderBvh(self):
        self.rendering_frame = self.cur_frame
        self.posture_idx = 0
        root = self.bvh_motion.get_root()
        self.drawFrameRecursively(root)

    def draw_grid(self):
        glBegin(GL_LINES)
        line = 20
        for i in range(-line, line+1):
            glVertex3fv(np.array([i, 0, -line]))
            glVertex3fv(np.array([i, 0, line]))
            glVertex3fv(np.array([-line, 0, i]))
            glVertex3fv(np.array([line, 0, i]))
        glEnd()

##################################################################

class Viewer:
    def __init__(self, bvh_motion):
        self.renderer = BvhRenderer(bvh_motion)
        self.camera_controller = CameraController()
        
    def render(self):
        self.camera_controller.init_viewport()
        self.renderer.draw_grid()

        if (self.renderer.get_bvh().name != ""):
            self.renderer.renderBvh()

##################################################################
            
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

    def paintGL(self):
        global viewer
        viewer.render()

    def resizeGL(self, width, height):
        global viewer
        viewer.camera_controller.set_viewport_size(width, height)
    
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
        self.play_btn = QtWidgets.QPushButton("Play", self)
        self.initGUI()
        
        timer = QtCore.QTimer(self)
        timer.setInterval(10) # period, in milliseconds
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

        self.frame_timer = QtCore.QTimer(self)
        self.frame_timer.timeout.connect(self.update_frame)

        self.button_left_pressed = False
        self.button_right_pressed = False



    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        gui_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(gui_layout)
        self.setCentralWidget(central_widget)
        gui_layout.addWidget(self.glWidget)

        self.play_btn.clicked.connect(self.play_btn_clicked)
        gui_layout.addWidget(self.play_btn)

        self.time_slider.setRange(0, 1)
        self.time_slider.valueChanged.connect(lambda val: self.set_frame(val))
        gui_layout.addWidget(self.time_slider)

        self.time_input.returnPressed.connect(self.set_frame_by_input)
        gui_layout.addWidget(self.time_input)

    def show_alert(self, message):
        QtWidgets.QMessageBox.question(self, 'Error', message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.NoButton)

    def set_frame_by_input(self):
        global viewer
        val = self.time_input.text()
        
        if not val.isdigit():
            self.show_alert("Enter decimal number")
            return
        val = int(val)
        if val < 0:
            self.show_alert("Enter positive number")
            return
        elif val >= viewer.renderer.get_bvh().get_frame_num():
            self.show_alert("Frame number cannot exceed bvh file's frame number")
            return
        self.set_frame(val)
        
    def play_btn_clicked(self):
        global viewer
        viewer.renderer.start_or_stop_animation()
        text = "Play"
        if viewer.renderer.animating_mode:
            text = "Pause"
        self.play_btn.setText(text)
        
    def set_frame(self, frame):
        global viewer
        viewer.renderer.cur_frame = frame
        self.time_input.setText(str(frame))
        
    def keyPressEvent(self, event):
        global viewer
        
        if event.key() == QtCore.Qt.Key_R:
            viewer.renderer.start_or_stop_animation()
        elif event.key() == QtCore.Qt.Key_V:
            viewer.camera_controller.flip_projection()
            
    def wheelEvent(self, event):
        yoffset = 0.005 * event.angleDelta().y()
        global viewer
        viewer.camera_controller.zoom(yoffset)
        

    def mousePressEvent(self, event):
        global viewer
        xpos = event.x()
        ypos = event.y()
        if event.buttons() & QtCore.Qt.RightButton:
            self.button_right_pressed = True
            viewer.camera_controller.set_cur_pos(xpos, ypos)
        elif event.buttons() & QtCore.Qt.LeftButton:
            self.button_left_pressed = True
            viewer.camera_controller.set_cur_pos(xpos, ypos)

    def mouseReleaseEvent(self, event):
        self.button_right_pressed = False
        self.button_left_pressed = False
    
    def mouseMoveEvent(self, event):
        global viewer
        xpos = event.x()
        ypos = event.y()
        if self.button_left_pressed:
            viewer.camera_controller.change_orbit(xpos, ypos)
            viewer.camera_controller.set_cur_pos(xpos, ypos)
        elif self.button_right_pressed:
            viewer.camera_controller.change_panning(xpos, ypos)
            viewer.camera_controller.set_cur_pos(xpos, ypos)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        global viewer

        viewer.renderer.animating_mode = False
        viewer.renderer.get_bvh().joint_num = 0
        viewer.renderer.get_bvh().joint_list = []

        file_name =  [u.toLocalFile() for u in event.mimeData().urls()][0]
        viewer.renderer.set_bvh(Motion(file_name))
        
        self.time_slider.setRange(0, viewer.renderer.get_bvh().get_frame_num()-1)
        self.frame_timer.stop()
        self.frame_timer.setInterval(int(viewer.renderer.get_bvh().frame_time * 1000))
        self.frame_timer.start()

    def update_frame(self):
        global viewer
        self.time_slider.setValue(viewer.renderer.cur_frame)
        if viewer.renderer.animating_mode:
            self.time_input.setText(str(viewer.renderer.cur_frame))
        viewer.renderer.set_next_frame()
        
##################################################################
def main():
    global viewer, win
    bvh_motion = Motion("")
    viewer = Viewer(bvh_motion)

    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
