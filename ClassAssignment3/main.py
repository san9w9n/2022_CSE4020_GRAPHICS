import os
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

################################################
#               GLOBAL VARIABLE

dist = 5.
azimuth = 45.
GRIDFACTOR = 5.
elevation = 36.

mouseX = 0
mouseY = 0

currentObject = None
animateMode = False
boxMode = True
orthMode = False
lClick = False
rClick = False
nothing = True
downloadedBvhFile = False
canDrawObj = False
objMode = False
objFileNames = []

ref = np.array([0., 0., 0.])
u = np.array([1., 0., 0.])
v = np.array([0., 1., 0.])
w = np.array([0., 0., 1.])
up = np.array([0., 1., 0.])

motion = []

################################################
#                 DRAW BOX

boxVarr = np.array([
            (-0.5773502691896258,0.5773502691896258,0.5773502691896258),
            ( -0.02 ,  0 ,  0.02 ),
            (0.8164965809277261,0.4082482904638631,0.4082482904638631),
            (  0.02 , 0 ,  0.02 ),
            (0.4082482904638631,-0.4082482904638631,0.8164965809277261),
            (  0.02 ,  -1 ,  0.02 ),

            (-0.4082482904638631,-0.8164965809277261,0.4082482904638631),
            ( -0.02 ,  -1 ,  0.02 ),
            (-0.4082482904638631,0.4082482904638631,-0.8164965809277261),
            ( -0.02 , 0 ,  -0.02 ),
            (0.4082482904638631,0.8164965809277261,-0.4082482904638631),
            (  0.02 , 0 ,  -0.02 ),
            (0.5773502691896258,-0.5773502691896258,-0.5773502691896258),
            ( 0.02 ,  -1 , -0.02 ),
            (-0.8164965809277261,-0.4082482904638631,-0.4082482904638631),
            (  -0.02 ,  -1 , -0.02 ),
        ], 'float32')
boxIarr = np.array([
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
            (0,4,7)
        ], dtype = 'int32')

def drawCube():
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*boxIarr.itemsize, boxVarr)
    glVertexPointer(3, GL_FLOAT, 6*boxIarr.itemsize, ctypes.c_void_p(boxVarr.ctypes.data + 3*boxIarr.itemsize))
    glDrawElements(GL_TRIANGLES, boxIarr.size, GL_UNSIGNED_INT, boxIarr)
    

################################################
#        DEFINITION OF CLASS FOR BVH

class Node:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.offset = np.zeros(3)
        self.orderOfChannel = []
        self.indexOfChannel = []
        self.children = []

    def appendChild(self, child):
        self.children.append(child)
    
    def drawOne(self):
        glTranslatef(self.offset[0], self.offset[1], self.offset[2]) 
        if boxMode or (canDrawObj and objMode):
            if self.parent:
                x, y, z = self.offset[0], self.offset[1], self.offset[2] 
                offset = getRootOfSumOfSquare(x, y, z)
                degreeVector = np.cross(getUnit(self.offset), np.array([0, 1, 0]))
                x, y, z = degreeVector[0], degreeVector[1], degreeVector[2]
                innerDegree = getRootOfSumOfSquare(x, y, z)
                degree = np.rad2deg(np.arcsin(innerDegree))
                if np.dot(self.offset, np.array([0, 1, 0])) > 0:
                    degree = 180 - degree
                glPushMatrix()
                glRotatef(degree, degreeVector[0], degreeVector[1], degreeVector[2])
                if downloadedBvhFile:
                    glScalef(30, -offset, 30)
                else:
                    glScalef(1, -offset, 1) 
                if canDrawObj and objMode:
                    glScalef(1.2, 1.3, 1.2)
                    objname = self.name.lower().replace(" ", "") + ".obj"
                    if objname == "spine.obj":
                        glScalef(0.5, 0.5, 0.5)
                    for idx, name in enumerate(objFileNames):
                        if (name == objname):
                            drawObjMesh(idx)
                            break
                else:
                    drawCube()
                glPopMatrix()
        elif self.parent:
            glBegin(GL_LINES)
            glVertex3fv(-self.offset)
            glVertex3fv(np.array([0.,0.,0.]))
            glEnd()

        
    def tPose(self):
        glPushMatrix()
        self.drawOne()
        for child in self.children:
            child.tPose()
        glPopMatrix()

    def animation(self, i):
        glPushMatrix()
        self.drawOne()
        for j, typeOf in zip(self.indexOfChannel, self.orderOfChannel):
            upperType = typeOf.upper()
            m = motion[i][j]
            if upperType == 'XROTATION':
                glRotatef(m, 1, 0, 0)
            elif upperType == 'YROTATION':
                glRotatef(m, 0, 1, 0)
            elif upperType == 'ZROTATION':
                glRotatef(m, 0, 0, 1)
            elif upperType == 'XPOSITION':
                glTranslatef(m, 0, 0)
            elif upperType == 'YPOSITION':
                glTranslatef(0, m, 0)
            elif upperType == 'ZPOSITION':
                glTranslatef(0, 0, m) 
        for child in self.children:
            child.animation(i)
        glPopMatrix()

