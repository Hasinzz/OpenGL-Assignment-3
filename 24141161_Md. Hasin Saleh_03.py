from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Window settings
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
GRID_SIZE = 600
GRID_STEP = 100
aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
fovY = 120

# Camera
camera_pos = [0, 500, 500]
camera_mode = 0  # 0 = third-person, 1 = first-person
camera_angle = 0  # Initial angle for camera rotation

# Game state
gun_pos = [0, 0, 0]
gun_angle = 0
bullets = []
enemies = []
life = 5
score = 0
missed_bullets = 0
max_enemies = 5
bullet_speed = 15
game_over = False
cheat_mode = False
auto_follow = False

# Classes -

class Bullet:
    def __init__(self, x, y, z, angle):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

    def move(self):
        rad = math.radians(self.angle)
        self.x += bullet_speed * math.cos(rad)
        self.z += bullet_speed * math.sin(rad)

class Enemy:
    def __init__(self):
        self.reset()

    def reset(self):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.randint(300, 500)
        self.x = dist * math.cos(angle)
        self.z = dist * math.sin(angle)
        self.y = 0
        self.scale = 1
        self.scale_dir = 1

    def move_towards_player(self):
        # Only move if the game is not over
        if not game_over:
            dx = gun_pos[0] - self.x
            dz = gun_pos[2] - self.z
            dist = math.sqrt(dx ** 2 + dz ** 2)
            if dist > 1:
                # Slow down enemy movement by reducing the speed factor from 1.5 to 0.5
                self.x += dx / dist * 0.5  # Slower movement
                self.z += dz / dist * 0.5

    def update_scale(self):
        self.scale += self.scale_dir * 0.01
        if self.scale >= 1.3 or self.scale <= 0.7:
            self.scale_dir *= -1

# Camera Setup -
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, aspect_ratio, 1, 2000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Adjust camera position based on rotation around the origin
    if camera_mode == 0:  # Third-person view
        eye_x = camera_pos[0] + 150 * math.cos(math.radians(camera_angle))
        eye_z = camera_pos[2] + 150 * math.sin(math.radians(camera_angle))
        gluLookAt(eye_x, camera_pos[1], eye_z, 0, 0, 0, 0, 1, 0)
    else:  # First-person view
        eye_x = gun_pos[0] - 150 * math.cos(math.radians(gun_angle))
        eye_z = gun_pos[2] - 150 * math.sin(math.radians(gun_angle))
        gluLookAt(eye_x, gun_pos[1] + 100, eye_z,
                  gun_pos[0], gun_pos[1], gun_pos[2], 0, 1, 0)

#Drawing -

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_boundaries():
    boundary_height = 100  # Height of the vertical boundaries

    # Create four vertical boundaries
    # Front boundary
    glPushMatrix()
    glTranslatef(0, boundary_height / 2, GRID_SIZE)
    glColor3f(0, 0, 1)  # Blue color for the boundary
    glScalef(GRID_SIZE * 2, boundary_height, 10)  # Width, height, depth
    glutSolidCube(1)
    glPopMatrix()

    # Back boundary
    glPushMatrix()
    glTranslatef(0, boundary_height / 2, -GRID_SIZE)
    glColor3f(0, 0, 1)
    glScalef(GRID_SIZE * 2, boundary_height, 10)
    glutSolidCube(1)
    glPopMatrix()

    # Left boundary
    glPushMatrix()
    glTranslatef(-GRID_SIZE, boundary_height / 2, 0)
    glColor3f(0, 0, 1)
    glScalef(10, boundary_height, GRID_SIZE * 2)
    glutSolidCube(1)
    glPopMatrix()

    # Right boundary
    glPushMatrix()
    glTranslatef(GRID_SIZE, boundary_height / 2, 0)
    glColor3f(0, 0, 1)
    glScalef(10, boundary_height, GRID_SIZE * 2)
    glutSolidCube(1)
    glPopMatrix()

def draw_grid():
    for i in range(-GRID_SIZE, GRID_SIZE, GRID_STEP):
        for j in range(-GRID_SIZE, GRID_SIZE, GRID_STEP):
            if ((i + j) // GRID_STEP) % 2 == 0:
                glColor3f(0.9, 0.8, 1)
            else:
                glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glVertex3f(i, 0, j)
            glVertex3f(i + GRID_STEP, 0, j)
            glVertex3f(i + GRID_STEP, 0, j + GRID_STEP)
            glVertex3f(i, 0, j + GRID_STEP)
            glEnd()

    # Call the function to draw the boundaries after the grid is drawn
    draw_boundaries()

def draw_player():
    glPushMatrix()
    glTranslatef(*gun_pos)

    # Body
    glColor3f(0, 0, 1)
    glutSolidCube(40)

    # Head
    glTranslatef(0, 40, 0)
    glColor3f(1, 1, 0)
    glutSolidSphere(20, 10, 10)

    # Gun
    glTranslatef(0, 20, 0)
    glRotatef(gun_angle, 0, 1, 0)
    glColor3f(0, 1, 1)
    gluCylinder(gluNewQuadric(), 5, 5, 60, 10, 10)

    glPopMatrix()

def draw_bullets():
    glColor3f(1, 1, 1)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b.x, b.y + 20, b.z)
        glutSolidCube(10)
        glPopMatrix()

