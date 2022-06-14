# 2022_CSE4020_GRAPHICS
2022 Computer Graphics, (Prof. Yoonsang Lee)

## ClassAssignment1


 Class assignment1의 목표는 perspective projection / orthogonal projection 에서 mouse의 동작에 따라 카메라를 조작하는 것이다. 구현해야 할 목표는 총 3가지이다.

### 마우스에 동작에 따라 카메라를 움직이는 것


  - 이를 구현하기 위해서는 먼저 카메라에 보이는 물체가 있어야 한다. 나는 정육면체를 그렸고, 기준을 표현하기 위해서 x, y, z 축도 그렸다. 각각 drawCube(X) 함수와 drawAxis(X)에서 구현되었다. X는 물체의 크기를 설정하는 것이다.
  - render() 함수를 구현해야 했다. render() 함수 내부에서는 glMultMatrixf() 의 인자로 getMyLookat()의 반환 matrix를 넣어주었다.
  - getMyLookat() 함수 내부에서는 현재 ref (target)의 좌표와 elevation과 azimuth에 따라 eye의 좌표를 정한 후 eye의 w, u, v vector를 계산했고, 이를 토대로 Mv vector를 만들어서 return한다.
  - Azimuth와 elevation은 button_callback을 통해 왼쪽 클릭을 했을 때, cursor_callback 함수에 의해 정해진다. 기존 mouse의 좌표와 움직이는 mouse의 위치에 따라서 계속해서 azimuth와 elevation이 정해진다.
  - Panning을 위한 translation은 button_callback을 통해 오른쪽 클릭을 했을 때, cursor_callback 함수에 의해 정해진다. 이 역시 기존 mouse 좌표와 변화하는 mouse의 위치에 따라서 정해진다.
  - Zooming은 scroll_callback 함수에 의해 정해진다.
###	V 키를 눌렀을 때 projection 모드 변경
  - key_callback 함수를 통해 v키가 눌렸을 때, orthoMode라는 global 변수를 true or false로 toggle 되도록 만들었다.
  - 최초 프로그램 실행때는 orthoMode가 False이고, v키를 누르면 toggle 된다. 
  - orthoMode가 True일 때는 glOrtho() 함수가, False일 때는 gluPerspective() 함수가 실행된다.
### rectangular grid 그리기
  - drawGrid(X) 함수에서 grid를 그리도록 했다. 
  - Global 변수인 GRIDFACTOR에 따라서 얼마나 넓게 그릴지 정할 수 있다.

### Result