class Bvh:
    def __init__(self, filename, bvhPlainTexts):
        self.filename = filename
        self.nodes = {}
        self.root = None
        self.frames = 0
        self.fps = 0

        self.parseBvhPlainTexts(bvhPlainTexts)
    
    def parseBvhPlainTexts(self, bvhPlainTexts):
        motionIndex = bvhPlainTexts.upper().find("MOTION")
        if motionIndex < 0:
            raise Exception("No Motion section.")
        motionString = bvhPlainTexts[motionIndex:motionIndex+6]
        hierPlainTexts, motionPlainTexts = bvhPlainTexts.split(motionString)
        self.parseHierPlainTexts(hierPlainTexts)
        self.parseMotionPlainTexts(motionPlainTexts)
            
    def parseHierPlainTexts(self, hierPlainTexts):
        linesOfHierPlainTexts = hierPlainTexts.split('\n')
        stackOfNodes = []
        cidx = 0
        for line in linesOfHierPlainTexts:
            words = line.strip().split(" ")
            lengthOfWords = len(words)
            if not words or lengthOfWords == 0:
                continue
            opcode = words[0].upper()
            if opcode == "ROOT":
                nameOfNode = words[1]
                node = Node(nameOfNode, None)
                self.root = node
                self.nodes[nameOfNode] = node
                stackOfNodes.append(node)
            elif opcode == "JOINT":
                nameOfNode = words[1]
                if (len(stackOfNodes) == 0):
                    raise Exception("Stack of nodes is empty. (JOINT)")
                parent = stackOfNodes[-1]
                node = Node(nameOfNode, parent)
                self.nodes[nameOfNode] = node
                parent.appendChild(node)
                stackOfNodes.append(node)
            elif opcode == "CHANNELS":
                if (len(stackOfNodes) == 0):
                    raise Exception("Stack of nodes is empty. (CHANNELS)")
                for e in words[2:]:
                    stackOfNodes[-1].indexOfChannel.append(cidx)
                    stackOfNodes[-1].orderOfChannel.append(e)
                    cidx += 1
            elif opcode == "OFFSET":
                if (len(stackOfNodes) == 0):
                    raise Exception("Stack of nodes is empty. (OFFSET)")
                for i, e in enumerate(words[1:], start=1):
                    offset = float(e)
                    stackOfNodes[-1].offset[i - 1] = offset
            elif opcode == "END":
                if len(stackOfNodes) == 0:
                    raise Exception("Stack of nodes is empty. (END)")
                nameOfLastNode = f"End Of {stackOfNodes[-1].name}"
                lastNode = Node(nameOfLastNode, stackOfNodes[-1])
                self.nodes[nameOfLastNode] = lastNode
                stackOfNodes[-1].appendChild(lastNode)
                stackOfNodes.append(lastNode)
            elif opcode == "}":
                if len(stackOfNodes) == 0:
                    raise Exception("Stack of nodes is empty. (POP)")
                stackOfNodes.pop()
   
    def parseMotionPlainTexts(self, motionPlainTexts):
        global motion
        motion = []
        lines = motionPlainTexts.split("\n")
        for line in lines:
            if len(line) == 0:
                continue
            words = line.replace("\n", "").strip().split()
            upperLine = line.upper()
            if upperLine.find("TIME") >= 0 and upperLine.find("FRAME") >= 0:
                self.fps = round(1 / float(words[2]))
                continue
            if upperLine.find("FRAMES") >= 0:
                self.frames = int(words[1])
                continue
            listOfFloats = []
            for word in words:
                try:
                    floatWord = float(word)
                    listOfFloats.append(floatWord)
                except:
                    pass
            motion.append(listOfFloats)

    def drawTPose(self):
        glPushMatrix()
        if downloadedBvhFile:
            glScalef(.03, .03, .03)
        self.root.tPose()
        glPopMatrix()
        
    def drawAnimation(self):
        idx = int((glfw.get_time() - timeOfPressSpace) * self.fps) % self.frames
        glPushMatrix()
        if downloadedBvhFile:
            glScalef(.03, .03, .03)
        self.root.animation(idx)
        glPopMatrix()
    
    def __str__(self):
        filename = f"File name : {self.filename}\n"
        numOfFrames = f"Number of frames : {self.frames}\n"
        fps = f"FPS : {self.fps}\n"
        numOfNodes = f"Number of joints : {len(self.nodes.keys())}\n"
        listOfAllNodes = "List of all joint names :\n"
        for name in self.nodes.keys():
            listOfAllNodes += f"\t{name}\n"
        return filename + numOfFrames + fps + numOfNodes + listOfAllNodes

