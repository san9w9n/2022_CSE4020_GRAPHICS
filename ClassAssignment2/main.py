from locale import normalize
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

orthMode = False
wireMode = True
hierMode = False
smooMode = True
lClick = False
rClick = False
nothing = True

ref = np.array([0., 0., 0.])
u = np.array([1., 0., 0.])
v = np.array([0., 1., 0.])
w = np.array([0., 0., 1.])
up = np.array([0., 1., 0.])

global varr, v_varr, smooNarr, iarr, narr
global treeVarr, treeV_Varr, treeSmooNarr, treeIarr, treeNarr
global duckVarr, duckV_Varr, duckSmooNarr, duckIarr, duckNarr
global eagleVarr, eagleV_Varr, eagleSmooNarr, eagleIarr, eagleNarr
global bearVarr, bearV_Varr, bearSmooNarr, bearIarr, bearNarr
global flyVarr, flyV_Varr, flySmooNarr, flyIarr, flyNarr

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


################################################
#          EVENT CALLBACK FUNCTION

def key_callback(window, key, scancode, action, mods):
    global orthMode, hierMode, wireMode, smooMode, nothing
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_H:
        hierMode = True
        nothing = False
    if key == glfw.KEY_V:
        orthMode = not orthMode
    if key == glfw.KEY_S:
        smooMode = not smooMode
    if key == glfw.KEY_Z:
        wireMode = not wireMode


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
    global hierMode, narr, v_varr, iarr, nothing, smooNarr, varr
    if (len(paths) == 0):
        return
    hierMode = False
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, paths[0])
    if filename.find(".obj") == -1:
        print("The file is not .obj file.")
        nothing = True
        return
    varr, v_varr, smooNarr, iarr, narr = getStuffsForDrawMesh(filename)
    nothing = False


################################################
#    GET ARRAYS OR ELEMENTS FOR DRAWING MESH

def getSmoothNarr(v_varr, iarr, narr):
    smooNarr = np.zeros((len(v_varr), 3), dtype=np.float32)
    varr = np.empty((0, 3), dtype=np.float32)
    j = 0
    for idx in iarr:
        for i in idx:
            varr = np.append(varr, np.array([v_varr[i]]), axis=0)
            smooNarr[i] += narr[j]
            j += 1
    for i in range(len(v_varr)):
        smooNarr[i] = getUnit(smooNarr[i])
    return varr, smooNarr


def getStuffsForDrawMesh(path):
    threeVertexCnt = 0
    fourVertexCnt = 0
    moreVertexCnt = 0

    iarr = np.empty((0, 3), dtype=np.int32)
    narr = np.empty((0, 3), dtype=np.float32)
    v_varr = np.empty((0, 3), dtype=np.float32)
    v_narr = np.empty((0, 3), dtype=np.float32)

    with open(path, 'r') as f:
        for line in f:
            try:
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
            except:
                print(f"sorry something's wrong while drawing {path}...")
                empthArr = np.empty((0, 3), dtype=np.float32)
                return empthArr, empthArr, empthArr, empthArr, empthArr

    if not hierMode and not nothing:
        print(f"File name : {path}")
        print(f"Total number of faces : {len(iarr)}")
        print(f"Number of faces with 3 vertices : {threeVertexCnt}")
        print(f"Number of faces with 4 vertices : {fourVertexCnt}")
        print(f"Number of faces with  more than 4 vertices : {moreVertexCnt}")

    varr, smooNarr = getSmoothNarr(v_varr, iarr, narr)
    return varr, v_varr, smooNarr, iarr, narr


################################################
#          SETTNGS FOR RENDERING

def setInitialBit():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)


def setPolygondMode():
    if (wireMode):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


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


def drawBackground():
    drawAxis()
    drawGrid()


def drawMesh():
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    if(smooMode):
        glNormalPointer(GL_FLOAT, 3 * smooNarr.itemsize, smooNarr)
        glVertexPointer(3, GL_FLOAT, 3 * v_varr.itemsize, v_varr)
        glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)
    else:
        glNormalPointer(GL_FLOAT, 3 * narr.itemsize, narr)
        glVertexPointer(3, GL_FLOAT, 3 * varr.itemsize, varr)
        glDrawArrays(GL_TRIANGLES, 0, int(varr.size / 3))


################################################
#              DRAW HIER MESHES

