from engine import *
pygame.init()

running = True
clock = pygame.time.Clock()
fps = 60

debug_hud = False

if __name__ == "__main__":
    player = open_map("test_map1.hcm")
    while running:
        canvas.fill("white")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    debug_hud = not debug_hud
        if not player.alive:
            player = open_map("test_map1.hcm")
        clock.tick(fps)
        pygame.display.set_caption(f"{clock.get_fps()}")
        objects.update()
        objects.draw(canvas)
        if player.rect.x >= 600:
            for i in everything:
                i.rect.x -= 5

        elif player.rect.x <= 200:
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