################################################
#              DRAW OBJ FILE


varrList, narrList = [], []
offsetList = np.empty((0, 3), np.float32)

def getStuffsForDrawMesh(path):
    global varrList, narrList
    threeVertexCnt = 0
    fourVertexCnt = 0
    moreVertexCnt = 0

    iarr = np.empty((0, 3), dtype=np.int32)
    narr = np.empty((0, 3), dtype=np.float32)
    v_varr = np.empty((0, 3), dtype=np.float32)
    v_narr = np.empty((0, 3), dtype=np.float32)

    with open(path, 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            elements = line.strip().split()
            if (not elements or len(elements) == 0):
                continue

            if elements[0] == "v":
                vertex = np.array([[float(elements[1]), float(
                    elements[2]), float(elements[3])]], dtype=np.float32)
                v_varr = np.append(v_varr, vertex, axis=0)
                continue

            if elements[0] == "vn":
                vertex = np.array([getUnit(np.array([float(elements[1]), float(
                    elements[2]), float(elements[3])], dtype=np.float32))], dtype=np.float32)
                v_narr = np.append(v_narr, vertex, axis=0)
                continue

            if elements[0] == "f":
                length = len(elements)
                if (length == 4):
                    threeVertexCnt += 1
                elif (length == 5):
                    fourVertexCnt += 1
                elif (length > 5):
                    moreVertexCnt += 1

                vertexIdxes = np.empty((0, 3), dtype=int)
                normals = np.empty((0, 3), dtype=np.float32)
                for e in elements[1:]:
                    faceInfo = e.split('/')
                    if len(faceInfo) >= 1:
                        vertexIdx = int(faceInfo[0]) - 1
                        vertexIdxes = np.append(vertexIdxes, vertexIdx)
                    if len(faceInfo) == 2:
                        normalIdx = int(
                            faceInfo[1]) - 1 if faceInfo[1] != "" else 0
                        normals = np.append(
                            normals, [v_narr[normalIdx]], axis=0)
                    if len(faceInfo) >= 3:
                        normalIdx = int(
                            faceInfo[2]) - 1 if faceInfo[2] != "" else 0
                        normals = np.append(
                            normals, [v_narr[normalIdx]], axis=0)
                idxLength = len(vertexIdxes)
                if idxLength == 3:
                    iarr = np.append(iarr, np.array([vertexIdxes]), axis=0)
                    for normal in normals:
                        narr = np.append(narr, np.array([normal]), axis=0)
                elif idxLength > 3:
                    for i in range(2, idxLength):
                        idx = np.array(
                            [vertexIdxes[0], vertexIdxes[i-1], vertexIdxes[i]])
                        iarr = np.append(iarr, np.array([idx]), axis=0)
                        normal = np.array(
                            [np.array(normals[0]), np.array(normals[i-1]), np.array(normals[i])])
                        narr = np.append(narr, normal, axis=0)
        varr = np.empty((0, 3), dtype=np.float32)
        for idx in iarr:
            for i in idx:
                varr = np.append(varr, np.array([v_varr[i]]), axis=0)
        varrList.append(varr)
        narrList.append(narr)


def drawObjMesh(idx):
    glScalef(0.3, 0.3, 0.3)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 3 * narrList[idx].itemsize, narrList[idx])
    glVertexPointer(3, GL_FLOAT, 3 * varrList[idx].itemsize, varrList[idx])
    glDrawArrays(GL_TRIANGLES, 0, int(varrList[idx].size / 3))

