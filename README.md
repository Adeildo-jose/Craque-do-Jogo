# Craque-do-Jogo

<h1 align="center">⚽ Quiz do Craque</h1>

<p align="center">
  <img src="assets/bola_menu.png" alt="Bola do Quiz do Craque" width="120"/>
</p>

<p align="center">
  Um jogo de quiz interativo sobre futebol feito com Python e Pygame.<br/>
  Prove que você conhece os maiores craques do futebol brasileiro!
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Pygame-2.x-green?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow" />
  <img src="https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" />
</p>

-----

## 🎮 Sobre o Jogo

**Quiz do Craque** é um jogo de perguntas e respostas temático de futebol, desenvolvido em Python com a biblioteca Pygame. O jogador avança por 5 fases, cada uma dedicada a um craque lendário do futebol, respondendo perguntas sobre regras, história e curiosidades do esporte.

A ambientação é totalmente imersiva: um estádio noturno animado com torcida, holofotes, grama listrada e placar, tudo desenhado em tempo real com Pygame.

-----

## 📸 Screenshots

| | |
|:-:|:-:|
| ![Menu](https://raw.githubusercontent.com/Adeildo-jose/Craque-do-Jogo/main/assets/screenshots/Menu.png) | ![Tela de pergunta](https://raw.githubusercontent.com/Adeildo-jose/Craque-do-Jogo/main/assets/screenshots/Tela%20de%20pergunta.png) |
| ![Cartão Amarelo](https://raw.githubusercontent.com/Adeildo-jose/Craque-do-Jogo/main/assets/screenshots/Cart%C3%A3o%20amarelo.png) | ![Cartão Vermelho](https://raw.githubusercontent.com/Adeildo-jose/Craque-do-Jogo/main/assets/screenshots/Cart%C3%A3o%20vermelho.png) |
| ![Ranking](https://raw.githubusercontent.com/Adeildo-jose/Craque-do-Jogo/main/assets/screenshots/Ranking.png) | |

-----

## 🏟️ Fases

Cada fase apresenta um jogador icônico e 4 perguntas temáticas. Para ser aprovado e avançar, o jogador precisa acertar ao menos **3 das 4 perguntas**. Erros são punidos com cartões — ao levar o segundo cartão (vermelho), a fase é reiniciada.

|Fase|Craque   |Clube             |Dificuldade  |
|----|---------|------------------|-------------|
|1   |Kuki     |Náutico           |Introdutória |
|2   |Caça Rato|Santa Cruz        |Fácil        |
|3   |Magrão   |Sport             |Intermediária|
|4   |Neymar   |Santos            |Intermediária|
|5   |Pelé     |Seleção Brasileira|Avançada     |

-----

## 🃏 Sistema de Cartões

O jogo usa um sistema de cartões inspirado no futebol real:

- **Sem erros** → os dois cartões ficam **cinza** (limpos)
- **1º erro na fase** → cartão **amarelo** (aviso)
- **2º erro na fase** → cartão **vermelho** → fase reiniciada automaticamente
- **Acertar uma pergunta** → o cartão amarelo é removido, voltando para limpo

O sistema de cartões reseta ao começar (ou recomeçar) cada fase.

-----

## ⏱️ Timer e Pontuação por Tempo

Cada pergunta tem um tempo limite de **15 segundos**. A pontuação obtida ao acertar diminui conforme o tempo passa — quanto mais rápido o jogador responder, mais pontos ele ganha.

| Fase | Pontuação máxima | Desconto | Pontuação mínima |
|------|-----------------|----------|-----------------|
| 1    | 10 pts          | -1 pt/s  | 1 pt            |
| 2    | 20 pts          | -1 pt/s  | 1 pt            |
| 3    | 30 pts          | -1 pt/s  | 1 pt            |
| 4    | 40 pts          | -1 pt/s  | 1 pt            |
| 5    | 50 pts          | -1 pt/s  | 1 pt            |

> A barra do timer muda de cor (verde → amarelo → vermelho) e exibe em tempo real quantos pontos você vai ganhar se responder naquele instante.

-----

## 🏆 Ranking

Ao final de cada partida, a pontuação é registrada no ranking local. A tela de ranking exibe os **melhores jogadores** da sessão, incentivando a competição por tempo de resposta e precisão.

-----

## 🕹️ Como Jogar

### Pré-requisitos

- Python **3.11** ou superior
- Pygame **2.x**

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/quiz-do-craque.git
cd quiz-do-craque

# Instale as dependências
pip install pygame
```

### Executando o jogo

```bash
python main.py
```

### Controles

|Ação                   |Controle                       |
|-----------------------|-------------------------------|
|Navegar no menu        |Mouse                          |
|Iniciar / continuar    |`Espaço` ou clique             |
|Escolher resposta      |Clique na opção (A / B / C / D)|
|Pular animação de texto|Clique ou qualquer tecla       |
|Voltar ao menu         |`ESC` ou botão **Menu**        |
|Recomeçar (Game Over)  |`R`                            |

-----

## 📁 Estrutura do Projeto

```
quiz-do-craque/
│
├── main.py          # Ponto de entrada — inicializa o Pygame e executa o jogo
├── game.py          # Classe principal Jogo: máquina de estados e lógica geral
├── entities.py      # Classes de dados: Pergunta, Fase, TextoAnimado, Particula
├── renderer.py      # Renderização: UI (texto, caixas, barras) e Estadio (cenário)
├── fases_data.py    # Conteúdo das fases: jogadores, clubes, cores e perguntas
├── constants.py     # Paleta de cores, dimensões da janela e estados do jogo
│
└── assets/
    ├── bola_menu.png    # Imagem da bola animada do menu
    ├── kuki.png         # Imagem do jogador — Fase 1
    ├── cacaRato.png     # Imagem do jogador — Fase 2
    ├── magrao.png       # Imagem do jogador — Fase 3
    ├── neymar.png       # Imagem do jogador — Fase 4
    ├── pele.png         # Imagem do jogador — Fase 5
    └── screenshots/     # Capturas de tela do jogo
```

-----

## 🧠 Arquitetura

O jogo é organizado como uma **máquina de estados finitos**. O estado atual determina o que é desenhado e como os eventos são tratados.

```
MENU → SELECAO_FASES → INTRO_FASE → PERGUNTA ⇄ FEEDBACK → RESULTADO
                                                               │
                                              ┌────────────────┤
                                              ↓                ↓
                                           VITORIA       SELECAO_FASES
```

### Estados

|Estado         |Descrição                                               |
|---------------|--------------------------------------------------------|
|`MENU`         |Tela inicial com estádio animado e botão Jogar          |
|`SELECAO_FASES`|Grade com os cards de cada fase (bloqueadas/disponíveis)|
|`INTRO_FASE`   |Apresentação do craque com texto animado                |
|`PERGUNTA`     |Exibição da pergunta e 4 alternativas                   |
|`FEEDBACK`     |Retorno visual após resposta (acerto/erro + cartão)     |
|`RESULTADO`    |Placar da fase e botão para continuar                   |
|`VITORIA`      |Tela de parabéns ao completar todas as fases            |
|`GAME_OVER`    |Tela de encerramento (reservada para expansão futura)   |

### Principais classes

**`Jogo`** (`game.py`) — Controla o loop principal, os eventos, a lógica de pontuação, o sistema de cartões e o despacho de renderização para cada estado.

**`UI`** (`renderer.py`) — Biblioteca de desenho de alto nível: texto com suporte a emojis, caixas com alpha, gradientes, barras de progresso e cartões de HUD.

**`Estadio`** (`renderer.py`) — Renderiza o cenário de fundo a cada frame: céu estrelado, arquibancada com torcedores, grama listrada, linhas do campo, traves e holofotes animados.

**`Fase`** (`entities.py`) — Encapsula os dados e o estado de uma fase: perguntas, acertos, erros e carregamento da imagem do jogador.

**`Pergunta`** (`entities.py`) — Armazena enunciado, opções e índice da resposta correta.

**`TextoAnimado`** (`entities.py`) — Revela texto caractere a caractere com velocidade configurável (efeito máquina de escrever).

**`Particula`** (`entities.py`) — Partícula física com gravidade, usada nos efeitos de acerto (verde) e erro (amarelo/vermelho).

-----

## ✨ Funcionalidades

- 🏟️ Cenário de estádio noturno animado em tempo real
- ⚽ Bola de futebol com rotação e flutuação no menu
- 🃏 Sistema de cartões amarelo e vermelho por fase
- 💥 Efeito de partículas em acertos e erros
- 🔒 Fases bloqueadas — desbloqueiam ao progredir
- ⭐ Registro de fases aprovadas na sessão
- 🖋️ Animação de texto tipo máquina de escrever na intro
- 🏆 Tela de vitória com confete animado
- ⏱️ Timer de 15 segundos por pergunta com barra visual colorida
- ⚡ Pontuação dinâmica — responder rápido vale mais pontos
- 📊 Ranking de melhores pontuações

-----

## 👨‍💻 Criadores

<table>
  <tr>
    <td align="center">
      <b>Adeildo José de Araújo Fragoso</b><br/>
      <a href="https://github.com/Adeildo-Jose">
        <img src="https://img.shields.io/badge/GitHub-Adeildo--Jose-181717?logo=github&logoColor=white" />
      </a>
    </td>
    <td align="center">
      <b>Davi Domingues Guaraná</b><br/>
      <a href="https://github.com/DaviDGuarana">
        <img src="https://img.shields.io/badge/GitHub-DaviDGuarana-181717?logo=github&logoColor=white" />
      </a>
    </td>
  </tr>
</table>

-----

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais. Sinta-se livre para estudar, modificar e se inspirar no código.