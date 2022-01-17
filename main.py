from engine import *
pygame.init()

running = True
clock = pygame.time.Clock()
fps = 60

debug_hud = False
player = None
there = False
current_map = -1
not_first = False
levels = list()
waiting = False
countdown = 0
ended = False
back_color = "white"

try:
    with open(os.path.join("data", "progress"), "r", encoding="utf8") as progress:
        if progress:
            current_map = int(progress.read())
            if current_map in [-1, 1]:
                raise FileNotFoundError
    not_first = True

except FileNotFoundError:
    with open(os.path.join("data", "progress"), "w+", encoding="utf8") as progress:
        current_map = 1
        progress.write(str(current_map))


def game_ending():
    global ended
    ended = True
    for j in groups:
        j.empty()
    ending_text = pygame.font.Font(None, 100)
    text = ending_text.render("Поздравляем!", False, "red", "white")
    canvas.blit(text, (50, 50))
    text = ending_text.render("Вы прошли все уровни", True, "red", "white")
    canvas.blit(text, (50, 200))


def go_to_main_menu():
    global back_color
    back_color = "white"
    ended = False
    for j in groups:
        j.empty()
    global new_game
    global cont_button
    new_game = Button(100, 100, 400, 200, "yellow", 0, 20, "Новая игра", pygame.event.post, parameter=PLAYER_THERE)
    if not_first:
        cont_button = Button(100, 400, 400, 200, "green", 0, 20, "Продолжить", pygame.event.post,
                             parameter=STARTED)


def go_to_level_choice():
    with open(os.path.join("data", "progress"), "r", encoding="utf8") as progress:
        opened = int(progress.read())
    for j in groups:
        j.empty()
    for n in range(opened):
        levels.append(Button(500, n * 120 + 20, 200, 100, "yellow", 0, 5, f"Уровень {n + 1}", pygame.event.post,
                             parameter=PLAYER_THERE))


if __name__ == "__main__":
    go_to_main_menu()
    while running:
        canvas.fill(back_color)
        clock.tick(fps)
        pygame.display.set_caption(f"Homecoming main FPS={clock.get_fps()}")
        objects.update()
        objects.draw(canvas)
        if not waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    if cont_button.is_pressed:
                        go_to_level_choice()
                if event == PLAYER_THERE:
                    back_color = choice([(255, 200, 200), (220, 255, 220), "white", (100, 220, 255)])
                    for b in levels:
                        if b.is_pressed:
                            current_map = int(b.text.split()[-1])
                    there = True
                    if new_game.is_pressed:
                        current_map = 1
                    player = open_map(f"map{current_map}.csv")
                if event == NEXT_LEVEL:
                    back_color = choice([(255, 200, 200), (220, 255, 220), "white", (100, 220, 255)])
                    there = True
                    not_first = True
                    current_map += 1
                    with open(os.path.join("data", "progress"), "r", encoding="utf8") as progress:
                        opened = int(progress.read())
                    if opened < current_map:
                        with open(os.path.join("data", "progress"), "w+", encoding="utf8") as progress:
                            progress.write(str(current_map))
                    player = open_map(f"map{current_map}.csv")
                if event == END_OF_GAME:
                    player = None
                    there = False
                    game_ending()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F5:
                        debug_hud = not debug_hud
                    if event.key == pygame.K_ESCAPE:
                        there = False
                        go_to_main_menu()
            if ended:
                game_ending()
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    go_to_main_menu()
                    ended = False

            if there:
                if not player.alive:
                    waiting = True
                    countdown = 0
                if player.rect.x >= 600:
                    for i in everything:
                        i.rect.x -= 5

                elif player.rect.x <= 400:
                    for i in everything:
                        i.rect.x += 5

                if player.rect.y <= 200:
                    for i in everything:
                        i.rect.y += 5

                elif player.rect.y >= 400:
                    for i in everything:
                        i.rect.y -= 5
                if debug_hud:
                    player.debug()
                player.draw_hud()
        else:
            countdown += 1
            player.remove(*groups)
            if countdown > 120:
                waiting = False
                player = open_map(f"map{current_map}.csv")
        pygame.display.flip()
pygame.quit()
