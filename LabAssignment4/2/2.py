import glfw
import numpy as np
from OpenGL.GL import *

T = np.array([[1., 0., 0.5],
              [0., 1., 0],
              [0., 0., 1.]])

def render(M):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    glBegin(GL_LINES)

    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))

    glEnd()

    glColor3ub(255, 255, 255)

    glBegin(GL_POINTS)
    glVertex2fv(((M @ T) @ np.array([0.5, 0., 1.]))[:-1])
    glEnd()
    
    glBegin(GL_LINES)
    glVertex2fv((M @ np.array([0.5, 0., 0.]))[:-1])
    glVertex2fv(np.array([0., 0.]))
    glEnd()

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480,480,"2018008877", None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        th = glfw.get_time()
        M = np.array([[np.cos(th), -np.sin(th), 0],
                   [np.sin(th), np.cos(th), 0],
                   [0., 0., 1.]])
        render(M)
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
	main()
