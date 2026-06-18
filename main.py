

import pygame
import sys
from game import Jogo

def main():
    pygame.init()
    pygame.display.set_caption("  Craque do jogo ")

    try:
        jogo = Jogo()
        jogo.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
