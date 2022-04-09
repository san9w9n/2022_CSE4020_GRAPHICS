import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# GLOBAL VARIABLE

OBJSIZE = .5
GRIDFACTOR = 10.

orthoMode = False
lClick, rClick = False, False

dist = 5.
azimuth = 45.
elevation = 36.

X, Y = 0, 0
mouseX, mouseY = 0, 0

ref = np.array([0., 0., 0.])
u = np.array([1, 0, 0])
v = np.array([0, 1, 0])
w = np.array([0, 0, 1])
up = np.array([0., 1., 0.])

# return cos(), sin()
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
    if denominator == 0 : return np.array([0, 0, 0])
    return num / denominator

def getMyLookAt():
    global u, v, w
    eye = np.array([ref[0] + dist * cosElev() * sinAzim(), 
                    ref[1] + dist* sinElev(), 
                    ref[2] + dist * cosElev() * cosAzim()])

    w = getUnit(eye - ref)
    u = getUnit(np.cross(up, w))
    v = getUnit(np.cross(w, u))

    Mv = np.array([[           u[0],            v[0],            w[0], 0],
                   [           u[1],            v[1],            w[1], 0],
                   [           u[2],            v[2],            w[2], 0],
                   [-np.dot(u, eye), -np.dot(v, eye), -np.dot(w, eye), 1]])
    return Mv

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    
    glLoadIdentity()

    if orthoMode:
        glOrtho(-10, 10, -10, 10, -20, 20)
    else:
        gluPerspective(45, 1, 3,20)

    glMultMatrixf(getMyLookAt())

    drawAxis(OBJSIZE)
    drawGrid(OBJSIZE)
    drawCube(OBJSIZE)

def drawAxis(X):
    glBegin(GL_LINES)

    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-X*GRIDFACTOR, 0., 0.]))
    glVertex3fv(np.array([ X*GRIDFACTOR, 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,           0., 0.]))
    glVertex3fv(np.array([0., X*GRIDFACTOR, 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., -X*GRIDFACTOR]))
    glVertex3fv(np.array([0., 0.,  X*GRIDFACTOR]))

    glEnd()
    
def drawGrid(X):
    glBegin(GL_LINES)
    glColor3ub(255, 255, 255)
    e = -X*GRIDFACTOR
    arr = []
    while (e <= X*GRIDFACTOR) :
        arr.append(e)
        e += X
    for p in arr:
        glVertex3fv(np.array([p, 0., X*GRIDFACTOR]))
        glVertex3fv(np.array([p, 0., -X*GRIDFACTOR]))
        glVertex3fv(np.array([X*GRIDFACTOR, 0., p]))
        glVertex3fv(np.array([-X*GRIDFACTOR, 0., p]))
    glEnd()

def drawCube(X):
    glBegin(GL_QUADS)
    glColor3f(.5,1.,1.)
    glVertex3f(X,X,-X)
    glVertex3f(-X,X,-X)
    glVertex3f(-X, X, X)
    glVertex3f( X, X, X) 

    glVertex3f( X,-X, X)
    glVertex3f(-X,-X, X)
    glVertex3f(-X,-X,-X)
    glVertex3f( X,-X,-X) 

    glVertex3f( X, X, X)
    glVertex3f(-X, X, X)
    glVertex3f(-X,-X, X)
    glVertex3f( X,-X, X)

    glVertex3f( X,-X,-X)
    glVertex3f(-X,-X,-X)
    glVertex3f(-X, X,-X)
    glVertex3f( X, X,-X)

    glVertex3f(-X, X, X) 
    glVertex3f(-X, X,-X)
    glVertex3f(-X,-X,-X) 
    glVertex3f(-X,-X, X) 

    glVertex3f( X, X,-X) 
    glVertex3f( X, X, X)
    glVertex3f( X,-X, X)
    glVertex3f( X,-X,-X)
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global orthoMode
    if key == glfw.KEY_V and action == glfw.PRESS:
        orthoMode = not orthoMode

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
    else: rClick = lClick = False

def cursor_callback(window, x, y):
    global ref, u, v, mouseX, mouseY, elevation, azimuth, up
    subX = mouseX - x
    subY = y - mouseY
    if (lClick):
        azimuth += subX*0.1
        elevation += subY*0.1
        if cosElev() < 0: up[1] = -1
        else: up[1] = 1
    elif (rClick):
        ref += (u * .01 * subX) + (v * .01 * subY)
    mouseX, mouseY = x, y

def scroll_callback(window, _, y):
    global dist
    if y: 
        if dist-y <= 0: dist = 0
        else: dist -= y

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800,800,"ClassAssignment1", None,None)
    if not window:
        glfw.terminate()
        return
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.make_context_current(window)

    glfw.swap_interval(1)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
	main()