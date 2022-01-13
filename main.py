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

try:
    with open(os.path.join("data", "progress"), "r", encoding="utf8") as progress:
        if progress:
            current_map = int(progress.read())
            if current_map == -1:
                raise FileNotFoundError
    not_first = True

except FileNotFoundError:
    with open(os.path.join("data", "progress"), "w+", encoding="utf8") as progress:
        current_map = 1
        progress.write(str(current_map))


def go_to_main_menu():
    for j in groups:
        j.empty()
    global new_game
    global cont_button
    new_game = Button(100, 100, 400, 200, "yellow", 0, 20, "Новая игра", pygame.event.post, parameter=PLAYER_THERE)
    if not_first:
        cont_button = Button(100, 400, 400, 200, "green", 0, 20, "Продолжить", pygame.event.post,
                             parameter=STARTED)


def go_to_level_choice():
    for j in groups:
        j.empty()
    for n in range(current_map):
        levels.append(Button(100, n * 70 + 20, 100, 50, "yellow", 0, 5, f"{n + 1}", pygame.event.post,
                             parameter=PLAYER_THERE))


if __name__ == "__main__":
    go_to_main_menu()
    while running:
        canvas.fill("white")
        clock.tick(fps)
        pygame.display.set_caption(f"{clock.get_fps()}")
        objects.update()
        objects.draw(canvas)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    debug_hud = not debug_hud
                if event.key == pygame.K_ESCAPE:
                    there = False
                    go_to_main_menu()
            if event.type == pygame.USEREVENT:
                if new_game.is_pressed:
                    current_map = 1
                if cont_button.is_pressed:
                    go_to_level_choice()
            if event == PLAYER_THERE:
                for b in levels:
                    if b.is_pressed:
                        current_map = int(b.text)
                there = True
                player = open_map(f"map{current_map}.hcm")
            if event == NEXT_LEVEL:
                there = True
                current_map += 1
                with open(os.path.join("data", "progress"), "w+", encoding="utf8") as progress:
                    progress.write(str(current_map))
                player = open_map(f"map{current_map}.hcm")

        if there:
            if not player.alive:
                player = open_map(f"map{current_map}.hcm")
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
        pygame.display.flip()
pygame.quit()
