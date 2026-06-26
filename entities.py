from __future__ import annotations

import pygame
import random
import os
from constants import *



class Pergunta:
    def __init__(self, texto: str, opcoes: list, resposta_idx: int):
        self.texto       = texto
        self.opcoes      = opcoes
        self.resposta_idx = resposta_idx

    def checar(self, idx: int) -> bool:
        return idx == self.resposta_idx


class Fase:

    def __init__(self, data: dict):
        self.jogador          = data["jogador"]
        self.clube            = data["clube"]
        self.cor_clube        = data["cor_clube"]
        self.cor2             = data["cor2"]
        self.cor_destaque     = data.get("cor_destaque", DOURADO)
        self.cor_arquibancada = data["cor_arquibancada"]
        self.descricao        = data.get("descricao", "")
        self.imagem_path      = data.get("imagem", None)
        self._imagem_original = None
        self._carregar_imagem()

        banco = [
            Pergunta(p["pergunta"], p["opcoes"], p["resposta"])
            for p in data["perguntas"]
        ]
        qtd = min(4, len(banco))
        self.perguntas     = random.sample(banco, qtd)
        self.pergunta_atual = 0
        self.acertos        = 0
        self.erros          = 0

    def _carregar_imagem(self):
        if self.imagem_path and os.path.exists(self.imagem_path):
            try:
                img = pygame.image.load(self.imagem_path).convert_alpha()
                self._imagem_original = img
            except Exception as e:
                print(f"[AVISO] Não carregou imagem {self.imagem_path}: {e}")

    def get_imagem(self, altura_alvo: int = 220) -> pygame.Surface | None:
        if self._imagem_original is None:
            return None
        ow, oh = self._imagem_original.get_size()
        fator   = altura_alvo / oh
        nw, nh  = int(ow * fator), int(oh * fator)
        return pygame.transform.scale(self._imagem_original, (nw, nh))

    def proxima_pergunta(self) -> Pergunta | None:
        if self.pergunta_atual < len(self.perguntas):
            return self.perguntas[self.pergunta_atual]
        return None

    def responder(self, idx: int) -> bool:
        p = self.proxima_pergunta()
        if p is None:
            return False
        correto = p.checar(idx)
        if correto:
            self.acertos += 1
        else:
            self.erros += 1
        self.pergunta_atual += 1
        return correto

    def concluida(self) -> bool:
        return self.pergunta_atual >= len(self.perguntas)

    def aprovado(self) -> bool:
        return self.acertos >= 3


class TextoAnimado:
    def __init__(self, texto: str, velocidade: int = 2):
        self.texto_completo  = texto
        self.chars_mostrados = 0
        self.velocidade      = velocidade
        self._counter        = 0

    def update(self):
        self._counter += 1
        if self._counter % self.velocidade == 0:
            if self.chars_mostrados < len(self.texto_completo):
                self.chars_mostrados += 1

    def get(self) -> str:
        return self.texto_completo[:self.chars_mostrados]

    def concluido(self) -> bool:
        return self.chars_mostrados >= len(self.texto_completo)

    def pular(self):
        self.chars_mostrados = len(self.texto_completo)


class Particula:
    def __init__(self, x: int, y: int, cor: tuple, acerto: bool = True):
        self.x        = x
        self.y        = y
        self.cor      = cor
        self.vx       = random.uniform(-4, 4)
        self.vy       = random.uniform(-7, -2) if acerto else random.uniform(-2, 3)
        self.vida     = 70
        self.max_vida = 70
        self.raio     = random.randint(3, 9)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.22
        self.vida -= 1

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * self.vida / self.max_vida)
        s = pygame.Surface((self.raio * 2, self.raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.cor, alpha), (self.raio, self.raio), self.raio)
        surface.blit(s, (int(self.x - self.raio), int(self.y - self.raio)))

    def morta(self) -> bool:
        return self.vida <= 0
