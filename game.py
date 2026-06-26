from __future__ import annotations

import pygame
import sys
import os
import random
import math
import json
from datetime import datetime

from constants   import *
from entities    import Fase, TextoAnimado, Particula
from renderer    import UI, Estadio
from fases_data  import FASES_DATA

LEADERBOARD_FILE = "leaderboard.json"
MAX_RECORDES     = 10

class Jogo:

    def __init__(self):
        self.screen = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("⚽  Quiz do Craque  ⚽")
        self.clock        = pygame.time.Clock()
        self.ui           = UI(self.screen)
        self.estadio_menu = Estadio(VERDE_CAMPO, (60, 60, 80))
        self._bola_menu_img = self._carregar_bola_menu()
        self._img_cartao_amarelo = self._carregar_imagem_cartao(asset_path("cartao_amarelo.png"))
        self._img_cartao_vermelho = self._carregar_imagem_cartao(asset_path("cartao_vermelho.png"))
        self._cartao_anim_timer = 0

        self._som = self._inicializar_audio()

        self._leaderboard     = self._carregar_leaderboard()
        self._nome_digitando  = ""
        self._entrada_nome    = False
        self._nome_salvo      = False

        self._reset_state()

    def _carregar_imagem_cartao(self, caminho: str) -> pygame.Surface | None:
        if os.path.exists(caminho):
            try:
                img = pygame.image.load(caminho).convert_alpha()
                w, h = img.get_size()
                nova_h = 330
                nova_w = int(w * nova_h / h)
                return pygame.transform.smoothscale(img, (nova_w, nova_h))
            except Exception as e:
                print(f"[AVISO] Não carregou imagem {caminho}: {e}")
        return None

    def _carregar_bola_menu(self) -> pygame.Surface | None:
        caminho = asset_path("bola_menu.png")
        if os.path.exists(caminho):
            try:
                return pygame.image.load(caminho).convert_alpha()
            except Exception as e:
                print(f"[AVISO] Não carregou imagem {caminho}: {e}")
        return None

    def _inicializar_audio(self) -> dict:
        sons = {k: None for k in ("acerto", "erro", "amarelo", "vermelho",
                                   "vitoria", "clique", "musica")}
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"[ÁUDIO] mixer não iniciou: {e}")
            return sons

        mapa = {
            "acerto":   asset_path("sons", "acerto.wav"),
            "erro":     asset_path("sons", "erro.wav"),
            "amarelo":  asset_path("sons", "amarelo.wav"),
            "vermelho": asset_path("sons", "vermelho.wav"),
            "vitoria":  asset_path("sons", "vitoria.wav"),
            "clique":   asset_path("sons", "clique.wav"),
            "musica":   asset_path("sons", "musica_fundo.mp3"),
        }
        for chave, caminho in mapa.items():
            if not os.path.exists(caminho):
                continue
            try:
                if chave == "musica":
                    sons[chave] = caminho          
                else:
                    s = pygame.mixer.Sound(caminho)
                    s.set_volume(0.7)
                    sons[chave] = s
            except Exception as e:
                print(f"[ÁUDIO] não carregou {caminho}: {e}")

        if sons["musica"]:
            try:
                pygame.mixer.music.load(sons["musica"])
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"[ÁUDIO] música não tocou: {e}")

        return sons

    def _tocar(self, nome: str):
        s = self._som.get(nome)
        if s and isinstance(s, pygame.mixer.Sound):
            s.play()

    def _carregar_leaderboard(self) -> list:
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return [d for d in dados
                    if isinstance(d, dict) and "nome" in d and "score" in d]
        except Exception as e:
            print(f"[LEADERBOARD] erro ao carregar: {e}")
            return []

    def _salvar_leaderboard(self):
        try:
            with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
                json.dump(self._leaderboard, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[LEADERBOARD] erro ao salvar: {e}")

    def _registrar_score(self, nome: str):
        nome = nome.strip() or "Anônimo"
        entrada = {
            "nome":  nome[:20],
            "score": self._score,
            "data":  datetime.now().strftime("%d/%m/%Y"),
        }
        self._leaderboard.append(entrada)
        self._leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self._leaderboard = self._leaderboard[:MAX_RECORDES]
        self._salvar_leaderboard()
        self._nome_salvo = True

    def _score_entra_no_ranking(self) -> bool:
        if self._score <= 0:
            return False
        if len(self._leaderboard) < MAX_RECORDES:
            return True
        return self._score > self._leaderboard[-1]["score"]

    
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
        self._pts_ganhos    = 0
        self._img_cache     = {}
        self._progresso_iniciado = False
        self._erros_cartao  = 0
        self._cartao_estado = None
        self._cartao_anim_timer = 0
        self._fase_maxima_desbloqueada = 0
        self._fases_aprovadas = set()
        self._timer_pergunta = 0
        self._timer_max      = 15 * FPS
        self._ajuda_usada       = False
        self._opcoes_eliminadas = []
        self._nome_digitando = ""
        self._entrada_nome   = False
        self._nome_salvo     = False


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

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self._entrada_nome and not self._nome_salvo:
                    if event.key == pygame.K_RETURN:
                        self._registrar_score(self._nome_digitando)
                        self._tocar("clique")
                    elif event.key == pygame.K_BACKSPACE:
                        self._nome_digitando = self._nome_digitando[:-1]
                    elif len(self._nome_digitando) < 20 and event.unicode.isprintable():
                        self._nome_digitando += event.unicode
                    return 

                if event.key == pygame.K_ESCAPE:
                    if self.estado == LEADERBOARD:
                        self.estado = MENU
                    elif self.estado != MENU:
                        self.estado = MENU

                if self.estado == MENU and event.key == pygame.K_SPACE:
                    self._continuar_ou_iniciar()

                if self.estado == INTRO_FASE:
                    if self._texto_animado and not self._texto_animado.concluido():
                        self._texto_animado.pular()
                    elif event.key == pygame.K_SPACE:
                        self.estado = PERGUNTA
                        self._timer_pergunta = self._timer_max

                if self.estado == VITORIA and event.key == pygame.K_SPACE:
                    if self._score_entra_no_ranking() and not self._nome_salvo:
                        self._entrada_nome = True
                        self.estado = LEADERBOARD
                    else:
                        self._reset_state()

                if self.estado == LEADERBOARD and event.key == pygame.K_SPACE:
                    if self._nome_salvo or not self._score_entra_no_ranking():
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
        self._tocar("clique")

        if self.estado == MENU:
            bx, by = LARGURA // 2 - 140, ALTURA // 2 + 120
            if bx <= pos[0] <= bx + 280 and by <= pos[1] <= by + 58:
                self._continuar_ou_iniciar()
            lbx, lby = LARGURA // 2 - 90, ALTURA // 2 + 194
            if lbx <= pos[0] <= lbx + 180 and lby <= pos[1] <= lby + 38:
                self.estado = LEADERBOARD
            return

        if self.estado == LEADERBOARD:
            bx, by = LARGURA // 2 - 100, ALTURA - 72
            if bx <= pos[0] <= bx + 200 and by <= pos[1] <= by + 44:
                if self._nome_salvo or not self._score_entra_no_ranking():
                    self._reset_state()
            return

        if self.estado == SELECAO_FASES:
            if self._clique_voltar_menu(pos):
                return
            idx = self._clique_fase_card(pos)
            if idx is not None:
                self._iniciar_fase(idx)
            return

        if self.estado in (INTRO_FASE, PERGUNTA, FEEDBACK, RESULTADO):
            if self._clique_voltar_menu(pos):
                return

        if self.estado == INTRO_FASE:
            if self._texto_animado and not self._texto_animado.concluido():
                self._texto_animado.pular()
            else:
                self.estado = PERGUNTA
                self._timer_pergunta = self._timer_max

        elif self.estado == PERGUNTA:
            if not self._ajuda_usada and self._clique_dica_treinador(pos):
                self._usar_dica()
                return
            for i in range(4):
                if i in self._opcoes_eliminadas:
                    continue
                rx, ry, rw, rh = self._opcao_rect(i)
                if rx <= pos[0] <= rx + rw and ry <= pos[1] <= ry + rh:
                    self._responder(i)

        elif self.estado == RESULTADO:
            bx, by = LARGURA // 2 - 120, ALTURA - 95
            if bx <= pos[0] <= bx + 240 and by <= pos[1] <= by + 54:
                if self._feedback_timer <= 0:
                    self._avancar_ou_gameover()

        elif self.estado == FEEDBACK:
            if self._cartao_estado == "vermelho" and self._clique_reiniciar_fase(pos):
                self._iniciar_fase(self.fase_idx)
                return
            if self._feedback_timer <= 0:
                if self.fase.concluida():
                    self.estado = RESULTADO
                else:
                    self.estado = PERGUNTA
                    self._timer_pergunta = self._timer_max

        elif self.estado in (VITORIA, GAME_OVER):
            self._reset_state()

    def _update(self):
        for p in self.particulas[:]:
            p.update()
            if p.morta():
                self.particulas.remove(p)

        if self._texto_animado:
            self._texto_animado.update()

        if self.estado == PERGUNTA:
            if self._timer_pergunta > 0:
                self._timer_pergunta -= 1
                if self._timer_pergunta == 0:
                    self._tocar("erro")
                    self._responder_timeout()

        if self._feedback_timer > 0:
            self._feedback_timer -= 1
            if self._feedback_timer <= 0 and self.estado == FEEDBACK:
                if not self._ultimo_acerto:
                    if self._cartao_estado == "vermelho":
                        self._iniciar_fase(self.fase_idx)
                        return
                    if self.fase.concluida():
                        self.estado = RESULTADO
                        self._feedback_timer = 0
                    return

                if not self.fase.concluida():
                    self.estado = PERGUNTA
                    self._timer_pergunta = self._timer_max  
                    self._opcoes_eliminadas = []            

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

    def _draw(self):
        dispatch = {
            MENU:          self._draw_menu,
            SELECAO_FASES: self._draw_selecao_fases,
            INTRO_FASE:    self._draw_intro,
            PERGUNTA:      self._draw_pergunta,
            FEEDBACK:      self._draw_feedback,
            RESULTADO:     self._draw_resultado,
            VITORIA:       self._draw_vitoria,
            GAME_OVER:     self._draw_gameover,
            LEADERBOARD:   self._draw_leaderboard,
        }
        dispatch.get(self.estado, lambda: None)()

        for p in self.particulas:
            p.draw(self.screen)

        if self._fade > 0:
            s = pygame.Surface((LARGURA, ALTURA))
            s.fill(PRETO)
            s.set_alpha(self._fade)
            self.screen.blit(s, (0, 0))


    def _draw_bola(self, cx: int, cy: int, raio: int, angulo: float):
        surf = pygame.Surface((raio * 2 + 6, raio * 2 + 6), pygame.SRCALPHA)
        ox, oy = raio + 3, raio + 3

        somb = pygame.Surface((raio * 2 + 6, raio * 2 + 6), pygame.SRCALPHA)
        pygame.draw.ellipse(somb, (0, 0, 0, 60),
                            (4, raio // 3 + 4, raio * 2, raio * 2 // 3))
        self.screen.blit(somb, (cx - ox, cy - oy + raio + 6))


        pygame.draw.circle(surf, (240, 240, 240), (ox, oy), raio)

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

        panel_pts_list = []

        def make_hex(cx2, cy2, r, rot):
            pts = []
            for k in range(6):
                a = rot + k * math.pi / 3
                pts.append((cx2 + int(r * math.cos(a)), cy2 + int(r * math.sin(a))))
            return pts
        panel_pts_list.append(make_hex(ox, oy, raio // 3, angulo))

        for k in range(5):
            a   = angulo + k * 2 * math.pi / 5
            dist = raio * 0.58
            px  = ox + int(dist * math.cos(a))
            py  = oy + int(dist * math.sin(a))
            if math.hypot(px - ox, py - oy) + raio // 3 <= raio:
                panel_pts_list.append(make_hex(px, py, raio // 4, angulo + k * 0.3))

        for pts in panel_pts_list:
            clipped = [p for p in pts
                       if math.hypot(p[0] - ox, p[1] - oy) <= raio - 1]
            if len(clipped) >= 3:
                pygame.draw.polygon(surf, (30, 30, 30), clipped)
            if len(pts) >= 3:
                pygame.draw.polygon(surf, (40, 40, 40), pts, 1)

        pygame.draw.circle(surf, (60, 60, 60), (ox, oy), raio, 2)

        self.screen.blit(surf, (cx - ox, cy - oy))

    def _draw_botao(self, x: int, y: int, w: int, h: int,
                    label: str, cor_base: tuple, cor_borda: tuple,
                    pulse: int = 0, hover: bool = False):

        somb = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        pygame.draw.rect(somb, (0, 0, 0, 80), (0, 0, w + 8, h + 8), border_radius=14)
        self.screen.blit(somb, (x - 4 + 4, y - 4 + 6))


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

        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=13)
        btn.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.screen.blit(btn, (x, y))

        if hover:
            glow = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*cor_borda, 80), (0, 0, w + 10, h + 10), border_radius=16)
            self.screen.blit(glow, (x - 5, y - 5))

        pygame.draw.rect(self.screen, cor_borda, (x, y, w, h), 3, border_radius=13)

        brilho_surf = pygame.Surface((w - 20, 3), pygame.SRCALPHA)
        brilho_surf.fill((255, 255, 255, 80))
        self.screen.blit(brilho_surf, (x + 10, y + 5))


        self.ui.texto(label, x + w // 2, y + h // 2 - 12,
                      cor_borda, self.ui.fonte_grande, centralizar=True)

    def _draw_menu(self):
        self.estadio_menu.draw(self.screen)

        self.ui.caixa(LARGURA // 2 - 310, 40, 620, ALTURA - 80,
                      (0, 0, 0), DOURADO, raio=18, alpha=175)

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

        self.ui.texto("⚽  QUIZ DO CRAQUE  ⚽", LARGURA // 2, 150,
                      DOURADO, self.ui.fonte_titulo, centralizar=True)
        self.ui.texto("Prove que você é um craque!", LARGURA // 2, 210,
                      BRANCO, self.ui.fonte_media, centralizar=True)
        self.ui.texto("5 fases incríveis te esperam pela frente.", LARGURA // 2, 252,
                      AMARELO, self.ui.fonte_pequena, centralizar=True)

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

        if self._score > 0:
            self.ui.texto(f"SCORE: {self._score}", 14, 10, DOURADO, self.ui.fonte_media)
        dica = "ESPAÇO = continuar" if self._progresso_iniciado else "ESPAÇO = jogar"
        self.ui.texto(f"ESC = voltar ao menu  |  {dica}", LARGURA // 2, ALTURA - 24,
                      CINZA, self.ui.fonte_mini, centralizar=True)

        lbx, lby = LARGURA // 2 - 90, ALTURA // 2 + 194
        mx2, my2 = pygame.mouse.get_pos()
        hover_lb = lbx <= mx2 <= lbx + 180 and lby <= my2 <= lby + 38
        self._draw_botao(lbx, lby, 180, 38, "🏆 Recordes",
                         (60, 50, 0), DOURADO, hover=hover_lb)

    def _fase_card_rect(self, i: int):
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

            self.ui.texto(str(i + 1), rx + 12, ry + 8,
                          DOURADO if desbloqueada else CINZA, self.ui.fonte_grande)

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

            cor_nome  = fd["cor_destaque"] if desbloqueada else CINZA
            cor_clube = BRANCO if desbloqueada else CINZA_ESC
            self.ui.texto(fd["jogador"], rx + rw // 2, ry + 184,
                          cor_nome, self.ui.fonte_media, centralizar=True)
            self.ui.texto(fd["clube"], rx + rw // 2, ry + 208,
                          cor_clube, self.ui.fonte_pequena, centralizar=True)

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


    def _draw_intro(self):
        estadio = Estadio(VERDE_CAMPO, self.fase.cor_arquibancada)
        estadio._tick = self._tick
        estadio.draw(self.screen)

        W, H = LARGURA, ALTURA
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

        hud = pygame.Surface((W, 54), pygame.SRCALPHA)
        for i in range(54):
            alpha = int(230 * (1 - i / 54 * 0.3))
            pygame.draw.line(hud, (0, 0, 0, alpha), (0, i), (W, i))
        self.screen.blit(hud, (0, 0))

        self.ui.texto(f"Fase {self.fase_idx + 1}: {self.fase.jogador}",
                      12, 10, self.fase.cor_destaque, self.ui.fonte_media)
        self.ui.texto(f"Pergunta {num}/{total}", W // 2, 10, BRANCO,
                      self.ui.fonte_media, centralizar=True)

        self._draw_cartoes_hud(W - 280, 8)
        self.ui.texto(f"{self._score} pts", W - 160, 10, AMARELO, self.ui.fonte_media)

        self.ui.barra_progresso(10, 44, W - 20, 8,
                                (num - 1) / total,
                                cor_preench=self.fase.cor_destaque)

        self._draw_botao_voltar_menu()

        img = self._get_imagem_fase(self.fase_idx, altura=int(H * 0.40))
        if img:
            iw, ih = img.get_size()
            self.screen.blit(img, (10, H - ih - 10))

        linhas = self.ui.wrap_text(p.texto, self.ui.fonte_media, 500)
        ph = 40 + len(linhas) * 30
        self.ui.caixa_gradiente(150, 60, W - 170, ph + 8,
                                (0, 10, 40), (0, 0, 20), raio=12)
        pygame.draw.rect(self.screen, self.fase.cor_clube,
                         (150, 60, W - 170, ph + 8), 2, border_radius=12)
        self.ui.texto("❓", 164, 70, AMARELO, self.ui.fonte_grande)
        for i, l in enumerate(linhas):
            self.ui.texto(l, 205, 70 + i * 30, BRANCO, self.ui.fonte_media)

        for i in range(4):
            rx, ry, rw, rh = self._opcao_rect(i)
            hover      = i == self._opcao_hover
            letra      = "ABCD"[i]
            eliminada  = i in self._opcoes_eliminadas

            somb = pygame.Surface((rw + 4, rh + 4), pygame.SRCALPHA)
            pygame.draw.rect(somb, (0, 0, 0, 60), (0, 0, rw + 4, rh + 4), border_radius=12)
            self.screen.blit(somb, (rx - 2 + 3, ry - 2 + 4))

            opt_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
            if eliminada:
                c1, c2 = (18, 18, 18), (10, 10, 10)
            elif hover:
                c1, c2 = (30, 100, 30), (10, 60, 10)
            else:
                c1, c2 = (20, 20, 60), (5, 5, 30)
            for row in range(rh):
                t = row / rh
                r2 = int(c1[0] + (c2[0] - c1[0]) * t)
                g2 = int(c1[1] + (c2[1] - c1[1]) * t)
                b2 = int(c1[2] + (c2[2] - c1[2]) * t)
                pygame.draw.line(opt_surf, (r2, g2, b2, 220 if not eliminada else 130),
                                 (0, row), (rw, row))
            mask2 = pygame.Surface((rw, rh), pygame.SRCALPHA)
            pygame.draw.rect(mask2, (255, 255, 255, 255), (0, 0, rw, rh), border_radius=10)
            opt_surf.blit(mask2, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            self.screen.blit(opt_surf, (rx, ry))

            if eliminada:
                cor_brd, borda_w = (50, 50, 50), 1
            else:
                cor_brd = self.fase.cor_destaque if hover else CINZA_MEDIO
                borda_w = 3 if hover else 2
            pygame.draw.rect(self.screen, cor_brd, (rx, ry, rw, rh), borda_w, border_radius=10)

            if hover and not eliminada:
                glow2 = pygame.Surface((rw + 8, rh + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow2, (*self.fase.cor_destaque, 40),
                                 (0, 0, rw + 8, rh + 8), border_radius=14)
                self.screen.blit(glow2, (rx - 4, ry - 4))

            if eliminada:
                badge_cor = (50, 50, 50)
                self.ui.caixa(rx + 6, ry + 8, 34, 34, badge_cor, (80, 80, 80), raio=8, alpha=180)
                self.ui.texto("✕", rx + 23, ry + 12, (160, 50, 50),
                              self.ui.fonte_media, centralizar=True, sombra=False)
            else:
                badge_cor = self.fase.cor_destaque if hover else CINZA
                self.ui.caixa(rx + 6, ry + 8, 34, 34, badge_cor, PRETO, raio=8, alpha=220)
                self.ui.texto(letra, rx + 23, ry + 12, PRETO if hover else BRANCO,
                              self.ui.fonte_media, centralizar=True)

            txt_cor = (70, 70, 70) if eliminada else (DOURADO if hover else BRANCO)
            self.ui.texto(p.opcoes[i], rx + 52, ry + 14, txt_cor,
                          self.ui.fonte_media, sombra=False)

            if eliminada:
                risco = pygame.Surface((rw, rh), pygame.SRCALPHA)
                pygame.draw.line(risco, (150, 50, 50, 90), (8, 8), (rw - 8, rh - 8), 2)
                self.screen.blit(risco, (rx, ry))

        if self._timer_max > 0:
            ratio    = self._timer_pergunta / self._timer_max
            segundos = math.ceil(self._timer_pergunta / FPS)
            if ratio > 0.5:
                cor_timer = VERDE_ESC
            elif ratio > 0.25:
                cor_timer = AMARELO
            else:
                cor_timer = VERMELHO
            bw, bh = W - 160, 12
            bx_t   = 150
            by_t   = 564
            self.ui.barra_progresso(bx_t, by_t, bw, bh, ratio,
                                    cor_preench=cor_timer, cor_fundo=(30, 30, 30))
            self.ui.texto(f"{segundos}s", bx_t + bw + 8, by_t - 2,
                          cor_timer, self.ui.fonte_pequena, sombra=False)
            pts_base    = 10 * (self.fase_idx + 1)
            segs_gastos = int((self._timer_max - self._timer_pergunta) / FPS)
            pts_agora   = max(1, pts_base - segs_gastos)
            self.ui.texto(f"⚡ +{pts_agora} pts", bx_t - 2, by_t - 18,
                          cor_timer, self.ui.fonte_mini, sombra=False)

        self._draw_dica_treinador()


    def _opcao_rect(self, i: int):
        col = i % 2
        row = i // 2
        x   = 150 + col * 375
        y   = 390 + row * 85
        return x, y, 355, 70

    def _voltar_menu_rect(self):
        return (LARGURA - 168, 10, 158, 34)

    def _draw_botao_voltar_menu(self):
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

    def _dica_treinador_rect(self):
        return (14, 310, 122, 60)

    def _clique_dica_treinador(self, pos) -> bool:
        rx, ry, rw, rh = self._dica_treinador_rect()
        return rx <= pos[0] <= rx + rw and ry <= pos[1] <= ry + rh

    def _usar_dica(self):
        p = self.fase.proxima_pergunta()
        if p is None or self._ajuda_usada:
            return
        erradas = [i for i in range(4) if i != p.resposta_idx]
        random.shuffle(erradas)
        self._opcoes_eliminadas = erradas[:2]
        self._ajuda_usada = True
        self._tocar("clique")

    def _draw_dica_treinador(self):
        if self._ajuda_usada:
            return

        rx, ry, rw, rh = self._dica_treinador_rect()
        mx, my = pygame.mouse.get_pos()
        hover  = rx <= mx <= rx + rw and ry <= my <= ry + rh

        somb = pygame.Surface((rw + 6, rh + 6), pygame.SRCALPHA)
        pygame.draw.rect(somb, (0, 0, 0, 80), (0, 0, rw + 6, rh + 6), border_radius=13)
        self.screen.blit(somb, (rx - 1, ry + 4))

        btn = pygame.Surface((rw, rh), pygame.SRCALPHA)
        c1 = (10, 90, 10) if hover else (5, 60, 5)
        c2 = (5,  50, 5)  if hover else (2, 30, 2)
        for row in range(rh):
            t  = row / rh
            r2 = int(c1[0] + (c2[0] - c1[0]) * t)
            g2 = int(c1[1] + (c2[1] - c1[1]) * t)
            b2 = int(c1[2] + (c2[2] - c1[2]) * t)
            pygame.draw.line(btn, (r2, g2, b2, 230), (0, row), (rw, row))
        mask = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rw, rh), border_radius=12)
        btn.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.screen.blit(btn, (rx, ry))

        if hover:
            glow = pygame.Surface((rw + 12, rh + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (50, 220, 50, 45), (0, 0, rw + 12, rh + 12), border_radius=16)
            self.screen.blit(glow, (rx - 6, ry - 6))

        cor_borda = VERDE_LIMA if hover else VERDE_ESC
        pygame.draw.rect(self.screen, cor_borda, (rx, ry, rw, rh), 2, border_radius=12)

        px, py = rx + 10, ry + 10
        pygame.draw.rect(self.screen, BRANCO,    (px, py, 22, 28), border_radius=3)
        pygame.draw.rect(self.screen, CINZA_ESC, (px, py, 22, 28), 1, border_radius=3)
        pygame.draw.rect(self.screen, CINZA, (px + 6, py - 4, 10, 6), border_radius=2)
        for li in range(3):
            pygame.draw.line(self.screen, CINZA_ESC,
                             (px + 3, py + 8 + li * 6),
                             (px + 18, py + 8 + li * 6), 1)

        cor_txt = VERDE_LIMA if hover else BRANCO
        self.ui.texto("DICA",      rx + 44, ry + 10, cor_txt,  self.ui.fonte_pequena, sombra=False)
        self.ui.texto("treinador", rx + 44, ry + 28, CINZA,    self.ui.fonte_mini,    sombra=False)

        brilho = pygame.Surface((rw - 16, 2), pygame.SRCALPHA)
        brilho.fill((255, 255, 255, 60))
        self.screen.blit(brilho, (rx + 8, ry + 5))

    def _draw_cartoes_hud(self, x: int, y: int):
        cw, ch, gap = 18, 26, 6
        for i in range(2):
            cx = x + i * (cw + gap)
            if i == 0:
                if self._cartao_estado == "vermelho":
                    cor = VERMELHO
                elif self._cartao_estado == "amarelo":
                    cor = AMARELO
                else:
                    cor = CINZA_ESC
            else:
                cor = VERMELHO if self._cartao_estado == "vermelho" else CINZA_ESC
            somb = pygame.Surface((cw + 2, ch + 2), pygame.SRCALPHA)
            pygame.draw.rect(somb, (0, 0, 0, 100), (0, 0, cw + 2, ch + 2), border_radius=3)
            self.screen.blit(somb, (cx + 2, y + 2))
            pygame.draw.rect(self.screen, cor, (cx, y, cw, ch), border_radius=3)
            pygame.draw.rect(self.screen, BRANCO, (cx, y, cw, ch), 1, border_radius=3)

    def _reiniciar_fase_rect(self):
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
            self.ui.texto(f"+{self._pts_ganhos} pontos!",
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

            self.ui.texto("Você escolheu:", W // 2, H // 2 - 10,
                          BRANCO, self.ui.fonte_media, centralizar=True,
                          sombra=False)
            self.ui.texto(erro_texto, W // 2, H // 2 + 25,
                          AMARELO if self._cartao_estado == "amarelo" else VERMELHO,
                          self.ui.fonte_grande, centralizar=True,
                          sombra=False)

            self.ui.texto("Resposta correta:", W // 2, H // 2 + 135,
                          BRANCO, self.ui.fonte_media, centralizar=True,
                          sombra=False)
            self.ui.texto(acertou_texto, W // 2, H // 2 + 170,
                          AMARELO, self.ui.fonte_grande, centralizar=True,
                          sombra=False)

        if (not self._ultimo_acerto) and self._cartao_estado:
            if self._cartao_estado == "amarelo":
                self.ui.texto("🟨  CARTÃO AMARELO!", W // 2, H // 2 + 95,
                              AMARELO, self.ui.fonte_media, centralizar=True,
                              sombra=False)
            elif self._cartao_estado == "vermelho":
                self.ui.texto("🟥  CARTÃO VERMELHO!  RECOMEÇANDO...",
                              W // 2, H // 2 + 95,
                              VERMELHO, self.ui.fonte_media,
                              centralizar=True,
                              sombra=False)

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

        self._draw_cartao_img()
        self._draw_botao_voltar_menu()


    def _draw_cartao_img(self):
        if self._cartao_estado is None or self._ultimo_acerto:
            return
        img = (self._img_cartao_amarelo if self._cartao_estado == "amarelo"
               else self._img_cartao_vermelho)
        if img is None:
            return

        iw, ih = img.get_size()
        margem = 18
        dest_x = LARGURA - iw - margem
        dest_y_final = ALTURA - ih - margem

        total_frames = 30
        if self._cartao_anim_timer < total_frames:
            progresso = self._cartao_anim_timer / total_frames
            progresso = 1 - (1 - progresso) ** 2 
            offset_y = int((ih + margem) * (1 - progresso))
            dest_y = dest_y_final + offset_y
            self._cartao_anim_timer += 1
        else:
            dest_y = dest_y_final

        self.screen.blit(img, (dest_x, dest_y))

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

        for i in range(3):
            bangle = self._tick * 0.04 + i * 2.1
            bx3 = int(W // 2 + 220 * math.cos(bangle))
            by3 = int(420 + 20 * math.sin(bangle * 2))
            self._draw_bola(bx3, by3, 16, bangle)

        if self._score_entra_no_ranking():
            msg = "🏆 Você entrou no ranking!  ESPAÇO = ver recordes"
        else:
            msg = "[ ESPAÇO ou CLIQUE para o menu ]"
        self.ui.texto(msg, W // 2, H - 48,
                      DOURADO if self._score_entra_no_ranking() else CINZA,
                      self.ui.fonte_pequena, centralizar=True)

    def _draw_resultado(self):
        estadio = Estadio(VERDE_CAMPO, self.fase.cor_arquibancada)
        estadio._tick = self._tick
        estadio.draw(self.screen)

        W, H = LARGURA, ALTURA
        aprovado = self.fase.acertos >= 3

        self.ui.caixa(W // 2 - 260, 70, 520, 340,
                      (0, 0, 0), DOURADO if aprovado else CINZA, raio=18, alpha=200)

        titulo = "✅  FASE CONCLUÍDA!" if aprovado else "❌  NÃO FOI DESSA VEZ"
        cor_titulo = VERDE_LIMA if aprovado else VERMELHO
        self.ui.texto(titulo, W // 2, 110, cor_titulo,
                      self.ui.fonte_titulo, centralizar=True)

        img = self._get_imagem_fase(self.fase_idx, altura=150)
        if img:
            iw, ih = img.get_size()
            self.screen.blit(img, (W // 2 - iw // 2, 150))

        self.ui.texto(f"Acertos: {self.fase.acertos} / {len(self.fase.perguntas)}",
                      W // 2, 320, BRANCO, self.ui.fonte_grande, centralizar=True)

        if aprovado:
            self.ui.texto(f"Score nesta fase: +{self._score_fase}",
                          W // 2, 360, DOURADO, self.ui.fonte_media, centralizar=True)
        else:
            self.ui.texto("Você precisa de pelo menos 3 acertos para avançar.",
                          W // 2, 360, CINZA, self.ui.fonte_pequena, centralizar=True)

        self.ui.texto(f"SCORE TOTAL: {self._score}", W // 2, 50,
                      AMARELO, self.ui.fonte_media, centralizar=True)

        bx, by = W // 2 - 120, H - 95
        mx2, my2 = pygame.mouse.get_pos()
        hover = bx <= mx2 <= bx + 240 and by <= my2 <= by + 54
        habilitado = self._feedback_timer <= 0
        texto_btn = "Continuar ▶" if aprovado else "↺ Tentar de novo"
        self._draw_botao(bx, by, 240, 54, texto_btn,
                         (40, 60, 0) if aprovado else (60, 20, 0),
                         DOURADO if aprovado else VERMELHO,
                         hover=hover and habilitado)

        self._draw_botao_voltar_menu()

    def _draw_leaderboard(self):
        self.estadio_menu.draw(self.screen)
        W, H = LARGURA, ALTURA

        self.ui.caixa(W // 2 - 340, 20, 680, H - 40,
                      (0, 0, 0), DOURADO, raio=18, alpha=210)

        self.ui.texto("🏆  RECORDES  🏆", W // 2, 38,
                      DOURADO, self.ui.fonte_titulo, centralizar=True)

        y0 = 108
        self.ui.caixa(W // 2 - 310, y0 - 6, 620, 30,
                      (40, 30, 0), DOURADO, raio=6, alpha=200)
        self.ui.texto("#",      W // 2 - 290, y0, DOURADO, self.ui.fonte_pequena)
        self.ui.texto("Nome",   W // 2 - 250, y0, DOURADO, self.ui.fonte_pequena)
        self.ui.texto("Score",  W // 2 + 120, y0, DOURADO, self.ui.fonte_pequena)
        self.ui.texto("Data",   W // 2 + 210, y0, DOURADO, self.ui.fonte_pequena)

        if not self._leaderboard:
            self.ui.texto("Nenhum recorde ainda. Jogue e seja o primeiro!",
                          W // 2, H // 2, CINZA, self.ui.fonte_media, centralizar=True)
        else:
            for rank, entrada in enumerate(self._leaderboard):
                yl = y0 + 36 + rank * 36
                cor_linha = (20, 20, 40) if rank % 2 == 0 else (10, 10, 25)
                self.ui.caixa(W // 2 - 310, yl - 4, 620, 30,
                              cor_linha, (0, 0, 0), raio=4, alpha=160, espessura_borda=0)

                medalha = {0: "🥇", 1: "🥈", 2: "🥉"}.get(rank, f"{rank + 1}.")
                cor_pos = [DOURADO, (200, 200, 200), (180, 120, 60)][rank] if rank < 3 else CINZA
                self.ui.texto(medalha, W // 2 - 290, yl, cor_pos, self.ui.fonte_pequena)
                self.ui.texto(entrada["nome"],  W // 2 - 250, yl, BRANCO,  self.ui.fonte_pequena)
                self.ui.texto(str(entrada["score"]), W // 2 + 120, yl, AMARELO, self.ui.fonte_pequena)
                self.ui.texto(entrada.get("data", "—"), W // 2 + 210, yl, CINZA, self.ui.fonte_pequena)

        if self._entrada_nome and not self._nome_salvo:
            by_input = H - 175
            self.ui.caixa(W // 2 - 260, by_input - 10, 520, 90,
                          (0, 30, 0), VERDE_ESC, raio=10, alpha=230)
            self.ui.texto("Novo recorde! Digite seu nome:",
                          W // 2, by_input + 4, VERDE_LIMA, self.ui.fonte_media, centralizar=True)
            campo_w = 360
            campo_x = W // 2 - campo_w // 2
            pygame.draw.rect(self.screen, (30, 30, 30),
                             (campo_x, by_input + 34, campo_w, 36), border_radius=8)
            pygame.draw.rect(self.screen, VERDE_ESC,
                             (campo_x, by_input + 34, campo_w, 36), 2, border_radius=8)
            cursor = "|" if self._tick % 60 < 30 else " "
            self.ui.texto(self._nome_digitando + cursor,
                          campo_x + 10, by_input + 42,
                          BRANCO, self.ui.fonte_media, sombra=False)
            self.ui.texto("ENTER para confirmar",
                          W // 2, by_input + 78, CINZA, self.ui.fonte_mini, centralizar=True)
        elif self._nome_salvo:
            self.ui.texto(f"✅ Recorde salvo! Bem-vindo ao ranking, {self._nome_digitando}!",
                          W // 2, H - 145, VERDE_LIMA, self.ui.fonte_media, centralizar=True)

        bx, by = W // 2 - 100, H - 72
        mx2, my2 = pygame.mouse.get_pos()
        hover_v = bx <= mx2 <= bx + 200 and by <= my2 <= by + 44
        self._draw_botao(bx, by, 200, 44, "◀ Voltar",
                         (40, 40, 40), DOURADO, hover=hover_v)

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

        mx2, my2 = pygame.mouse.get_pos()
        hover_r = W // 2 - 110 <= mx2 <= W // 2 + 110 and H - 80 <= my2 <= H - 30
        self._draw_botao(W // 2 - 110, H - 80, 220, 50,
                         "[ R ] Recomeçar",
                         (80, 0, 0), VERMELHO, hover=hover_r)

    def _continuar_ou_iniciar(self):

        self.estado = SELECAO_FASES

    def _iniciar_fase(self, idx: int):
        self.fase_idx       = idx
        self.fases[idx]     = Fase(FASES_DATA[idx])
        self._texto_animado = None
        self._score_fase    = 0
        self.estado         = INTRO_FASE
        self._progresso_iniciado = True
        self._erros_cartao  = 0
        self._cartao_estado = None
        self._cartao_anim_timer = 0
        self._timer_pergunta = self._timer_max
        self._ajuda_usada       = False
        self._opcoes_eliminadas = []


    def _responder(self, idx: int):
        segundos_gastos = int((self._timer_max - self._timer_pergunta) / FPS)
        self._timer_pergunta = 0   # para o timer
        acerto          = self.fase.responder(idx)
        self._ultimo_acerto = acerto
        self._opcao_sel = idx

        cx, cy = LARGURA // 2, ALTURA // 2

        if acerto:
            cor = VERDE_LIMA
            self._tocar("acerto")
        else:
            cor = AMARELO if (self._erros_cartao + 1) == 1 else VERMELHO

        for _ in range(22):
            self.particulas.append(Particula(cx, cy, cor, acerto))

        if acerto:
            pts_base        = 10 * (self.fase_idx + 1)
            pts             = max(1, pts_base - segundos_gastos)
            self._pts_ganhos = pts
            self._score     += pts
            self._score_fase += pts
            self._erros_cartao = 0
            self._cartao_estado = None
            self._cartao_anim_timer = 0
        else:
            self._erros_cartao += 1
            if self._erros_cartao == 1:
                self._cartao_estado = "amarelo"
                self._cartao_anim_timer = 0
                self._tocar("amarelo")
            elif self._erros_cartao >= 2:
                self._cartao_estado = "vermelho"
                self._cartao_anim_timer = 0
                self._tocar("vermelho")

        self._feedback_timer = 80
        self.estado          = FEEDBACK

        if acerto and self.fase.concluida():
            self._feedback_timer = 80
            pygame.time.set_timer(pygame.USEREVENT, 1400)

        if (not acerto) and self._cartao_estado == "vermelho":
            self._feedback_timer = max(self._feedback_timer, 120)
            return

    def _responder_timeout(self):
        self._opcao_sel = -1
        self._ultimo_acerto = False

        self._erros_cartao += 1
        if self._erros_cartao == 1:
            self._cartao_estado = "amarelo"
            self._cartao_anim_timer = 0
            self._tocar("amarelo")
        else:
            self._cartao_estado = "vermelho"
            self._cartao_anim_timer = 0
            self._tocar("vermelho")

        cx, cy = LARGURA // 2, ALTURA // 2
        cor = AMARELO if self._cartao_estado == "amarelo" else VERMELHO
        for _ in range(18):
            self.particulas.append(Particula(cx, cy, cor, False))

        self.fase.responder(-1)
        self.fase.erros  = max(0, self.fase.erros - 1)
        self.fase.pergunta_atual = min(self.fase.pergunta_atual,
                                       len(self.fase.perguntas))

        self._feedback_timer = 80
        self.estado = FEEDBACK


        if self._cartao_estado == "vermelho":
            self._feedback_timer = max(self._feedback_timer, 120)



    def _avancar_ou_gameover(self):
        if self.fase.aprovado():
            self._fases_aprovadas.add(self.fase_idx)
            prox = self.fase_idx + 1
            if prox >= len(self.fases):
                self._tocar("vitoria")
                self.estado = VITORIA
            else:
                self._fase_maxima_desbloqueada = max(self._fase_maxima_desbloqueada, prox)
                self.fase_idx = prox
                self.estado = SELECAO_FASES
        else:
            self.estado = SELECAO_FASES
