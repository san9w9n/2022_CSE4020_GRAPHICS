import glfw
import numpy as np
from OpenGL.GL import *

init = np.array([[1., 0., 0.],
	   			 [0., 1., 0.],
	   			 [0., 0., 1.]])
tenDegree = np.radians(10)
now = init


dic = {
	glfw.KEY_W: np.array([[0.9, 0., 0.],
	   					  [0. , 1., 0.],
	   					  [0. , 0., 1.]]),
	glfw.KEY_E: np.array([[1.1, 0., 0.],
	   					  [0. , 1., 0.],
	   					  [0. , 0., 1.]]),
	glfw.KEY_S: np.array([[np.cos(tenDegree), -np.sin(tenDegree), 0.], 
                      	  [np.sin(tenDegree),  np.cos(tenDegree), 0.], 
                      	  [0.,		   		   0.,		   		  1.]]),
	glfw.KEY_D: np.array([[np.cos(-tenDegree), -np.sin(-tenDegree), 0.], 
                      	  [np.sin(-tenDegree),  np.cos(-tenDegree), 0.], 
                      	  [0.,		   		   0.,		   		  1.]]),
	glfw.KEY_X: np.array([[1., -0.1, 0.],
	   					  [0., 1., 0.],
	   					  [0., 0., 1.]]),
	glfw.KEY_C: np.array([[1., 0.1, 0.],
	   					  [0., 1. , 0.],
	   					  [0., 0. , 1.]]),
	glfw.KEY_R: np.array([[1., 0. , 0.],
	   					  [0., -1., 0.],
	   					  [0., 0. , 1.]]),
}

def render(T):
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

    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv( (T @ np.array([.0, .5, 1.]))[:-1])
    glVertex2fv( (T @ np.array([.0, .0, 1.]))[:-1])
    glVertex2fv( (T @ np.array([.5, .0, 1.]))[:-1])
    glEnd()

def key_callback(window, key, scancode, action, mods):
	global now
	if action != glfw.PRESS: return
	if key == glfw.KEY_1:
		now = init
		return
	try: now = dic[key] @ now
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
		render(now)
		glfw.swap_buffers(window)
	glfw.terminate()

if __name__ == "__main__":
	main()
