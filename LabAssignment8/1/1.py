import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo
import ctypes

gCamAng = 0.
gCamHeight = 1.

objRed, objGreen, objBlue = 1., 1., 1.
lightRed, lightGreen, lightBlue = 1., 1., 1.

def createVertexArraySeparate():
  varr = np.array([
    (0, 0, 1),         # v0 normal
    (-1,  1,  1),  # v0 position
    (0, 0, 1),         # v2 normal
    (1, -1,  1),  # v2 position
    (0, 0, 1),         # v1 normal
    (1,  1,  1),  # v1 position

    (0, 0, 1),         # v0 normal
    (-1,  1,  1),  # v0 position
    (0, 0, 1),         # v3 normal
    (-1, -1,  1),  # v3 position
    (0, 0, 1),         # v2 normal
    (1, -1,  1),  # v2 position

    (0, 0, -1),
    (-1,  1, -1),  # v4
    (0, 0, -1),
    (1,  1, -1),  # v5
    (0, 0, -1),
    (1, -1, -1),  # v6

    (0, 0, -1),
    (-1,  1, -1),  # v4
    (0, 0, -1),
    (1, -1, -1),  # v6
    (0, 0, -1),
    (-1, -1, -1),  # v7

    (0, 1, 0),
    (-1,  1,  1),  # v0
    (0, 1, 0),
    (1,  1,  1),  # v1
    (0, 1, 0),
    (1,  1, -1),  # v5

    (0, 1, 0),
    (-1,  1,  1),  # v0
    (0, 1, 0),
    (1,  1, -1),  # v5
    (0, 1, 0),
    (-1,  1, -1),  # v4

    (0, -1, 0),
    (-1, -1,  1),  # v3
    (0, -1, 0),
    (1, -1, -1),  # v6
    (0, -1, 0),
    (1, -1,  1),  # v2

    (0, -1, 0),
    (-1, -1,  1),  # v3
    (0, -1, 0),
    (-1, -1, -1),  # v7
    (0, -1, 0),
    (1, -1, -1),  # v6

    (1, 0, 0),
    (1,  1,  1),  # v1
    (1, 0, 0),
    (1, -1,  1),  # v2
    (1, 0, 0),
    (1, -1, -1),  # v6

    (1, 0, 0),
    (1,  1,  1),  # v1
    (1, 0, 0),
    (1, -1, -1),  # v6
    (1, 0, 0),
    (1,  1, -1),  # v5

    (-1, 0, 0),
    (-1,  1,  1),  # v0
    (-1, 0, 0),
    (-1, -1, -1),  # v7
    (-1, 0, 0),
    (-1, -1,  1),  # v3

    (-1, 0, 0),
    (-1,  1,  1),  # v0
    (-1, 0, 0),
    (-1,  1, -1),  # v4
    (-1, 0, 0),
    (-1, -1, -1),  # v7
  ], 'float32')
  return varr


def drawCube_glDrawArray():
  global gVertexArraySeparate
  varr = gVertexArraySeparate
  glEnableClientState(GL_VERTEX_ARRAY)
  glEnableClientState(GL_NORMAL_ARRAY)
  glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
  glVertexPointer(3, GL_FLOAT, 6*varr.itemsize,
                  ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
  glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))


def render():
  global gCamAng, gCamHeight
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glEnable(GL_DEPTH_TEST)

  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  gluPerspective(45, 1, 1, 10)

  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  gluLookAt(5*np.sin(gCamAng), gCamHeight, 5 *
            np.cos(gCamAng), 0, 0, 0, 0, 1, 0)

  glEnable(GL_LIGHTING)
  glEnable(GL_LIGHT0)
  glEnable(GL_NORMALIZE)

  glPushMatrix()
  lightPos = (3., 4., 5., 1.)
  glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
  glPopMatrix()

  lightColor = (lightRed, lightGreen, lightBlue, 1.)
  ambientLightColor = (.1, .1, .1, 1.)
  glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
  glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
  glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

  objectColor = (objRed, objGreen, objBlue, 1.)
  specularObjectColor = (1., 1., 1., 1.)
  glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
  glMaterialfv(GL_FRONT, GL_SHININESS, 10)
  glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

  glPushMatrix()
  glColor3ub(0, 0, 255) 

  drawCube_glDrawArray()
  glPopMatrix()

  glDisable(GL_LIGHTING)

def key_callback(window, key, scancode, action, mods):
  global gCamAng, gCamHeight, objRed, objGreen, objBlue, lightRed, lightGreen, lightBlue
  if action == glfw.PRESS or action == glfw.REPEAT:
    if key == glfw.KEY_1:
      gCamAng += np.radians(-10)
    elif key == glfw.KEY_3:
      gCamAng += np.radians(10)
    elif key == glfw.KEY_2:
      gCamHeight += .1
    elif key == glfw.KEY_W:
      gCamHeight += -.1
    elif key == glfw.KEY_A:
      lightRed, lightGreen, lightBlue = 1., 0., 0.
    elif key == glfw.KEY_S:
      lightRed, lightGreen, lightBlue = 0., 1., 0.
    elif key == glfw.KEY_D:
      lightRed, lightGreen, lightBlue = 0., 0., 1.
    elif key == glfw.KEY_F:
      lightRed, lightGreen, lightBlue = 1., 1., 1.
    elif key == glfw.KEY_Z:
      objRed, objGreen, objBlue = 1., 0., 0.
    elif key == glfw.KEY_X:
      objRed, objGreen, objBlue = 0., 1., 0.
    elif key == glfw.KEY_C:
      objRed, objGreen, objBlue = 0., 0., 1.
    elif key == glfw.KEY_V:
      objRed, objGreen, objBlue = 1., 1., 1.

gVertexArraySeparate = None

def main():
  global gVertexArraySeparate

  if not glfw.init():
    return
  window = glfw.create_window(480, 480, '2018008877', None, None)
  if not window:
    glfw.terminate()
    return
  glfw.make_context_current(window)
  glfw.set_key_callback(window, key_callback)
  glfw.swap_interval(1)

  gVertexArraySeparate = createVertexArraySeparate()

  while not glfw.window_should_close(window):
    glfw.poll_events()
    render()
    glfw.swap_buffers(window)

  glfw.terminate()

if __name__ == "__main__":
  main()