def setHierMeshes():
    global treeVarr, treeV_Varr, treeSmooNarr, treeIarr, treeNarr
    global duckVarr, duckV_Varr, duckSmooNarr, duckIarr, duckNarr
    global eagleVarr, eagleV_Varr, eagleSmooNarr, eagleIarr, eagleNarr
    global bearVarr, bearV_Varr, bearSmooNarr, bearIarr, bearNarr
    global flyVarr, flyV_Varr, flySmooNarr, flyIarr, flyNarr

    dirpath = os.path.dirname(__file__)

    path = os.path.join(dirpath, 'tree.obj')
    treeVarr, treeV_Varr, treeSmooNarr, treeIarr, treeNarr = getStuffsForDrawMesh(
        path)

    path = os.path.join(dirpath, 'duck.obj')
    duckVarr, duckV_Varr, duckSmooNarr, duckIarr, duckNarr = getStuffsForDrawMesh(
        path)

    path = os.path.join(dirpath, 'eagle.obj')
    eagleVarr, eagleV_Varr, eagleSmooNarr, eagleIarr, eagleNarr = getStuffsForDrawMesh(
        path)

    path = os.path.join(dirpath, 'bear.obj')
    bearVarr, bearV_Varr, bearSmooNarr, bearIarr, bearNarr = getStuffsForDrawMesh(
        path)

    path = os.path.join(dirpath, 'fly.obj')
    flyVarr, flyV_Varr, flySmooNarr, flyIarr, flyNarr = getStuffsForDrawMesh(
        path)


def drawHierMeshes():
    global varr, v_varr, smooNarr, iarr, narr

    t = glfw.get_time()

    glPushMatrix()                            # BEGIN OF ROOT

    glScalef(0.5, 0.5, 0.5)
    glTranslate(0, np.cos(t), 0)
    glRotatef(-t * 180/np.pi, 0, 1, 0)
    glPushMatrix()
    glScalef(0.2, 0.2, 0.2)
    varr, v_varr, smooNarr, iarr, narr = treeVarr, treeV_Varr, treeSmooNarr, treeIarr, treeNarr
    drawMesh()
    glPopMatrix()

    glPushMatrix()                            # BEGIN OF CHILD1
    glTranslatef(3, np.sin(t), 3)
    glPushMatrix()
    glScalef(0.01, 0.01, 0.01)
    glRotatef(-30, 0, 1, 0)
    glRotatef(-90, 1, 0, 0)
    varr, v_varr, smooNarr, iarr, narr = duckVarr, duckV_Varr, duckSmooNarr, duckIarr, duckNarr
    drawMesh()
    glPopMatrix()

    glPushMatrix()                            # BEGIN OF CHILD1-1
    glRotatef(-t * 180/np.pi, 0, 1, 0)
    glTranslatef(2, 6+2*np.sin(t), 2)
    glScalef(0.02, 0.02, 0.02)
    glRotatef(-210, 0, 1, 0)
    varr, v_varr, smooNarr, iarr, narr = eagleVarr, eagleV_Varr, eagleSmooNarr, eagleIarr, eagleNarr
    drawMesh()
    glPopMatrix()                             # END OF CHILD1-1

    glPushMatrix()                            # BEGIN OF CHILD1-2
    glRotatef(-t * 180/np.pi, 0, 1, 0)
    glTranslatef(-2, 6+2*np.sin(t), -2)
    glScalef(0.02, 0.02, 0.02)
    glRotatef(-30, 0, 1, 0)
    varr, v_varr, smooNarr, iarr, narr = eagleVarr, eagleV_Varr, eagleSmooNarr, eagleIarr, eagleNarr
    drawMesh()
    glPopMatrix()                             # END OF CHILD1-2
    glPopMatrix()                             # END OF CHILD1

    glPushMatrix()                            # BEGIN OF CHILD2
    glTranslatef(-3, -np.sin(t), -3)
    glPushMatrix()
    glScalef(0.8, 0.8, 0.8)
    glRotatef(120, 0, 1, 0)
    varr, v_varr, smooNarr, iarr, narr = bearVarr, bearV_Varr, bearSmooNarr, bearIarr, bearNarr
    drawMesh()
    glPopMatrix()

    glPushMatrix()                            # BEGIN OF CHILD2-1
    glRotatef(t * 360/np.pi, 0, 1, 0)
    glTranslatef(2, 3, 2)
    glScalef(0.03, 0.03, 0.03)
    glRotatef(-90, 1, 0, 0)
    varr, v_varr, smooNarr, iarr, narr = flyVarr, flyV_Varr, flySmooNarr, flyIarr, flyNarr
    drawMesh()
    glPopMatrix()                             # END OF CHILD2-1

    glPushMatrix()                            # BEGIN OF CHILD2-2
    glRotatef(t * 360/np.pi, 0, 1, 0)
    glTranslatef(-2, 3, -2)
    glScalef(0.03, 0.03, 0.03)
    glRotatef(-180, 0, 1, 0)
    glRotatef(-90, 1, 0, 0)
    varr, v_varr, smooNarr, iarr, narr = flyVarr, flyV_Varr, flySmooNarr, flyIarr, flyNarr
    drawMesh()
    glPopMatrix()                             # END OF CHILD2-2
    glPopMatrix()                             # END OF CHILD2

    glPopMatrix()                             # END OF ROOT


################################################
#                RENDERING


def render():
    setInitialBit()
    setPolygondMode()
    setProjectionMode()
    setViewMode()

    drawBackground()

    enableLight()
    setLight()
    if not nothing:
        if not hierMode and not nothing:
            glPushMatrix()
            drawMesh()
            glPopMatrix()
        elif hierMode:
            drawHierMeshes()
    disableLight()


################################################
#                 MAIN

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 800, "ClassAssignment2", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)
    setHierMeshes()

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
