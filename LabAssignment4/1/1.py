import glfw
import numpy as np
from OpenGL.GL import *

sequence = []

def Q():
    glTranslatef(-0.1, 0., 0.)
def E():
    glTranslatef(0.1, 0., 0.)
def A():
    glRotatef(10, 0, 0, 1)
def D():
    glRotatef(-10, 0, 0, 1)

dic = {
	glfw.KEY_Q: Q,
    glfw.KEY_E: E,
    glfw.KEY_A: A,
    glfw.KEY_D: D,
}

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()

    glColor3ub(255, 255, 255)
    
    for func in reversed(sequence):
        func()
        
    drawTriangle()

def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([.0, .5]))
    glVertex2fv(np.array([.0, .0]))
    glVertex2fv(np.array([.5, .0]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global sequence
    if action == glfw.PRESS or action == glfw.REPEAT : 
        if key == glfw.KEY_1:
            sequence.clear()
            return
        try:
            element = dic[key]
            sequence.append(element)
        except: pass

def main():
	if not glfw.init():
		return
	window = glfw.create_window(480,480,"2018008877", None,None)
	if not window:
		glfw.terminate()
		return
	glfw.set_key_callback(window, key_callback)
	glfw.make_context_current(window)
	while not glfw.window_should_close(window):
		glfw.poll_events()
		render()
		glfw.swap_buffers(window)
	glfw.terminate()

if __name__ == "__main__":
	main()
