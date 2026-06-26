

import pygame
import sys
import traceback
from game import Jogo

def main():
    pygame.init()
    pygame.display.set_caption("  Craque do jogo ")

    try:
        jogo = Jogo()
        jogo.run()
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        print("\n[ERRO] O jogo encontrou um problema e foi encerrado.")
        input("Pressione ENTER para fechar...")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
