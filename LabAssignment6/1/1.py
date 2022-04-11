import glfw
from OpenGL.GL import *
import numpy as np


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLoadIdentity()

    myOrtho(-5, 5, -5, 5, -8, 8)
    myLookAt(np.array([5, 3, 5]), np.array([1, 1, -1]), np.array([0, 1, 0]))

    drawFrame()
    glColor3ub(255, 255, 255)
    drawCubeArray()

def myLookAt(eye, at, up):
    eye = eye.astype('float32')
    at = at.astype('float32')
    up = up.astype('float32')
    
    w = (eye-at) / np.sqrt(np.dot(eye-at,eye-at))
    u = np.cross(up,w) / np.sqrt(np.dot(np.cross(up,w),np.cross(up,w)))
    v = np.cross(w,u)

    M = np.array([[u[0], u[1], u[2], -np.dot(u, eye)],
                 [v[0], v[1], v[2], -np.dot(v, eye)],
                 [w[0], w[1], w[2], -np.dot(w, eye)],
                 [0., 0., 0., 1.]])
    glMultMatrixf(M.T)

def myOrtho(left, right, bottom, top, near, far):
    l = float(left)
    r = float(right)
    b = float(bottom)
    t = float(top)
    n = float(near)
    f = float(far)

    R = np.array([[2/(r-l), 0., 0., -(r+l)/(r-l)],
                   [0., 2/(t-b), 0., -(t+b)/(t-b)],
                   [0., 0., -2/(f-n), -(f+n)/(f-n)],
                   [0., 0., 0., 1.]])

    glMultMatrixf(R.T)

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

def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)

    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)

    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)

    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)

    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glEnd()

def drawCubeArray():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                glPushMatrix()
                glTranslatef(i,j,-k-1)
                glScalef(.5,.5,.5)
                drawUnitCube()
                glPopMatrix()

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2018008877", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
