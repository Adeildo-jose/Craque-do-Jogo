from __future__ import annotations

import pygame
import random
import math
import sys
from constants import *


def _carregar_fonte_emoji() -> pygame.font.Font | None:
    candidatas = [
        # Windows
        "segoeuiemoji", "seguiemj",
        # macOS
        "applecoloremoji",
        # Linux / genérico
        "notocoloremoji", "symbola", "dejavusans",
    ]
    for nome in candidatas:
        try:
            f = pygame.font.SysFont(nome, 22)
            # Verifica se a fonte realmente suporta um emoji básico
            surf = f.render("⚽", True, (255, 255, 255))
            if surf.get_width() > 4:   # fontes sem suporte retornam glifos minúsculos
                return f
        except Exception:
            pass
    return None


def _tem_emoji(texto: str) -> bool:
    """Retorna True se a string contiver algum caractere emoji/símbolo Unicode acima de U+00FF."""
    return any(ord(c) > 0x00FF for c in texto)


# ─────────────────────────────────────────────────────────
#  CLASSE: UI  —  helpers de desenho de texto e formas
# ─────────────────────────────────────────────────────────
class UI:
    def __init__(self, screen: pygame.Surface):
        self.screen        = screen
        self.fonte_titulo  = pygame.font.SysFont("monospace", 46, bold=True)
        self.fonte_grande  = pygame.font.SysFont("monospace", 30, bold=True)
        self.fonte_media   = pygame.font.SysFont("monospace", 21, bold=True)
        self.fonte_pequena = pygame.font.SysFont("monospace", 15)
        self.fonte_mini    = pygame.font.SysFont("monospace", 12)

        # Fonte dedicada a emojis (pode ser None se o sistema não tiver)
        self._fonte_emoji = _carregar_fonte_emoji()

        # Mapeamento de emojis para substitutos ASCII/texto, usado como
        # fallback quando nenhuma fonte emoji está disponível.
        self._EMOJI_FALLBACK = {
            "⚽": "[bola]",
            "🏆": "[trofeu]",
            "😢": "[triste]",
            "🔒": "[bloq]",
            "⭐": "[*]",
            "❤":  "<3",
            "❓": "[?]",
            "✅": "[OK]",
            "❌": "[X]",
            "🟨": "[AM]",
            "🟥": "[VM]",
            "🏠": "[menu]",
            "🏃": "[jogador]",
            "✕":  "x",
            "↺":  "<<",
        }

    # ── helpers internos ──────────────────────────────────

    def _substituir_emojis(self, txt: str) -> str:
        """Substitui cada emoji pelo seu texto alternativo."""
        for emoji, sub in self._EMOJI_FALLBACK.items():
            txt = txt.replace(emoji, sub)
        return txt

    def _render_com_emoji(self, txt: str, fonte_base: pygame.font.Font,
                          cor: tuple) -> pygame.Surface:
        """
        Renderiza uma string misturando a fonte base (para texto ASCII)
        e a fonte emoji (para caracteres acima de U+00FF).
        Retorna um Surface com a linha completa.
        """
        # Separa a string em segmentos: texto normal / emoji
        segmentos = []   # lista de (texto, é_emoji)
        buf, modo_emoji = "", False
        for ch in txt:
            eh_emoji = ord(ch) > 0x00FF
            if eh_emoji != modo_emoji:
                if buf:
                    segmentos.append((buf, modo_emoji))
                buf, modo_emoji = ch, eh_emoji
            else:
                buf += ch
        if buf:
            segmentos.append((buf, modo_emoji))

        # Renderiza cada segmento
        surfs = []
        altura_max = fonte_base.get_height()
        for seg_txt, eh_emoji in segmentos:
            if eh_emoji and self._fonte_emoji:
                s = self._fonte_emoji.render(seg_txt, True, cor)
            else:
                # Fallback: substitui por texto ASCII
                seg_limpo = self._substituir_emojis(seg_txt) if eh_emoji else seg_txt
                s = fonte_base.render(seg_limpo, True, cor)
            surfs.append(s)
            altura_max = max(altura_max, s.get_height())

        # Junta tudo horizontalmente
        largura_total = sum(s.get_width() for s in surfs)
        resultado = pygame.Surface((max(1, largura_total), altura_max),
                                   pygame.SRCALPHA)
        x_off = 0
        for s in surfs:
            # Centraliza verticalmente dentro da linha
            y_off = (altura_max - s.get_height()) // 2
            resultado.blit(s, (x_off, y_off))
            x_off += s.get_width()
        return resultado

    # ── Texto ──────────────────────────────────────────
    def texto(self, txt: str, x: int, y: int,
              cor: tuple = BRANCO,
              fonte: pygame.font.Font = None,
              centralizar: bool = False,
              sombra: bool = True,
              sombra_offset: int = 2):
        f = fonte or self.fonte_media

        if _tem_emoji(txt):
            # Renderização especial para strings com emoji
            if sombra:
                s_somb = self._render_com_emoji(txt, f, PRETO)
                rs = s_somb.get_rect()
                rs.x = (x - s_somb.get_width() // 2 if centralizar else x) + sombra_offset
                rs.y = y + sombra_offset
                self.screen.blit(s_somb, rs)

            surf = self._render_com_emoji(txt, f, cor)
            r = surf.get_rect()
            r.x = x - surf.get_width() // 2 if centralizar else x
            r.y = y
            self.screen.blit(surf, r)
            return r
        else:
            # Caminho original (sem emoji) – inalterado
            if sombra:
                s  = f.render(txt, True, PRETO)
                rs = s.get_rect()
                rs.centerx = x if centralizar else x + sombra_offset
                rs.y       = y + sombra_offset
                self.screen.blit(s, rs)
            surf = f.render(txt, True, cor)
            r    = surf.get_rect()
            if centralizar:
                r.centerx = x
            else:
                r.x = x
            r.y = y
            self.screen.blit(surf, r)
            return r

    def texto_multilinha(self, linhas: list, x: int, y_inicio: int,
                         cor: tuple = BRANCO, fonte: pygame.font.Font = None,
                         espacamento: int = 28, centralizar: bool = False):
        f = fonte or self.fonte_media
        for i, linha in enumerate(linhas):
            self.texto(linha, x, y_inicio + i * espacamento,
                       cor, f, centralizar=centralizar)

    # ── Formas ────────────────────────────────────────
    def caixa(self, x: int, y: int, w: int, h: int,
              cor: tuple, borda: tuple = BRANCO,
              raio: int = 10, espessura_borda: int = 3,
              alpha: int = 210):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*cor, alpha), (0, 0, w, h), border_radius=raio)
        self.screen.blit(s, (x, y))
        if espessura_borda > 0:
            pygame.draw.rect(self.screen, borda, (x, y, w, h),
                             espessura_borda, border_radius=raio)

    def caixa_gradiente(self, x: int, y: int, w: int, h: int,
                        cor_topo: tuple, cor_base: tuple, raio: int = 10):
        """Caixa com gradiente vertical."""
        for i in range(h):
            t = i / h
            r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * t)
            g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * t)
            b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (x, y + i), (x + w, y + i))
        pygame.draw.rect(self.screen, CINZA_ESC, (x, y, w, h), 2, border_radius=raio)

    def barra_progresso(self, x: int, y: int, w: int, h: int,
                        valor: float, cor_preench: tuple = VERDE_ESC,
                        cor_fundo: tuple = CINZA_ESC):
        pygame.draw.rect(self.screen, cor_fundo,    (x, y, w, h), border_radius=h // 2)
        largura_preench = int(w * max(0.0, min(1.0, valor)))
        if largura_preench > 0:
            pygame.draw.rect(self.screen, cor_preench,
                             (x, y, largura_preench, h), border_radius=h // 2)
        pygame.draw.rect(self.screen, BRANCO, (x, y, w, h), 2, border_radius=h // 2)

    # ── Utilitário de texto ────────────────────────────
    def wrap_text(self, texto: str, fonte: pygame.font.Font, max_w: int) -> list:
        palavras = texto.split()
        linhas, linha = [], ""
        for p in palavras:
            teste = linha + (" " if linha else "") + p
            if fonte.size(teste)[0] <= max_w:
                linha = teste
            else:
                if linha:
                    linhas.append(linha)
                linha = p
        if linha:
            linhas.append(linha)
        return linhas


# ─────────────────────────────────────────────────────────
#  CLASSE: Estadio  —  cenário de fundo com animação
# ─────────────────────────────────────────────────────────
class Estadio:
    def __init__(self, cor_grama: tuple, cor_arquibancada: tuple,
                 cor_luz: tuple = AMARELO):
        self.cor_grama        = cor_grama
        self.cor_arquibancada = cor_arquibancada
        self.cor_luz          = cor_luz
        self._tick            = 0

    def draw(self, surface: pygame.Surface):
        self._tick += 1
        W, H = surface.get_size()

        # ── Céu noturno ──────────────────────────────
        surface.fill((8, 8, 22))
        for i in range(50):
            random.seed(i * 7 + 3)
            sx = random.randint(0, W)
            sy = random.randint(0, H // 3)
            brilho = int(160 + 80 * math.sin(self._tick * 0.04 + i))
            pygame.draw.rect(surface, (brilho, brilho, brilho), (sx, sy, 2, 2))

        # ── Arquibancada com gradiente ────────────────
        arq_y = H // 5
        arq_h = H // 3
        for i in range(arq_h):
            t  = i / arq_h
            r  = int(self.cor_arquibancada[0] * (1 - t * 0.4))
            g  = int(self.cor_arquibancada[1] * (1 - t * 0.4))
            b  = int(self.cor_arquibancada[2] * (1 - t * 0.4))
            pygame.draw.line(surface, (r, g, b), (0, arq_y + i), (W, arq_y + i))

        # Torcedores
        for col in range(0, W, 20):
            for row in range(arq_y + 4, arq_y + arq_h - 8, 16):
                random.seed(col * 100 + row)
                c = random.choice([VERMELHO, AMARELO, AZUL, BRANCO, LARANJA, ROXO])
                pygame.draw.ellipse(surface, c, (col, row, 11, 9))

        # ── Grama com listras ─────────────────────────
        grama_top = int(H * 0.48)
        listras   = 10
        for i in range(listras):
            t      = i / listras
            fator  = 0.85 + 0.15 * (i % 2)
            cor_g  = tuple(max(0, min(255, int(c * fator))) for c in self.cor_grama)
            rect_y = grama_top + i * (H - grama_top) // listras
            rect_h = (H - grama_top) // listras + 2
            pygame.draw.rect(surface, cor_g, (0, rect_y, W, rect_h))

        # ── Linhas do campo ───────────────────────────
        meio_x = W // 2
        campo_y2 = H - 10

        pygame.draw.rect(surface, BRANCO, (40, grama_top, W - 80, campo_y2 - grama_top), 2)
        pygame.draw.line(surface, BRANCO, (meio_x, grama_top), (meio_x, campo_y2), 2)
        centro_y = grama_top + (campo_y2 - grama_top) // 2
        pygame.draw.ellipse(surface, BRANCO,
                            (meio_x - 65, centro_y - 55, 130, 110), 2)
        pygame.draw.circle(surface, BRANCO, (meio_x, centro_y), 5)

        # ── Traves ───────────────────────────────────
        for tx in [40, W - 40]:
            tl = 30
            pygame.draw.rect(surface, (220, 220, 220),
                             (tx - tl, grama_top + 8, tl * 2, 4))
            pygame.draw.rect(surface, (220, 220, 220),
                             (tx - tl, grama_top + 8, 3, 60))
            pygame.draw.rect(surface, (220, 220, 220),
                             (tx + tl - 3, grama_top + 8, 3, 60))

        # ── Holofotes ────────────────────────────────
        for lx in [90, W - 90]:
            self._draw_holofote(surface, lx, arq_y - 15, W, H)

    def _draw_holofote(self, surface, x, y, W, H):
        pygame.draw.rect(surface, CINZA_ESC, (x - 5, y - 28, 10, 28))
        pygame.draw.rect(surface, CINZA,     (x - 14, y - 34, 28, 10))
        pts = [(x, y), (x - 50, y + 130), (x + 50, y + 130)]
        luz = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(luz, (255, 255, 180, 22), pts)
        surface.blit(luz, (0, 0))
