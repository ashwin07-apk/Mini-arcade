import pygame
import random


def run_game():

    pygame.init()

    # -------------------------
    # Screen settings
    # -------------------------

    WIDTH = 600
    HEIGHT = 400
    CELL_SIZE = 20

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")

    clock = pygame.time.Clock()

    # -------------------------
    # Colors
    # -------------------------

    BLACK = (0, 0, 0)
    GREEN = (0, 200, 0)
    DARK_GREEN = (0, 120, 0)
    RED = (200, 0, 0)
    WHITE = (255, 255, 255)

    # -------------------------
    # Fonts
    # -------------------------

    font = pygame.font.Font(None, 32)
    large_font = pygame.font.Font(None, 60)

    # -------------------------
    # Game variables
    # -------------------------

    snake = []
    direction = (CELL_SIZE, 0)
    food = (0, 0)

    score = 0
    speed = 10

    game_started = False
    game_over = False
    running = True

    # -------------------------
    # Reset game
    # -------------------------

    def reset_game():

        nonlocal snake
        nonlocal direction
        nonlocal food
        nonlocal score
        nonlocal speed
        nonlocal game_over

        snake = [
            (300, 200),
            (280, 200),
            (260, 200)
        ]

        direction = (CELL_SIZE, 0)

        food = (
            random.randrange(0, WIDTH, CELL_SIZE),
            random.randrange(0, HEIGHT, CELL_SIZE)
        )

        score = 0
        speed = 10
        game_over = False

    reset_game()

    # -------------------------
    # Main game loop
    # -------------------------

    while running:

        # -------------------------
        # Handle events
        # -------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # Start game with Enter
                if not game_started:

                    if event.key == pygame.K_RETURN:
                        game_started = True
                        reset_game()

                # Controls during game
                elif not game_over:

                    if (
                        event.key == pygame.K_UP
                        and direction != (0, CELL_SIZE)
                    ):
                        direction = (0, -CELL_SIZE)

                    elif (
                        event.key == pygame.K_DOWN
                        and direction != (0, -CELL_SIZE)
                    ):
                        direction = (0, CELL_SIZE)

                    elif (
                        event.key == pygame.K_LEFT
                        and direction != (CELL_SIZE, 0)
                    ):
                        direction = (-CELL_SIZE, 0)

                    elif (
                        event.key == pygame.K_RIGHT
                        and direction != (-CELL_SIZE, 0)
                    ):
                        direction = (CELL_SIZE, 0)

                # Restart after game over
                else:

                    if event.key == pygame.K_RETURN:
                        reset_game()
                        game_started = True

            # -------------------------
            # Start button
            # -------------------------

            if event.type == pygame.MOUSEBUTTONDOWN:

                mouse_x, mouse_y = pygame.mouse.get_pos()

                button_x = WIDTH // 2 - 100
                button_y = HEIGHT // 2
                button_width = 200
                button_height = 60

                if (
                    button_x <= mouse_x <= button_x + button_width
                    and button_y <= mouse_y <= button_y + button_height
                ):
                    reset_game()
                    game_started = True

        # -------------------------
        # Update game
        # -------------------------

        if game_started and not game_over:

            head_x, head_y = snake[0]

            new_head = (
                head_x + direction[0],
                head_y + direction[1]
            )

            snake.insert(0, new_head)

            # -------------------------
            # Food collision
            # -------------------------

            if new_head == food:

                score += 1

                food = (
                    random.randrange(0, WIDTH, CELL_SIZE),
                    random.randrange(0, HEIGHT, CELL_SIZE)
                )

                # Increase speed every 5 points
                if score % 5 == 0:
                    speed += 2

            else:
                snake.pop()

            # -------------------------
            # Wall collision
            # -------------------------

            if (
                new_head[0] < 0
                or new_head[0] >= WIDTH
                or new_head[1] < 0
                or new_head[1] >= HEIGHT
            ):
                game_over = True

            # -------------------------
            # Self collision
            # -------------------------

            if new_head in snake[1:]:
                game_over = True

        # -------------------------
        # Draw background
        # -------------------------

        screen.fill(BLACK)

        # -------------------------
        # Start screen
        # -------------------------

        if not game_started:

            title = large_font.render(
                "SNAKE",
                True,
                GREEN
            )

            screen.blit(
                title,
                (
                    WIDTH // 2 - title.get_width() // 2,
                    100
                )
            )

            button_rect = pygame.Rect(
                WIDTH // 2 - 100,
                HEIGHT // 2,
                200,
                60
            )

            pygame.draw.rect(
                screen,
                GREEN,
                button_rect
            )

            button_text = font.render(
                "START GAME",
                True,
                BLACK
            )

            screen.blit(
                button_text,
                (
                    button_rect.centerx - button_text.get_width() // 2,
                    button_rect.centery - button_text.get_height() // 2
                )
            )

            instruction = font.render(
                "or press ENTER",
                True,
                WHITE
            )

            screen.blit(
                instruction,
                (
                    WIDTH // 2 - instruction.get_width() // 2,
                    300
                )
            )

        else:

            # -------------------------
            # Draw snake
            # -------------------------

            for index, segment in enumerate(snake):

                if index == 0:
                    color = DARK_GREEN
                else:
                    color = GREEN

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        segment[0],
                        segment[1],
                        CELL_SIZE,
                        CELL_SIZE
                    )
                )

            # -------------------------
            # Draw food
            # -------------------------

            pygame.draw.rect(
                screen,
                RED,
                (
                    food[0],
                    food[1],
                    CELL_SIZE,
                    CELL_SIZE
                )
            )

            # -------------------------
            # Score
            # -------------------------

            score_text = font.render(
                f"Score: {score}",
                True,
                WHITE
            )

            screen.blit(score_text, (10, 10))

            # -------------------------
            # Speed
            # -------------------------

            speed_text = font.render(
                f"Speed: {speed}",
                True,
                WHITE
            )

            screen.blit(speed_text, (10, 40))

            # -------------------------
            # Game over
            # -------------------------

            if game_over:

                game_over_text = large_font.render(
                    "GAME OVER",
                    True,
                    RED
                )

                screen.blit(
                    game_over_text,
                    (
                        WIDTH // 2 - game_over_text.get_width() // 2,
                        130
                    )
                )

                restart_text = font.render(
                    "Press ENTER to restart",
                    True,
                    WHITE
                )

                screen.blit(
                    restart_text,
                    (
                        WIDTH // 2 - restart_text.get_width() // 2,
                        210
                    )
                )

        pygame.display.update()

        clock.tick(speed)

    pygame.quit()
