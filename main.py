import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
from math import sin, cos, radians

# Function to generate a 3D cube
def draw_cube():
    vertices = [
        (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1),  # Back vertices
        (1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1)       # Front vertices
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),     # Back
        (4, 5), (5, 6), (6, 7), (7, 4),     # Front
        (0, 4), (1, 5), (2, 6), (3, 7)      # Sides
    ]
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Function to draw the crosshair (reticle)
def draw_crosshair(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)  # Move to the position of the crosshair
    glBegin(GL_LINES)
    glColor3f(1, 1, 1)  # White color for crosshair
    glVertex3f(-0.05, 0, 0)
    glVertex3f(0.05, 0, 0)
    glVertex3f(0, -0.05, 0)
    glVertex3f(0, 0.05, 0)
    glEnd()
    glPopMatrix()

# Function to create new 3D obstacles
def generate_obstacle():
    x = random.uniform(-10, 10)
    y = random.uniform(-5, 5)
    z = random.uniform(-30, -100)
    return [x, y, z]

# Function to create a bullet with initial direction
def create_bullet(angle_y, angle_x):
    speed = 0.5
    bullet_direction = [
        cos(radians(angle_y)) * cos(radians(angle_x)),
        sin(radians(angle_x)),
        sin(radians(angle_y)) * cos(radians(angle_x))
    ]
    return bullet_direction

# Main function
def main():
    pygame.init()
    display = (1920, 1080)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 150.0)

    # Player's position
    player_x, player_y = 0, 0
    player_z = -5  # Fixed Z position for the camera

    # List of obstacles
    num_obstacles = 20
    obstacles = [generate_obstacle() for _ in range(num_obstacles)]
    bullets = []  # List to store bullets
    score = 0  # Player score

    # Mouse controls for camera rotation
    pygame.mouse.set_visible(False)  # Hide the mouse cursor
    pygame.event.set_grab(True)  # Grab mouse input
    mouse_x, mouse_y = pygame.mouse.get_pos()
    sensitivity = 0.1

    angle_y, angle_x = 0, 0  # Angles for bullet direction

    # Game loop
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:  # Shoot bullet
                    bullets.append([0, 0, 0] + create_bullet(angle_y, angle_x))

        # Mouse movement for camera rotation
        new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
        delta_x = (new_mouse_x - mouse_x) * sensitivity
        delta_y = (new_mouse_y - mouse_y) * sensitivity

        # Update angles based on mouse movement
        angle_y += delta_x
        angle_x -= delta_y

        # Clamp the angle_x to allow full vertical aiming
        angle_x = max(-90, min(90, angle_x))  # Allow full vertical movement

        # Update mouse position for next frame
        mouse_x, mouse_y = new_mouse_x, new_mouse_y

        # Handle movement of obstacles
        keys = pygame.key.get_pressed()
        if keys[K_w]:  # Move obstacles toward the player
            for obstacle in obstacles:
                obstacle[2] += 0.1  # Move obstacles towards the player

        if keys[K_s]:  # Move obstacles away from the player
            for obstacle in obstacles:
                obstacle[2] -= 0.1  # Move obstacles away from the player

        if keys[K_a]:  # Turn left
            angle_y -= 1  # Rotate camera left

        if keys[K_d]:  # Turn right
            angle_y += 1  # Rotate camera right

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw player's weapon (as a small green cube) at the center of the screen
        glPushMatrix()
        glTranslatef(0, 0, -1)  # Fixed position for the weapon
        glColor3f(0, 1, 0)  # Green color for weapon
        draw_cube()
        glPopMatrix()

        # Draw obstacles
        for obstacle in obstacles:
            glPushMatrix()
            glTranslatef(obstacle[0], obstacle[1], obstacle[2])
            glColor3f(1, 0, 0)  # Red color for obstacles
            draw_cube()
            glPopMatrix()

            # Check collision with player
            if (abs(player_x - obstacle[0]) < 1 and
                abs(player_y - obstacle[1]) < 1 and
                -6 < obstacle[2] < -4):
                print("Game Over! Score:", score)
                pygame.quit()
                return

        # Update and draw bullets
        for bullet in bullets:
            bullet[0] += bullet[3] * 0.1  # Update x position
            bullet[1] += bullet[4] * 0.1  # Update y position
            bullet[2] += bullet[5] * 0.1  # Update z position

            # Draw bullet
            glPushMatrix()
            glTranslatef(bullet[0], bullet[1], bullet[2])
            glColor3f(1, 1, 0)  # Yellow color for bullets
            draw_cube()
            glPopMatrix()

            # Check collision with obstacles
            for obstacle in obstacles:
                if (abs(bullet[0] - obstacle[0]) < 1 and
                    abs(bullet[1] - obstacle[1]) < 1 and
                    abs(bullet[2] - obstacle[2]) < 1):
                    obstacles.remove(obstacle)
                    bullets.remove(bullet)
                    score += 1
                    break

            # Remove bullets that go out of bounds
            if bullet[2] > 0 or bullet[2] < -150:
                bullets.remove(bullet)

        # Calculate crosshair position based on angles
        crosshair_x = cos(radians(angle_y)) * cos(radians(angle_x)) * 5  # Distance from player
        crosshair_y = sin(radians(angle_x)) * 5
        crosshair_z = sin(radians(angle_y)) * cos(radians(angle_x)) * 5

        # Draw crosshair
        draw_crosshair(crosshair_x, crosshair_y, crosshair_z)

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