![image](https://user-images.githubusercontent.com/67817432/173562732-58668ce3-3d68-421b-bb8d-4345ef2a7823.png)


---

## ClassAssignment2

### https://youtu.be/YW8vy31HfnA

### 요구사항 구현
  1. Manipulate the camera: ClassAssignment1 와 동일하게 구현하였다. ‘v’ key를 누르면 projection mode가 toggle 되고, 마우스 조작을 통해 카메라를 회전시키거나 움직일 수 있다. 또한 마우스 휠을 사용해서 Zoom In/Out 을 구현하였다.
  2. Single mesh rendering mode: drop_callback을 사용해서 file을 drag하고 window위에 drop 하면 single mesh rendering mode로 전환되도록 하였다. 이때 filename에 ‘.obj’ 가 존재하지 않으면 열리지 않도록 만들었다. File이 정상적으로 들어왔다면, getStuffsForDrawMesh() 함수를 통해서 file을 parsing 한 뒤 vertex와 index 등의 정보를 가져온다. 또한 요구사항에 적힌 대로, file name과 face의 개수를 출력하도록 하였다. Sample file은 모두 정상적으로 동작한다.
  3. Animating hierarchical model rendering mode: ‘h’를 누르면 hierarchical model rendering mode로 바뀌게 된다. 총 4개의 obj 파일을 사용하였다. root node는 나무, root의 첫번째 자식은 오리, 두번째 자식은 곰이다. 오리의 자식은 독수리 두 마리이고, 곰의 자식은 나비 두 마리이다. Matrix stack을 활용한 3-level hierarchy 이며 leaf node를 재외하고 모두 두 개의 자식을 가진다. 나무를 중심으로 곰과 오리가 회전을 하고, 이때 나무는 위 아래로 움직인다. 또한 곰의 위에서는 나비 두 마리가 곰을 중심으로 회전하고, 독수리도 역시 오리를 중심으로 회전을 한다. 곰과 오리 모두 움직이고 있는 상태이고, 독수리와 나비는 항상 곰과 오리를 중심으로만 회전한다.
  4. Light source는 총 3개를 만들었고, LIGHT0, LIGHT1, LIGHT2 를 통해 번호를 설정하였다. 또한 GL_FILL과 GL_LINE를 활용하여 ‘z’를 눌렀을 때 wire frame mode와 solid mode가 toggle 되도록 만들었다.
  5. (Extra credit) smooth shading : ‘s’를 누르면 forsed smooth shading과 normal data shading이 토글된다.
  6. (Extra credit) triangulation : obj file에서 다각형이 존재하더라도 triangulation을 활용해 삼각형으로 나타내도록 하였다.
  
### Light configuration
  1. Light source의 개수는 총 3개이다.
  2. Light source의 위치는 각각 (3, 4, 5), (-2, 3, 1), (-2, -3, -5) 이고 색은 각각 red, green, blue 이다.
  3. Light source의 type은 모두 point light 이다.

### Result

   ![image](https://user-images.githubusercontent.com/67817432/173563338-52b1dca8-d611-4de8-968a-4d08fa9a4708.png)

---

## ClassAssignment3

### https://youtu.be/ADkXxml4L9I


### 요구사항 구현
  1. Manipulate the camera: ClassAssignment1 와 동일하게 구현하였다. ‘v’ key를 누르면 projection mode가 toggle 되고, 마우스 조작을 통해 카메라를 회전시키거나 움직일 수 있다. 또한 마우스 휠을 사용해서 Zoom In/Out 을 구현하였다.
  2. Load a bvh file: drop_callback을 사용해서 file을 drag하고 window위에 drop 하면 single mesh rendering mode로 전환되도록 하였다. 이때 filename에 ‘.bvh’ 가 존재하지 않으면 열리지 않도록 만들었다. File이 정상적으로 들어왔다면, Bvh class의 객체를 만들어 준 뒤 메소드를 통해 bvh file을 parsing 한다. Parsing 을 하면서 Node class 객체를 통해 각 Node를 만들어주고, parent와 children 멤버 변수를 통해 부모 자식을 이어준다. File parsing이 종료되면 bvh file의 정보를 출력한다. 이는 Bvh class의 __str__ 를 통해서 이루어졌다. 처음 rendering이 되면, 명세에 나와 있듯이 t-pose로 시작하게 된다. T-pose의 경우 translation 이나 rotation을 적용하지 않았다. End-effector joint를 위해서 End opcode를 읽을 시에 “End of ~” Node class 객체를 만들어 주었다.
  3. Render a bvh file: 1을 눌렀을 때는 Line rendering을 하고, 2를 눌렀을 때는 Box rendering을 한다. 이 Line/Box rendering mode의 변경은 프로그램 실행 중 어떤 시간이던지 적용할 수 있다.
  4. Animate the loaded motion if press the <spacebar>: spacebar를 눌렀을 때, motion의 처음부터 끝까지 계속해서 반복해서 보여준다.
  5. (extra credit) Use different obj files to draw each body part instead of a line segment: sample-walk.bvh 와 sample-spin.bvh 의 경우는 obj 모드로 변경 시 각 파트의 obj file들을 rendering 할 수 있게 된다. Obj file을 parsing 하고 rendering 하는 부분은 ClassAssignment2 의 것을 일부 가져왔다.

###	추가 구현 사항
  1. sample-walk.bvh 와 sample-spin.bvh가 rendering 되었을 때, 키보드 ‘o’를 누르면, obj file mode와 normal mode가 toggle 되도록 하였다.
  2. 다운로드 받은 파일과 sample file의 object 크기 차이가 심해서 파일의 이름에 “sample” 이 없는 경우 기존보다 작게 rendering 된다.

### Result
   ![image](https://user-images.githubusercontent.com/67817432/173563791-f3398baa-33b3-4231-bad9-660c27ffa4ef.png)