def openObjFiles():
    global canDrawObj, varrList, narrList, objMode
    varrList, narrList = [], []
    dirpath = os.path.dirname(__file__)
    for name in objFileNames:
        path = os.path.join(dirpath, name)
        try: getStuffsForDrawMesh(path)
        except:
            canDrawObj = False
            break
        canDrawObj = True
        objMode = True

################################################
#           CONVINIENT FUNCTIONS


def cosAzim():
    return np.cos(np.radians(azimuth))


def sinAzim():
    return np.sin(np.radians(azimuth))


def cosElev():
    return np.cos(np.radians(elevation))


def sinElev():
    return np.sin(np.radians(elevation))


def getUnit(num):
    denominator = np.sqrt(np.dot(num, num))
    if denominator == 0:
        return np.array([0, 0, 0])
    return num / denominator

def getRootOfSumOfSquare(x, y, z):
    return ((x*x) + (y*y) + (z*z)) ** 0.5

################################################
#          EVENT CALLBACK FUNCTION

def key_callback(window, key, scancode, action, mods):
    global orthMode, boxMode, timeOfPressSpace, animateMode, objMode
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_V:
        orthMode = not orthMode
    if key == glfw.KEY_1 and not objMode:
        boxMode = False
    if key == glfw.KEY_2 and not objMode:
        boxMode = True
    if key == glfw.KEY_SPACE:
        timeOfPressSpace = glfw.get_time()
        animateMode = not animateMode
    if key == glfw.KEY_O:
        if canDrawObj:
            objMode = not objMode
        else:
            objMode = False



def button_callback(window, button, action, mod):
    global lClick, rClick, mouseX, mouseY
    if button == glfw.MOUSE_BUTTON_LEFT:
        mouseX, mouseY = glfw.get_cursor_pos(window)
        lClick = (action == glfw.PRESS)
        rClick = False
    elif button == glfw.MOUSE_BUTTON_RIGHT:
        mouseX, mouseY = glfw.get_cursor_pos(window)
        rClick = (action == glfw.PRESS)
        lClick = False
    else:
        rClick = lClick = False


def cursor_callback(window, x, y):
    global ref, u, v, mouseX, mouseY, elevation, azimuth, up
    subX = mouseX - x
    subY = y - mouseY
    if (lClick):
        azimuth += subX*0.1
        elevation += subY*0.1
        if cosElev() < 0:
            up[1] = -1
        else:
            up[1] = 1
    elif (rClick):
        ref += (u * .01 * subX) + (v * .01 * subY)
    mouseX, mouseY = x, y


def scroll_callback(window, _, y):
    global dist
    if y:
        if dist-y <= 0:
            dist = 0
        else:
            dist -= y