def draw_enemies():
    for e in enemies:
        glPushMatrix()
        glTranslatef(e.x, e.y, e.z)
        glScalef(e.scale, e.scale, e.scale)
        glColor3f(1, 0, 0)
        glutSolidSphere(25, 10, 10)
        glTranslatef(0, 40, 0)
        glColor3f(0, 0, 0)
        glutSolidSphere(10, 10, 10)
        glPopMatrix()

# Main Display -

def show_screen():
    global gun_angle, bullets, enemies, score, missed_bullets, life, game_over, cheat_mode

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setup_camera()

    draw_grid()
    draw_player()
    draw_bullets()
    draw_enemies()

    draw_text(10, 770, f"Player Life Remaining: {life}")
    draw_text(10, 745, f"Game Score: {score}")
    draw_text(10, 720, f"Player Bullet Missed: {missed_bullets}")

    # Update bullets
    new_bullets = []
    for b in bullets:
        b.move()
        if abs(b.x) < GRID_SIZE and abs(b.z) < GRID_SIZE:
            new_bullets.append(b)
        else:
            missed_bullets += 1
    bullets = new_bullets

    # Update enemies
    for e in enemies:
        e.move_towards_player()
        e.update_scale()
        dist = math.sqrt((gun_pos[0] - e.x) ** 2 + (gun_pos[2] - e.z) ** 2)
        if dist < 50:
            life -= 1
            e.reset()
            if life <= 0:
                game_over = True

    # Bullet-enemy collisions
    for b in bullets[:]:
        for e in enemies:
            dist = math.sqrt((b.x - e.x) ** 2 + (b.z - e.z) ** 2)
            if dist < 30:
                score += 1
                bullets.remove(b)
                e.reset()
                break

    # Continuous firing and automatic gun rotation (Cheat Mode)
    if cheat_mode:
        gun_angle += 1  # Continuously rotate the gun
        if random.random() < 0.05:  # Random chance to fire a bullet
            bullets.append(Bullet(gun_pos[0], gun_pos[1], gun_pos[2], gun_angle))

    glutSwapBuffers()

def idle():
    if not game_over:
        glutPostRedisplay()

# Input Handling -

def key_pressed(key, x, y):
    global gun_angle, gun_pos, bullets, game_over, life, score, missed_bullets, cheat_mode, auto_follow

    if key == b'w':
        gun_pos[0] += 10 * math.cos(math.radians(gun_angle))
        gun_pos[2] += 10 * math.sin(math.radians(gun_angle))
    elif key == b's':
        gun_pos[0] -= 10 * math.cos(math.radians(gun_angle))
        gun_pos[2] -= 10 * math.sin(math.radians(gun_angle))
    elif key == b'a':
        gun_angle = (gun_angle + 5) % 360
    elif key == b'd':
        gun_angle = (gun_angle - 5) % 360
    elif key == b'r':
        game_over = False
        life = 5
        score = 0
        missed_bullets = 0
        bullets.clear()
        for e in enemies:
            e.reset()
    elif key == b'c':  # Toggle cheat mode
        cheat_mode = not cheat_mode
    elif key == b'v':  # Toggle automatic gun following
        auto_follow = not auto_follow

def specialKeyListener(key, x, y):
    global camera_pos, camera_angle

    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_pos[1] += 10  # Increase the y-coordinate (move the camera up)

    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_pos[1] -= 10  # Decrease the y-coordinate (move the camera down)

    # Rotate camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_angle -= 5  # Rotate the camera to the left

    # Rotate camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_angle += 5  # Rotate the camera to the right

def mouse_listener(button, state, x, y):
    global camera_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        bullets.append(Bullet(gun_pos[0], gun_pos[1], gun_pos[2], gun_angle))
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = 1 - camera_mode

#Main Function -

def main():
    global enemies
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Bullet Frenzy")  
    glEnable(GL_DEPTH_TEST)

    enemies = [Enemy() for i in range(max_enemies)]

    glutDisplayFunc(show_screen)
    glutIdleFunc(idle)
    glutKeyboardFunc(key_pressed)
    glutSpecialFunc(specialKeyListener)  
    glutMouseFunc(mouse_listener)
    glutMainLoop()

if __name__ == '__main__':
    main()
