import pygame
import random

# Constants
CELL = 48
COLS = 12
ROWS = 8
W = COLS * CELL
H = ROWS * CELL + 60
FPS = 10

# Colors
BG       = (15, 15, 35)
WALL     = (40, 40, 80)
OPEN     = (25, 25, 55)
C_START  = (20, 80, 180)
C_END    = (180, 30, 50)
C_AGENT  = (245, 165, 30)
C_TRAIL  = (80, 60, 20)
C_BEST   = (40, 160, 90)
C_TEXT   = (200, 200, 220)

# Maze: 0=open  1=wall
MAZE = [
    [0,0,1,0,0,0,1,0,0,0,0,0],
    [1,0,1,0,1,0,1,0,1,1,0,1],
    [0,0,0,0,1,0,0,0,0,1,0,0],
    [0,1,1,0,1,1,0,1,0,1,1,0],
    [0,0,1,0,0,0,0,1,0,0,0,0],
    [1,0,1,1,1,0,1,0,1,1,0,1],
    [0,0,0,0,1,0,0,0,0,1,0,0],
    [0,1,1,0,0,0,1,0,1,0,0,0],
]

START = (0, 0)
END   = (7, 11)

# Q-Learning: learns which direction is best from each cell
class QLearning:
    def __init__(self):
        self.q = {}          # table: (row, col, direction) -> score
        self.alpha = 0.7     # learning rate
        self.gamma = 0.9     # importance of future rewards
        self.epsilon = 1.0   # exploration rate (1=random, 0=learned)

    def get(self, r, c, d):
        return self.q.get((r, c, d), 0.0)

    def update(self, r, c, d, reward, nr, nc):
        # update score based on reward + best possible future score
        best_next = max(self.get(nr, nc, i) for i in range(4))
        old = self.get(r, c, d)
        self.q[(r, c, d)] = old + self.alpha * (reward + self.gamma * best_next - old)

    def choose(self, r, c, valid_dirs):
        # explore randomly OR follow what was learned
        if random.random() < self.epsilon:
            return random.choice(valid_dirs)
        return max(valid_dirs, key=lambda d: self.get(r, c, d))


# Agent: the character moving through the maze
class Agent:
    def __init__(self):
        self.best_path = None
        self.best_steps = float('inf')
        self.try_num = 1
        self.reset()

    def reset(self):
        self.r, self.c = START
        self.path = [(self.r, self.c)]
        self.steps = 0
        self.done = False

    def get_valid_dirs(self):
        # returns directions the agent can move (no wall, no out of bounds)
        dirs = []
        moves = [(-1,0),(1,0),(0,-1),(0,1)]
        for i, (dr, dc) in enumerate(moves):
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and MAZE[nr][nc] != 1:
                dirs.append(i)
        return dirs


MOVES = [(-1,0),(1,0),(0,-1),(0,1)]

def draw(screen, agent, font, speed):
    screen.fill(BG)

    # Draw maze cells
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * CELL, r * CELL
            if MAZE[r][c] == 1:
                pygame.draw.rect(screen, WALL, (x+2, y+2, CELL-4, CELL-4), border_radius=4)
            else:
                pygame.draw.rect(screen, OPEN, (x+2, y+2, CELL-4, CELL-4), border_radius=4)

    # Draw best path in green
    if agent.best_path:
        for (r, c) in agent.best_path:
            x, y = c * CELL + CELL//4, r * CELL + CELL//4
            pygame.draw.rect(screen, C_BEST, (x, y, CELL//2, CELL//2), border_radius=3)

    # Draw current trail in orange
    for (r, c) in agent.path:
        x, y = c * CELL + CELL//3, r * CELL + CELL//3
        pygame.draw.rect(screen, C_TRAIL, (x, y, CELL//3, CELL//3), border_radius=2)

    # Draw start cell
    sx, sy = START[1]*CELL, START[0]*CELL
    pygame.draw.rect(screen, C_START, (sx+2, sy+2, CELL-4, CELL-4), border_radius=4)
    screen.blit(font.render("S", True, (255,255,255)), (sx+14, sy+12))

    # Draw end cell
    ex, ey = END[1]*CELL, END[0]*CELL
    pygame.draw.rect(screen, C_END, (ex+2, ey+2, CELL-4, CELL-4), border_radius=4)
    screen.blit(font.render("E", True, (255,255,255)), (ex+14, ey+12))

    # Draw agent
    ax, ay = agent.c * CELL + CELL//2, agent.r * CELL + CELL//2
    pygame.draw.circle(screen, C_AGENT, (ax, ay), CELL//3)

    # Draw HUD text at the bottom
    best = agent.best_steps if agent.best_steps < float('inf') else '—'
    txt = f"Try #{agent.try_num}   Steps: {agent.steps}   Best: {best}   Speed: x{speed}   [UP/DOWN] speed   [R] reset"
    screen.blit(font.render(txt, True, C_TEXT), (10, ROWS * CELL + 15))

    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("PathFinder AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16)

    agent = Agent()
    ql = QLearning()
    running = True
    speed = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    speed = min(speed + 1, 20)
                if event.key == pygame.K_DOWN:
                    speed = max(speed - 1, 1)
                if event.key == pygame.K_r:
                    agent = Agent()
                    ql = QLearning()

        if not agent.done:
            valid = agent.get_valid_dirs()
            if not valid or agent.steps >= 150:
                # Failed — reset and reduce exploration
                ql.epsilon = max(0.05, ql.epsilon * 0.995)
                agent.try_num += 1
                agent.reset()
            else:
                d = ql.choose(agent.r, agent.c, valid)
                dr, dc = MOVES[d]
                nr, nc = agent.r + dr, agent.c + dc

                # Reward: positive if closer to end, negative if farther
                dist_before = abs(agent.r - END[0]) + abs(agent.c - END[1])
                dist_after  = abs(nr - END[0]) + abs(nc - END[1])
                reward = 1 if dist_after < dist_before else -0.5

                if (nr, nc) == END:
                    reward = 100
                    agent.done = True
                    if agent.steps + 1 < agent.best_steps:
                        agent.best_steps = agent.steps + 1
                        agent.best_path = agent.path + [(nr, nc)]

                ql.update(agent.r, agent.c, d, reward, nr, nc)
                agent.r, agent.c = nr, nc
                agent.path.append((nr, nc))
                agent.steps += 1

        else:
            # Success — short pause then restart
            pygame.time.wait(400)
            ql.epsilon = max(0.05, ql.epsilon * 0.99)
            agent.try_num += 1
            agent.reset()

        draw(screen, agent, font, speed)
        clock.tick(FPS * speed)

    pygame.quit()


main()