def drop_callback(window, paths):
    global nothing, animateMode, objFileNames, currentObject, downloadedBvhFile, canDrawObj, objMode
    if (len(paths) == 0):
        return
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, paths[0])
    if filename.find(".bvh") == -1:
        print("The file is not .bvh file.")
        nothing = True
        canDrawObj = False
        objMode = False
        return
    downloadedBvhFile = filename.find("sample") < 0
    with open(filename, 'r') as f:
        objFileNames = []
        currentObject = Bvh(filename, f.read())
        for name in currentObject.nodes.keys():
            objName = name.lower().replace(' ', '')
            if objName.find("endof") < 0:
                objFileNames.append(f"{objName}.obj")
        print(currentObject)
        openObjFiles()
        nothing = False
        animateMode = False


################################################
#          SETTNGS FOR RENDERING

def setInitialBit():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

def getMyLookAt():
    global u, v, w
    eye = np.array([ref[0] + dist * cosElev() * sinAzim(),
                    ref[1] + dist * sinElev(),
                    ref[2] + dist * cosElev() * cosAzim()])

    w = getUnit(eye - ref)
    u = getUnit(np.cross(up, w))
    v = getUnit(np.cross(w, u))
    eyeU = -np.dot(u, eye)
    eyeV = -np.dot(v, eye)
    eyeW = -np.dot(w, eye)
    Mv = np.array([[u[0], v[0], w[0], 0],
                   [u[1], v[1], w[1], 0],
                   [u[2], v[2], w[2], 0],
                   [eyeU, eyeV, eyeW, 1]])
    return Mv


def setViewMode():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glMultMatrixf(getMyLookAt())


def setProjectionMode():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if (orthMode):
        glOrtho(-10, 10, -10, 10, -10, 10)
    else:
        gluPerspective(45, 1, 3, 20)


################################################
#              CONTROL LIGHTS

def enableLight():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_NORMALIZE)


def setLight():
    glPushMatrix()
    lightColor = (1., 0., 0., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    lightPos = (3., 4., 5., 1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    glPopMatrix()

    glPushMatrix()
    lightColor = (0., 1., 0., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    lightPos = (-2., 3., 1., 1.)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor)
    glPopMatrix()

    glPushMatrix()
    lightColor = (0., 0., 1., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    lightPos = (-2., -3., -5., 1.)
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT2, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLightColor)
    glPopMatrix()

def setObjectColor():
    objectColor = (1,1,1,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

def disableLight():
    glDisable(GL_LIGHTING)


################################################
#           DRAW GRID && AXIS && OBJECT

def drawAxis():
    glBegin(GL_LINES)

    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-GRIDFACTOR, 0., 0.]))
    glVertex3fv(np.array([GRIDFACTOR, 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,           0., 0.]))
    glVertex3fv(np.array([0., GRIDFACTOR, 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., -GRIDFACTOR]))
    glVertex3fv(np.array([0., 0.,  GRIDFACTOR]))

    glEnd()


def drawGrid():
    glBegin(GL_LINES)
    glColor3ub(255, 255, 255)
    e = -GRIDFACTOR
    arr = []
    while (e <= GRIDFACTOR+.2):
        arr.append(e)
        e += .2
    for p in arr:
        glVertex3fv(np.array([p, 0., GRIDFACTOR]))
        glVertex3fv(np.array([p, 0., -GRIDFACTOR]))
        glVertex3fv(np.array([GRIDFACTOR, 0.,  p]))
        glVertex3fv(np.array([-GRIDFACTOR, 0., p]))
    glEnd()

def drawBackGround():
    drawAxis()
    drawGrid()

################################################
#                RENDERING


def render():
    setInitialBit()
    setProjectionMode()
    setViewMode()
    drawBackGround()

    enableLight()
    setLight()
    setObjectColor()
    if not boxMode and not objMode:
        disableLight()
    
    if not nothing and currentObject:
        if animateMode:
            currentObject.drawAnimation()
        else:
            currentObject.drawTPose()
    disableLight()


################################################
#                 MAIN

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, "ClassAssignment3", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()