"""
game.py – Classe Jogo: máquina de estados principal do Quiz do Craque.
"""

import pygame
import sys
import os
import random
import math

from constants   import *
from entities    import Fase, TextoAnimado, Particula
from renderer    import UI, Estadio
from fases_data  import FASES_DATA

class Jogo:

    def __init__(self):
        self.screen = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("⚽  Quiz do Craque  ⚽")
        self.clock       = pygame.time.Clock()
        self.ui          = UI(self.screen)
        self.estadio_menu = Estadio(VERDE_CAMPO, (60, 60, 80))
        self._bola_menu_img = self._carregar_bola_menu()

        self._reset_state()

    def _carregar_bola_menu(self) -> pygame.Surface | None:
        """Carrega a imagem da bola usada no menu (fundo já removido)."""
        caminho = os.path.join("assets", "bola_menu.png")
        if os.path.exists(caminho):
            try:
                return pygame.image.load(caminho).convert_alpha()
            except Exception as e:
                print(f"[AVISO] Não carregou imagem {caminho}: {e}")
        return None

    
    def _reset_state(self):
        self.fases          = [Fase(d) for d in FASES_DATA]
        self.fase_idx       = 0
        self._score         = 0
        self._score_fase    = 0
        self.particulas     = []
        self.estado         = MENU
        self._tick          = 0
        self._opcao_hover   = -1
        self._ultimo_acerto = None
        self._texto_animado = None
        self._fade          = 0
        self._fade_dir      = 0
        self._proximo_estado = None
        self._feedback_timer = 0
        self._opcao_sel     = -1
        self._img_cache     = {}   # cache de imagens redimensionadas
        self._progresso_iniciado = False
        self._erros_cartao = 0
        self._cartao_estado = None  # None | "amarelo" | "vermelho"
        self._fase_maxima_desbloqueada = 0   # índice mais alto já liberado
        self._fases_aprovadas = set()        # índices das fases já concluídas


    @property
    def fase(self) -> Fase:
        return self.fases[self.fase_idx]

  
    def run(self):
        while True:
            self._tick += 1
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

  
    def _get_imagem_fase(self, idx: int, altura: int = 230) -> pygame.Surface | None:
        key = (idx, altura)
        if key not in self._img_cache:
            self._img_cache[key] = self.fases[idx].get_imagem(altura)
        return self._img_cache[key]

    # ── EVENTOS ──────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.estado != MENU:
                        self.estado = MENU

                if self.estado == MENU and event.key == pygame.K_SPACE:
                    self._continuar_ou_iniciar()

                if self.estado == INTRO_FASE:
                    if self._texto_animado and not self._texto_animado.concluido():
                        self._texto_animado.pular()
                    elif event.key == pygame.K_SPACE:
                        self.estado = PERGUNTA

                if self.estado == VITORIA and event.key == pygame.K_SPACE:
                    self._reset_state()

                if self.estado == GAME_OVER and event.key == pygame.K_r:
                    self._reset_state()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)
                if self.estado == FEEDBACK and self.fase.concluida():
                    self.estado = RESULTADO
                    self._feedback_timer = 0

    def _handle_click(self, pos):
        if self.estado == MENU:
            bx, by = LARGURA // 2 - 140, ALTURA // 2 + 120
            if bx <= pos[0] <= bx + 280 and by <= pos[1] <= by + 58:
                self._continuar_ou_iniciar()
            return

        if self.estado == SELECAO_FASES:
            if self._clique_voltar_menu(pos):
                return
            idx = self._clique_fase_card(pos)
            if idx is not None:
                self._iniciar_fase(idx)
            return

        # Botão "Voltar ao Menu" disponível em todas as telas de fase
        if self.estado in (INTRO_FASE, PERGUNTA, FEEDBACK, RESULTADO):
            if self._clique_voltar_menu(pos):
                return

        if self.estado == INTRO_FASE:
            if self._texto_animado and not self._texto_animado.concluido():
                self._texto_animado.pular()
            else:
                self.estado = PERGUNTA

        elif self.estado == PERGUNTA:
            for i in range(4):
                rx, ry, rw, rh = self._opcao_rect(i)
                if rx <= pos[0] <= rx + rw and ry <= pos[1] <= ry + rh:
                    self._responder(i)

        elif self.estado == RESULTADO:
            bx, by = LARGURA // 2 - 120, ALTURA - 95
            if bx <= pos[0] <= bx + 240 and by <= pos[1] <= by + 54:
                if self._feedback_timer <= 0:
                    self._avancar_ou_gameover()

        elif self.estado == FEEDBACK:
            # Botão de recomeçar imediato quando levou vermelho
            if self._cartao_estado == "vermelho" and self._clique_reiniciar_fase(pos):
                self._iniciar_fase(self.fase_idx)
                return
            if self._feedback_timer <= 0:
                self.estado = PERGUNTA

        elif self.estado in (VITORIA, GAME_OVER):
            self._reset_state()

    # ── UPDATE ───────────────────────────────────────────
    def _update(self):
        for p in self.particulas[:]:
            p.update()
            if p.morta():
                self.particulas.remove(p)

        if self._texto_animado:
            self._texto_animado.update()

        if self._feedback_timer > 0:
            self._feedback_timer -= 1
            if self._feedback_timer <= 0 and self.estado == FEEDBACK:
                # Cartões: em caso de erro, NÃO avançar para a próxima pergunta.
                # (Para vermelho, o recomeço da fase acontece imediatamente aqui.)
                if not self._ultimo_acerto:
                    if self._cartao_estado == "vermelho":
                        self._iniciar_fase(self.fase_idx)
                        return
                    # erro amarelo: mantém a mesma pergunta no FEEDBACK
                    return

                if not self.fase.concluida():
                    self.estado = PERGUNTA

        if self._fade_dir != 0:
            self._fade += self._fade_dir * 8
            self._fade = max(0, min(255, self._fade))
            if self._fade >= 255 and self._fade_dir == 1 and self._proximo_estado:
                self.estado      = self._proximo_estado
                self._proximo_estado = None
                self._fade_dir   = -1
            elif self._fade <= 0:
                self._fade_dir = 0

        mx, my = pygame.mouse.get_pos()
        self._opcao_hover = -1
        if self.estado == PERGUNTA:
            for i in range(4):
                rx, ry, rw, rh = self._opcao_rect(i)
                if rx <= mx <= rx + rw and ry <= my <= ry + rh:
                    self._opcao_hover = i

    # ── DRAW PRINCIPAL ───────────────────────────────────
    def _draw(self):
        dispatch = {
            MENU:          self._draw_menu,
            SELECAO_FASES: self._draw_selecao_fases,
            INTRO_FASE: self._draw_intro,
            PERGUNTA:   self._draw_pergunta,
            FEEDBACK:   self._draw_feedback,
            RESULTADO:  self._draw_resultado,
            VITORIA:    self._draw_vitoria,
            GAME_OVER:  self._draw_gameover,
        }
        dispatch.get(self.estado, lambda: None)()

        for p in self.particulas:
            p.draw(self.screen)

        if self._fade > 0:
            s = pygame.Surface((LARGURA, ALTURA))
            s.fill(PRETO)
            s.set_alpha(self._fade)
            self.screen.blit(s, (0, 0))

    # ─────────────────────────────────────────────────────
    #  BOLA MELHORADA — renderiza em Surface separada
    # ─────────────────────────────────────────────────────
    def _draw_bola(self, cx: int, cy: int, raio: int, angulo: float):
        """Desenha bola de futebol realista com painéis hexagonais."""
        surf = pygame.Surface((raio * 2 + 6, raio * 2 + 6), pygame.SRCALPHA)
        ox, oy = raio + 3, raio + 3

        # ── Sombra ──────────────────────────────────────
        somb = pygame.Surface((raio * 2 + 6, raio * 2 + 6), pygame.SRCALPHA)
        pygame.draw.ellipse(somb, (0, 0, 0, 60),
                            (4, raio // 3 + 4, raio * 2, raio * 2 // 3))
        self.screen.blit(somb, (cx - ox, cy - oy + raio + 6))


        # ── Corpo branco com gradiente simulado ─────────
        pygame.draw.circle(surf, (240, 240, 240), (ox, oy), raio)

        # Brilho (reflexo) — círculo menor branco intenso
        brilho_x = ox - raio // 3
        brilho_y = oy - raio // 3
        brilho_r = raio // 4
        brilho_surf = pygame.Surface((brilho_r * 2, brilho_r * 2), pygame.SRCALPHA)
        for r2 in range(brilho_r, 0, -1):
            alpha = int(180 * (r2 / brilho_r) ** 0.5)
            pygame.draw.circle(brilho_surf, (255, 255, 255, alpha),
                               (brilho_r, brilho_r), r2)
        surf.blit(brilho_surf, (brilho_x - brilho_r, brilho_y - brilho_r),
                  special_flags=pygame.BLEND_RGBA_ADD)

        # ── Painéis pretos (pentágonos) ──────────────────
        # Centro + 5 painéis ao redor (clássico de futebol)
        panel_pts_list = []

        def make_hex(cx2, cy2, r, rot):
            pts = []
            for k in range(6):
                a = rot + k * math.pi / 3
                pts.append((cx2 + int(r * math.cos(a)), cy2 + int(r * math.sin(a))))
            return pts

        # Painel central
        panel_pts_list.append(make_hex(ox, oy, raio // 3, angulo))

        # 5 painéis orbitais
        for k in range(5):
            a   = angulo + k * 2 * math.pi / 5
            dist = raio * 0.58
            px  = ox + int(dist * math.cos(a))
            py  = oy + int(dist * math.sin(a))
            # Clamp dentro do círculo
            if math.hypot(px - ox, py - oy) + raio // 3 <= raio:
                panel_pts_list.append(make_hex(px, py, raio // 4, angulo + k * 0.3))

        for pts in panel_pts_list:
            # Clip to circle
            clipped = [p for p in pts
                       if math.hypot(p[0] - ox, p[1] - oy) <= raio - 1]
            if len(clipped) >= 3:
                pygame.draw.polygon(surf, (30, 30, 30), clipped)
            if len(pts) >= 3:
                # Draw outline only
                pygame.draw.polygon(surf, (40, 40, 40), pts, 1)

        # ── Borda da bola ────────────────────────────────
        pygame.draw.circle(surf, (60, 60, 60), (ox, oy), raio, 2)

        self.screen.blit(surf, (cx - ox, cy - oy))

    # ─────────────────────────────────────────────────────
    #  BOTÃO PREMIUM
    # ─────────────────────────────────────────────────────
    def _draw_botao(self, x: int, y: int, w: int, h: int,
                    label: str, cor_base: tuple, cor_borda: tuple,
                    pulse: int = 0, hover: bool = False):
        """Desenha botão com gradiente, brilho e sombra."""
        # Sombra
        somb = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        pygame.draw.rect(somb, (0, 0, 0, 80), (0, 0, w + 8, h + 8), border_radius=14)
        self.screen.blit(somb, (x - 4 + 4, y - 4 + 6))


        # Fundo com gradiente vertical
        btn = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(h):
            t = i / h
            if hover:
                r = int(cor_base[0] * (1 - t * 0.3) + 40 * (1 - t))
                g = int(cor_base[1] * (1 - t * 0.3) + 40 * (1 - t))
                b = int(cor_base[2] * (1 - t * 0.3) + 40 * (1 - t))
            else:
                r = int(cor_base[0] * (1.2 - t * 0.4))
                g = int(cor_base[1] * (1.2 - t * 0.4))
                b = int(cor_base[2] * (1.2 - t * 0.4))
            r, g, b = min(255, r), min(255, g), min(255, b)
            pygame.draw.line(btn, (r, g, b, 230), (0, i), (w, i))

        # Arredonda
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=13)
        btn.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.screen.blit(btn, (x, y))

        # Borda exterior com glow
        if hover:
            glow = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*cor_borda, 80), (0, 0, w + 10, h + 10), border_radius=16)
            self.screen.blit(glow, (x - 5, y - 5))

        pygame.draw.rect(self.screen, cor_borda, (x, y, w, h), 3, border_radius=13)

        # Linha de brilho no topo
        brilho_surf = pygame.Surface((w - 20, 3), pygame.SRCALPHA)
        brilho_surf.fill((255, 255, 255, 80))
        self.screen.blit(brilho_surf, (x + 10, y + 5))

        # Texto centralizado
        self.ui.texto(label, x + w // 2, y + h // 2 - 12,
                      cor_borda, self.ui.fonte_grande, centralizar=True)

    # ── MENU ─────────────────────────────────────────────
    def _draw_menu(self):
        self.estadio_menu.draw(self.screen)

        # Painel central semi-transparente
        self.ui.caixa(LARGURA // 2 - 310, 40, 620, ALTURA - 80,
                      (0, 0, 0), DOURADO, raio=18, alpha=175)

        # Bola do menu — imagem com fundo removido, com flutuação suave
        angle  = self._tick * 0.025
        bx     = LARGURA // 2 + int(60 * math.cos(angle))
        by_pos = 100 + int(14 * math.sin(angle * 2))
        if self._bola_menu_img:
            tam = 84
            if "_bola_menu_pequena" not in self.__dict__:
                self._bola_menu_pequena = pygame.transform.smoothscale(
                    self._bola_menu_img, (tam, tam)
                )
            rot_graus = -(angle * 1.8) * 180 / math.pi
            img_final = pygame.transform.rotozoom(self._bola_menu_pequena, rot_graus, 1.0)
            fw, fh = img_final.get_size()
            self.screen.blit(img_final, (bx - fw // 2, by_pos - fh // 2))
        else:
            self._draw_bola(bx, by_pos, 32, angle * 1.8)

        # Chamada para a tela de seleção de fases
        self.ui.texto("⚽  QUIZ DO CRAQUE  ⚽", LARGURA // 2, 150,
                      DOURADO, self.ui.fonte_titulo, centralizar=True)
        self.ui.texto("Prove que você é um craque!", LARGURA // 2, 210,
                      BRANCO, self.ui.fonte_media, centralizar=True)
        self.ui.texto("5 fases incríveis te esperam pela frente.", LARGURA // 2, 252,
                      AMARELO, self.ui.fonte_pequena, centralizar=True)

        # Botão JOGAR melhorado
        bx2, by2 = LARGURA // 2 - 140, ALTURA // 2 + 120
        pulse = int(8 * math.sin(self._tick * 0.1))
        mx, my = pygame.mouse.get_pos()
        hover_btn = (bx2 - 5 <= mx <= bx2 + 285 and by2 - 5 <= my <= by2 + 63)
        label_jogar = "▶  CONTINUAR" if self._progresso_iniciado else "▶   JOGAR"
        self._draw_botao(bx2 - pulse // 2, by2 - pulse // 4,
                         280 + pulse, 58 + pulse // 2,
                         label_jogar,
                         (0, 120, 30), DOURADO,
                         pulse=pulse, hover=hover_btn)

        # Score
        if self._score > 0:
            self.ui.texto(f"SCORE: {self._score}", 14, 10, DOURADO, self.ui.fonte_media)
        dica = "ESPAÇO = continuar" if self._progresso_iniciado else "ESPAÇO = jogar"
        self.ui.texto(f"ESC = voltar ao menu  |  {dica}", LARGURA // 2, ALTURA - 24,
                      CINZA, self.ui.fonte_mini, centralizar=True)

    # ── SELEÇÃO DE FASES ─────────────────────────────────
    def _fase_card_rect(self, i: int):
        """Retângulo do card da fase i na tela de seleção de fases."""
        n         = len(self.fases)
        margem_x  = 30
        gap       = 14
        largura_total = LARGURA - margem_x * 2
        card_w    = (largura_total - gap * (n - 1)) // n
        card_h    = 440
        x = margem_x + i * (card_w + gap)
        y = 140
        return (x, y, card_w, card_h)

    def _clique_fase_card(self, pos):
        """Retorna o índice da fase clicada (se desbloqueada) ou None."""
        for i in range(len(self.fases)):
            if i > self._fase_maxima_desbloqueada:
                continue
            rx, ry, rw, rh = self._fase_card_rect(i)
            if rx <= pos[0] <= rx + rw and ry <= pos[1] <= ry + rh:
                return i
        return None

    def _draw_selecao_fases(self):
        self.estadio_menu.draw(self.screen)

        W, H = LARGURA, ALTURA
        self.ui.texto("⚽  ESCOLHA SUA FASE  ⚽", W // 2, 28,
                      DOURADO, self.ui.fonte_titulo, centralizar=True)
        self.ui.texto("Clique em um craque desbloqueado para jogar",
                      W // 2, 84, BRANCO, self.ui.fonte_pequena, centralizar=True)

        mx, my = pygame.mouse.get_pos()

        for i, fd in enumerate(FASES_DATA):
            rx, ry, rw, rh = self._fase_card_rect(i)
            desbloqueada = i <= self._fase_maxima_desbloqueada
            aprovada     = i in self._fases_aprovadas
            hover        = desbloqueada and rx <= mx <= rx + rw and ry <= my <= ry + rh

            cor_borda = DOURADO if hover else (fd["cor_clube"] if desbloqueada else CINZA_ESC)
            cor_fundo = fd["cor_clube"] if desbloqueada else (35, 35, 35)
            self.ui.caixa(rx, ry, rw, rh, cor_fundo, cor_borda,
                          raio=14, alpha=225 if desbloqueada else 170)

            if hover:
                glow = pygame.Surface((rw + 10, rh + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*DOURADO, 50), (0, 0, rw + 10, rh + 10), border_radius=18)
                self.screen.blit(glow, (rx - 5, ry - 5))

            # Número da fase
            self.ui.texto(str(i + 1), rx + 12, ry + 8,
                          DOURADO if desbloqueada else CINZA, self.ui.fonte_grande)

            # Imagem do jogador
            img = self._get_imagem_fase(i, altura=150)
            if img:
                iw, ih = img.get_size()
                ix = rx + rw // 2 - iw // 2
                iy = ry + 26
                if desbloqueada:
                    self.screen.blit(img, (ix, iy))
                else:
                    sombra_img = img.copy()
                    sombra_img.set_alpha(70)
                    self.screen.blit(sombra_img, (ix, iy))

            # Nome / clube
            cor_nome  = fd["cor_destaque"] if desbloqueada else CINZA
            cor_clube = BRANCO if desbloqueada else CINZA_ESC
            self.ui.texto(fd["jogador"], rx + rw // 2, ry + 184,
                          cor_nome, self.ui.fonte_media, centralizar=True)
            self.ui.texto(fd["clube"], rx + rw // 2, ry + 208,
                          cor_clube, self.ui.fonte_pequena, centralizar=True)

            # Status
            if not desbloqueada:
                self.ui.texto("🔒 BLOQUEADA", rx + rw // 2, ry + rh - 36,
                              CINZA, self.ui.fonte_pequena, centralizar=True)
            elif aprovada:
                self.ui.texto("⭐ APROVADO", rx + rw // 2, ry + rh - 36,
                              VERDE_LIMA, self.ui.fonte_pequena, centralizar=True)
            else:
                pulse = int(4 * math.sin(self._tick * 0.15)) if hover else 0
                self.ui.texto("▶ JOGAR" + (" " * 0), rx + rw // 2, ry + rh - 36 - pulse,
                              AMARELO if hover else BRANCO, self.ui.fonte_pequena, centralizar=True)

        self._draw_botao_voltar_menu()

        if self._score > 0:
            self.ui.texto(f"SCORE: {self._score}", 14, 10,
                          DOURADO, self.ui.fonte_media)

        self.ui.texto("ESC ou 🏠 Menu = voltar ao menu principal",
                      W // 2, H - 26, CINZA, self.ui.fonte_mini, centralizar=True)


    # ── INTRO FASE ───────────────────────────────────────
    def _draw_intro(self):
        estadio = Estadio(VERDE_CAMPO, self.fase.cor_arquibancada)
        estadio._tick = self._tick
        estadio.draw(self.screen)

        W, H = LARGURA, ALTURA
        # painel esquerdo
        self.ui.caixa(20, 20, W // 2 - 30, H - 40, (0, 0, 0),
                      self.fase.cor_clube, raio=14, alpha=210)

        self.ui.texto(f"FASE {self.fase_idx + 1} de {len(self.fases)}",
                      W // 4, 40, DOURADO, self.ui.fonte_grande, centralizar=True)
        self.ui.texto(self.fase.jogador, W // 4, 80,
                      self.fase.cor_destaque, self.ui.fonte_titulo, centralizar=True)
        self.ui.texto(self.fase.clube, W // 4, 136,
                      BRANCO, self.ui.fonte_media, centralizar=True)

        desc_linhas = self.ui.wrap_text(self.fase.descricao, self.ui.fonte_pequena, W // 2 - 60)
        for i, l in enumerate(desc_linhas):
            self.ui.texto(l, W // 4, 168 + i * 22, CINZA, self.ui.fonte_pequena, centralizar=True)

        intro = f"Responda {len(self.fase.perguntas)} perguntas e mostre\nque você merece a camisa de\n{self.fase.jogador}!"
        if self._texto_animado is None:
            self._texto_animado = TextoAnimado(intro, velocidade=2)
        t = self._texto_animado.get()
        for i, linha in enumerate(t.split("\n")):
            self.ui.texto(linha, W // 4, 270 + i * 30,
                          VERDE_LIMA, self.ui.fonte_media, centralizar=True, sombra=False)

        if self._texto_animado.concluido():
            pulse = int(6 * math.sin(self._tick * 0.1))
            self._draw_botao(W // 4 - 120 - pulse // 2, H - 80 - pulse // 4,
                             240 + pulse, 50 + pulse // 2,
                             "ESPAÇO / CLIQUE",
                             (0, 80, 0), AMARELO, hover=False)

        # Imagem do jogador no painel direito
        img = self._get_imagem_fase(self.fase_idx, altura=int(H * 0.65))
        if img:
            iw, ih = img.get_size()
            ix = W // 2 + (W // 2 - iw) // 2
            iy = (H - ih) // 2
            self.screen.blit(img, (ix, iy))
        else:
            self.ui.texto("🏃", W * 3 // 4, H // 2, self.fase.cor_clube,
                          self.ui.fonte_titulo, centralizar=True)

        self._draw_botao_voltar_menu()

    # ── PERGUNTA ─────────────────────────────────────────
    def _draw_pergunta(self):
        estadio = Estadio(VERDE_CAMPO, self.fase.cor_arquibancada)
        estadio._tick = self._tick
        estadio.draw(self.screen)

        p     = self.fase.proxima_pergunta()
        if p is None:
            return
        num   = self.fase.pergunta_atual + 1
        total = len(self.fase.perguntas)
        W, H  = LARGURA, ALTURA

        # HUD topo com gradiente
        hud = pygame.Surface((W, 54), pygame.SRCALPHA)
        for i in range(54):
            alpha = int(230 * (1 - i / 54 * 0.3))
            pygame.draw.line(hud, (0, 0, 0, alpha), (0, i), (W, i))
        self.screen.blit(hud, (0, 0))

        self.ui.texto(f"Fase {self.fase_idx + 1}: {self.fase.jogador}",
                      12, 10, self.fase.cor_destaque, self.ui.fonte_media)
        self.ui.texto(f"Pergunta {num}/{total}", W // 2, 10, BRANCO,
                      self.ui.fonte_media, centralizar=True)

        # Cartões da fase + score
        self._draw_cartoes_hud(W - 280, 8)
        self.ui.texto(f"{self._score} pts", W - 160, 10, AMARELO, self.ui.fonte_media)

        # Barra de progresso
        self.ui.barra_progresso(10, 44, W - 20, 8,
                                (num - 1) / total,
                                cor_preench=self.fase.cor_destaque)

        self._draw_botao_voltar_menu()

        # Imagem lateral do jogador
        img = self._get_imagem_fase(self.fase_idx, altura=int(H * 0.40))
        if img:
            iw, ih = img.get_size()
            self.screen.blit(img, (10, H - ih - 10))

        # Caixa da pergunta com gradiente
        linhas = self.ui.wrap_text(p.texto, self.ui.fonte_media, 500)
        ph = 40 + len(linhas) * 30
        self.ui.caixa_gradiente(150, 60, W - 170, ph + 8,
                                (0, 10, 40), (0, 0, 20), raio=12)
        pygame.draw.rect(self.screen, self.fase.cor_clube,
                         (150, 60, W - 170, ph + 8), 2, border_radius=12)
        self.ui.texto("❓", 164, 70, AMARELO, self.ui.fonte_grande)
        for i, l in enumerate(linhas):
            self.ui.texto(l, 205, 70 + i * 30, BRANCO, self.ui.fonte_media)

        # Opções melhoradas
        for i in range(4):
            rx, ry, rw, rh = self._opcao_rect(i)
            hover   = i == self._opcao_hover
            letra   = "ABCD"[i]

            # Sombra da opção
            somb = pygame.Surface((rw + 4, rh + 4), pygame.SRCALPHA)
            pygame.draw.rect(somb, (0, 0, 0, 60), (0, 0, rw + 4, rh + 4), border_radius=12)
            self.screen.blit(somb, (rx - 2 + 3, ry - 2 + 4))


            # Fundo com gradiente
            opt_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
            if hover:
                c1, c2 = (30, 100, 30), (10, 60, 10)
            else:
                c1, c2 = (20, 20, 60), (5, 5, 30)
            for row in range(rh):
                t = row / rh
                r2 = int(c1[0] + (c2[0] - c1[0]) * t)
                g2 = int(c1[1] + (c2[1] - c1[1]) * t)
                b2 = int(c1[2] + (c2[2] - c1[2]) * t)
                pygame.draw.line(opt_surf, (r2, g2, b2, 220), (0, row), (rw, row))
            mask2 = pygame.Surface((rw, rh), pygame.SRCALPHA)
            pygame.draw.rect(mask2, (255, 255, 255, 255), (0, 0, rw, rh), border_radius=10)
            opt_surf.blit(mask2, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            self.screen.blit(opt_surf, (rx, ry))

            # Borda com glow ao hover
            cor_brd = self.fase.cor_destaque if hover else CINZA_MEDIO
            borda_w = 3 if hover else 2
            pygame.draw.rect(self.screen, cor_brd, (rx, ry, rw, rh), borda_w, border_radius=10)

            if hover:
                glow2 = pygame.Surface((rw + 8, rh + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow2, (*self.fase.cor_destaque, 40),
                                 (0, 0, rw + 8, rh + 8), border_radius=14)
                self.screen.blit(glow2, (rx - 4, ry - 4))

            # Badge da letra
            badge_cor = self.fase.cor_destaque if hover else CINZA
            self.ui.caixa(rx + 6, ry + 8, 34, 34, badge_cor, PRETO, raio=8, alpha=220)
            self.ui.texto(letra, rx + 23, ry + 12, PRETO if hover else BRANCO,
                          self.ui.fonte_media, centralizar=True)

            # Texto da opção
            txt_cor = DOURADO if hover else BRANCO
            # Remover sombra do texto dentro do botão da alternativa
            self.ui.texto(p.opcoes[i], rx + 52, ry + 14, txt_cor, self.ui.fonte_media, sombra=False)


    def _opcao_rect(self, i: int):
        col = i % 2
        row = i // 2
        x   = 150 + col * 375
        y   = 390 + row * 85
        return x, y, 355, 70

    # ── BOTÃO VOLTAR AO MENU (mantém progresso) ──────────
    def _voltar_menu_rect(self):
        """Retângulo do botão 'Voltar ao Menu', exibido durante as fases."""
        return (LARGURA - 168, 10, 158, 34)

    def _draw_botao_voltar_menu(self):
        """Desenha um botão discreto para voltar ao menu sem perder o progresso."""
        rx, ry, rw, rh = self._voltar_menu_rect()
        mx, my = pygame.mouse.get_pos()
        hover  = rx <= mx <= rx + rw and ry <= my <= ry + rh

        s = pygame.Surface((rw, rh), pygame.SRCALPHA)
        cor_fundo = (40, 40, 40, 215) if not hover else (70, 70, 20, 230)
        pygame.draw.rect(s, cor_fundo, (0, 0, rw, rh), border_radius=8)
        self.screen.blit(s, (rx, ry))
        cor_borda = AMARELO if hover else CINZA
        pygame.draw.rect(self.screen, cor_borda, (rx, ry, rw, rh), 2, border_radius=8)
        self.ui.texto("🏠 Menu", rx + rw // 2, ry + 7,
                      AMARELO if hover else BRANCO,
                      self.ui.fonte_pequena, centralizar=True, sombra=False)

    def _clique_voltar_menu(self, pos) -> bool:
        rx, ry, rw, rh = self._voltar_menu_rect()
        if rx <= pos[0] <= rx + rw and ry <= pos[1] <= ry + rh:
            self.estado = MENU
            return True
        return False

    def _draw_cartoes_hud(self, x: int, y: int):
        """Desenha os dois cartões da fase no HUD (cinza/amarelo/vermelho)."""
        cw, ch, gap = 18, 26, 6
        for i in range(2):
            cx = x + i * (cw + gap)
            if i == 0:
                # Primeiro cartão: amarelo se houve 1 erro, vermelho se 2, cinza se limpo
                if self._cartao_estado == "vermelho":
                    cor = VERMELHO
                elif self._cartao_estado == "amarelo":
                    cor = AMARELO
                else:
                    cor = CINZA_ESC
            else:
                # Segundo cartão: vermelho apenas se levou vermelho, senão cinza
                cor = VERMELHO if self._cartao_estado == "vermelho" else CINZA_ESC
            # Sombra
            somb = pygame.Surface((cw + 2, ch + 2), pygame.SRCALPHA)
            pygame.draw.rect(somb, (0, 0, 0, 100), (0, 0, cw + 2, ch + 2), border_radius=3)
            self.screen.blit(somb, (cx + 2, y + 2))
            # Cartão
            pygame.draw.rect(self.screen, cor, (cx, y, cw, ch), border_radius=3)
            pygame.draw.rect(self.screen, BRANCO, (cx, y, cw, ch), 1, border_radius=3)

    # ── FEEDBACK ─────────────────────────────────────────
    def _reiniciar_fase_rect(self):
        """Retângulo do botão 'Recomeçar fase' (mostrado no cartão vermelho)."""
        bx, by = LARGURA // 2 - 170, ALTURA - 95
        return (bx, by, 340, 52)

    def _clique_reiniciar_fase(self, pos) -> bool:
        rx, ry, rw, rh = self._reiniciar_fase_rect()
        if rx <= pos[0] <= rx + rw and ry <= pos[1] <= ry + rh:
            return True
        return False

    def _draw_feedback(self):
        estadio = Estadio(VERDE_CAMPO, self.fase.cor_arquibancada)
        estadio._tick = self._tick
        estadio.draw(self.screen)
        self._draw_pergunta()

        s    = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        alfa = 155
        # No erro: 1º amarelo, 2º vermelho (e seguintes)
        if self._ultimo_acerto:
            cor = (0, 100, 0, alfa)
        else:
            cor = (180, 140, 0, alfa) if self._cartao_estado == "amarelo" else (120, 0, 0, alfa)
        s.fill(cor)
        self.screen.blit(s, (0, 0))

        W, H = LARGURA, ALTURA
        if self._ultimo_acerto:
            self.ui.texto("✅  CORRETO!", W // 2, H // 2 - 40,
                          VERDE_LIMA, self.ui.fonte_titulo, centralizar=True,
                          sombra=False)
            self.ui.texto(f"+{10 * (self.fase_idx + 1)} pontos!",
                          W // 2, H // 2 + 30, DOURADO, self.ui.fonte_grande, centralizar=True,
                          sombra=False)
        else:
            p = self.fase.perguntas[self.fase.pergunta_atual - 1]
            acertou_texto = p.opcoes[p.resposta_idx]
            erro_texto    = p.opcoes[self._opcao_sel] if 0 <= self._opcao_sel < len(p.opcoes) else "—"

            self.ui.texto("❌  ERROU!", W // 2, H // 2 - 65,
                          VERMELHO if self._cartao_estado == "vermelho" else AMARELO,
                          self.ui.fonte_titulo, centralizar=True,
                          sombra=False)

            # Erro da pessoa (escolha)
            self.ui.texto("Você escolheu:", W // 2, H // 2 - 10,
                          BRANCO, self.ui.fonte_media, centralizar=True,
                          sombra=False)
            self.ui.texto(erro_texto, W // 2, H // 2 + 25,
                          AMARELO if self._cartao_estado == "amarelo" else VERMELHO,
                          self.ui.fonte_grande, centralizar=True,
                          sombra=False)

            # Resposta correta (deslocada para não sobrepor o cartão)
            self.ui.texto("Resposta correta:", W // 2, H // 2 + 135,
                          BRANCO, self.ui.fonte_media, centralizar=True,
                          sombra=False)
            self.ui.texto(acertou_texto, W // 2, H // 2 + 170,
                          AMARELO, self.ui.fonte_grande, centralizar=True,
                          sombra=False)

        # Cartões (apenas em caso de erro)
        if (not self._ultimo_acerto) and self._cartao_estado:
            # Mostra o cartão com base na SEQUÊNCIA de erro atual
            if self._cartao_estado == "amarelo":
                self.ui.texto("🟨  CARTÃO AMARELO!", W // 2, H // 2 + 95,
                              AMARELO, self.ui.fonte_media, centralizar=True,
                              sombra=False)
            elif self._cartao_estado == "vermelho":
                # Mostra explicitamente que levou vermelho e vai recomeçar
                self.ui.texto("🟥  CARTÃO VERMELHO!  RECOMEÇANDO...",
                              W // 2, H // 2 + 95,
                              VERMELHO, self.ui.fonte_media,
                              centralizar=True,
                              sombra=False)

                # Botão de recomeçar fase (clique imediato)
                rx, ry, rw, rh = self._reiniciar_fase_rect()
                mx, my = pygame.mouse.get_pos()
                hover = rx <= mx <= rx + rw and ry <= my <= ry + rh

                sbtn = pygame.Surface((rw, rh), pygame.SRCALPHA)
                cor_fundo = (80, 0, 0, 230) if hover else (50, 0, 0, 210)
                pygame.draw.rect(sbtn, cor_fundo, (0, 0, rw, rh), border_radius=10)
                pygame.draw.rect(sbtn, AMARELO if hover else CINZA, (0, 0, rw, rh), 2, border_radius=10)
                self.screen.blit(sbtn, (rx, ry))

                self.ui.texto("↺  Recomeçar fase",
                              rx + rw // 2, ry + 8,
                              AMARELO if hover else BRANCO,
                              self.ui.fonte_pequena,
                              centralizar=True,
                              sombra=False)

        self._draw_botao_voltar_menu()

    # ── RESULTADO ────────────────────────────────────────
    def _draw_resultado(self):
        estadio = Estadio(VERDE_CAMPO, self.fase.cor_arquibancada)
        estadio._tick = self._tick
        estadio.draw(self.screen)

        aprovado = self.fase.aprovado()
        W, H     = LARGURA, ALTURA

        self.ui.caixa(80, 50, W - 160, H - 100, (0, 0, 0),
                      self.fase.cor_clube, raio=16, alpha=230)

        if aprovado:
            self.ui.texto(f"🏆  VOCÊ É {self.fase.jogador.upper()}!",
                          W // 2, 70, DOURADO, self.ui.fonte_grande, centralizar=True)
        else:
            self.ui.texto("😢  Não foi dessa vez...",
                          W // 2, 70, VERMELHO, self.ui.fonte_grande, centralizar=True)

        img = self._get_imagem_fase(self.fase_idx, altura=int(H * 0.48))
        if img:
            iw, ih = img.get_size()
            self.screen.blit(img, (W // 2 - iw // 2, 115))

        self.ui.texto(f"Acertos: {self.fase.acertos} / {len(self.fase.perguntas)}",
                      W // 2, H - 165,
                      VERDE_LIMA if aprovado else VERMELHO,
                      self.ui.fonte_grande, centralizar=True)

        if aprovado:
            self.ui.texto(f"Score nesta fase: +{self._score_fase}",
                          W // 2, H - 130, AMARELO, self.ui.fonte_media, centralizar=True)
        else:
            self.ui.texto("Tente novamente para passar de fase!",
                          W // 2, H - 130, AMARELO, self.ui.fonte_media, centralizar=True)

        # Botão continuar melhorado
        if self._feedback_timer <= 0:
            bx, by   = W // 2 - 120, H - 92
            pulse    = int(5 * math.sin(self._tick * 0.12))
            mx, my   = pygame.mouse.get_pos()
            hover_btn = bx - 5 <= mx <= bx + 245 and by - 5 <= my <= by + 59
            if aprovado:
                ultima = self.fase_idx + 1 >= len(self.fases)
                label = "Resultado Final ▶" if ultima else "Ver Fases ▶"
                cor_b = (0, 100, 20)
            else:
                label = "Ver Fases ▶"
                cor_b = (110, 10, 10)
            self._draw_botao(bx - pulse, by, 240 + pulse * 2, 54 + pulse // 2,
                             label, cor_b, DOURADO, pulse=pulse, hover=hover_btn)

        self._draw_botao_voltar_menu()

    # ── VITÓRIA ──────────────────────────────────────────
    def _draw_vitoria(self):
        self.screen.fill(COR_FUNDO)

        for i in range(40):
            random.seed(i + self._tick // 3)
            cx2 = random.randint(0, LARGURA)
            cy2 = (self._tick * 3 + i * 25) % ALTURA
            cor = random.choice([AMARELO, VERDE_LIMA, ROXO, LARANJA, VERMELHO, AZUL])
            pygame.draw.rect(self.screen, cor, (cx2, cy2, 12, 7))

        W, H = LARGURA, ALTURA
        self.ui.texto("🏆  PARABÉNS!  🏆", W // 2, 50,
                      DOURADO, self.ui.fonte_titulo, centralizar=True)
        self.ui.texto("Você é um verdadeiro CRAQUE DO FUTEBOL!", W // 2, 110,
                      BRANCO, self.ui.fonte_grande, centralizar=True)

        n     = len(self.fases)
        slot_w = W // n
        for i, fase in enumerate(self.fases):
            cx_slot = slot_w * i + slot_w // 2
            img     = self._get_imagem_fase(i, altura=130)
            if img:
                iw, ih = img.get_size()
                self.screen.blit(img, (cx_slot - iw // 2, 155))
            self.ui.texto(fase.jogador, cx_slot, 295,
                          AMARELO, self.ui.fonte_mini, centralizar=True)

        self.ui.texto(f"SCORE FINAL: {self._score}", W // 2, 340,
                      DOURADO, self.ui.fonte_titulo, centralizar=True)

        for i in range(5):
            angle  = self._tick * 0.05 + i * (2 * math.pi / 5)
            sx     = int(W // 2 + 180 * math.cos(angle))
            sy     = int(395 + 30 * math.sin(angle * 2))
            pygame.draw.circle(self.screen, DOURADO, (sx, sy), 8)

        # Bolas decorativas
        for i in range(3):
            bangle = self._tick * 0.04 + i * 2.1
            bx3 = int(W // 2 + 220 * math.cos(bangle))
            by3 = int(420 + 20 * math.sin(bangle * 2))
            self._draw_bola(bx3, by3, 16, bangle)

        self.ui.texto("[ ESPAÇO ou CLIQUE para o menu ]", W // 2, H - 48,
                      CINZA, self.ui.fonte_pequena, centralizar=True)

    # ── GAME OVER ────────────────────────────────────────
    def _draw_gameover(self):
        self.screen.fill((28, 0, 0))

        for i in range(20):
            random.seed(i + self._tick // 6)
            gx = random.randint(0, LARGURA)
            gy = (self._tick * 2 + i * 40) % ALTURA
            self.ui.texto("✕", gx, gy, (180, 0, 0), self.ui.fonte_pequena)

        W, H = LARGURA, ALTURA
        self.ui.texto("GAME  OVER", W // 2, 170,
                      VERMELHO, self.ui.fonte_titulo, centralizar=True)
        self.ui.texto(f"Score: {self._score}", W // 2, 260,
                      AMARELO, self.ui.fonte_grande, centralizar=True)
        self.ui.texto(f"Chegou até: {self.fase.jogador}", W // 2, 310,
                      BRANCO, self.ui.fonte_media, centralizar=True)

        img = self._get_imagem_fase(self.fase_idx, altura=150)
        if img:
            iw, ih = img.get_size()
            self.screen.blit(img, (W // 2 - iw // 2, 330))

        # Botões de recomeçar
        mx2, my2 = pygame.mouse.get_pos()
        hover_r = W // 2 - 110 <= mx2 <= W // 2 + 110 and H - 80 <= my2 <= H - 30
        self._draw_botao(W // 2 - 110, H - 80, 220, 50,
                         "[ R ] Recomeçar",
                         (80, 0, 0), VERMELHO, hover=hover_r)

    # ── LÓGICA ───────────────────────────────────────────
    def _continuar_ou_iniciar(self):
        """Chamado pelo botão JOGAR/CONTINUAR do menu: leva o jogador
        para a tela de seleção de fases."""
        self.estado = SELECAO_FASES

    def _iniciar_fase(self, idx: int):
        self.fase_idx       = idx
        self.fases[idx]     = Fase(FASES_DATA[idx])
        self._texto_animado = None
        self._score_fase    = 0
        self.estado         = INTRO_FASE
        self._progresso_iniciado = True
        # cartões: zerar ao (re)começar a fase
        self._erros_cartao = 0
        self._cartao_estado = None


    def _responder(self, idx: int):
        acerto          = self.fase.responder(idx)
        self._ultimo_acerto = acerto
        self._opcao_sel = idx

        cx, cy = LARGURA // 2, ALTURA // 2

        # Cor das partículas: acerto verde; erro depende do cartão (amarelo no 1º erro, vermelho no 2º)
        if acerto:
            cor = VERDE_LIMA
        else:
            cor = AMARELO if (self._erros_cartao + 1) == 1 else VERMELHO

        for _ in range(22):
            self.particulas.append(Particula(cx, cy, cor, acerto))

        if acerto:
            pts             = 10 * (self.fase_idx + 1)
            self._score     += pts
            self._score_fase += pts
            # acerto limpa o cartão amarelo
            self._erros_cartao = 0
            self._cartao_estado = None
        else:
            self._erros_cartao += 1
            if self._erros_cartao == 1:
                self._cartao_estado = "amarelo"
            elif self._erros_cartao >= 2:
                self._cartao_estado = "vermelho"
                # vermelho: exibe feedback e reinicia a fase


        self._feedback_timer = 80
        self.estado          = FEEDBACK


        if self.fase.concluida():
            self._feedback_timer = 80
            pygame.time.set_timer(pygame.USEREVENT, 1400)

        # Se levou vermelho, recomeça a fase após ~2s mantendo o FEEDBACK
        if (not acerto) and self._cartao_estado == "vermelho":
            self._feedback_timer = max(self._feedback_timer, 120)  # ~120 frames @60FPS
            return



    def _avancar_ou_gameover(self):
        if self.fase.aprovado():
            self._fases_aprovadas.add(self.fase_idx)
            prox = self.fase_idx + 1
            if prox >= len(self.fases):
                self.estado = VITORIA
            else:
                self._fase_maxima_desbloqueada = max(self._fase_maxima_desbloqueada, prox)
                self.fase_idx = prox
                self.estado = SELECAO_FASES
        else:
            # Não aprovado: volta à seleção para tentar de novo
            self.estado = SELECAO_FASES
