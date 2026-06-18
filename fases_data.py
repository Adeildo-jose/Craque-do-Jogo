"""
fases_data.py – Dados de cada fase: jogador, clube, cores e perguntas.
Ordem: Kuki → Caça Rato → Magrão → Neymar → Pelé
"""

from constants import *

FASES_DATA = [
    # ── FASE 1: KUKI ─────────────────────────────────────
    {
        "jogador":         "Kuki",
        "clube":           "Náutico",
        "imagem":          "assets/kuki.png",
        "cor_clube":       (0, 80, 180),
        "cor2":            BRANCO,
        "cor_fundo":       (0, 10, 60),
        "cor_arquibancada":(20, 60, 160),
        "cor_destaque":    (100, 160, 255),
        "descricao":       "Ídolo do Timbu! Goleiro lendário do Náutico.",
        "perguntas": [
            {
                "pergunta": "Quantos jogadores de cada time ficam em campo durante uma partida?",
                "opcoes":   ["9", "11", "13", "10"],
                "resposta": 1
            },
            {
                "pergunta": "Qual é o tempo regulamentar de uma partida de futebol?",
                "opcoes":   ["80 minutos", "100 minutos", "90 minutos", "120 minutos"],
                "resposta": 2
            },
            {
                "pergunta": "Em que posição joga o goleiro?",
                "opcoes":   ["Ataque", "Meio-campo", "Defesa da baliza", "Lateral"],
                "resposta": 2
            },
            {
                "pergunta": "O 'drible da vaca' é um movimento clássico de qual esporte?",
                "opcoes":   ["Basquete", "Futebol", "Handebol", "Vôlei"],
                "resposta": 1
            },
        ]
    },

    # ── FASE 2: CAÇA RATO ────────────────────────────────
    {
        "jogador":         "Caça Rato",
        "clube":           "Santa Cruz",
        "imagem":          "assets/cacaRato.png",
        "cor_clube":       (220, 20, 60),
        "cor2":            BRANCO,
        "cor_fundo":       (60, 0, 0),
        "cor_arquibancada":(180, 30, 30),
        "cor_destaque":    (255, 100, 100),
        "descricao":       "A Cobra Coral! Ídolo eterno da Cobra Coral de Pernambuco.",
        "perguntas": [
            {
                "pergunta": "O que é um 'hat-trick'?",
                "opcoes":   ["Três gols do mesmo jogador", "Dois gols seguidos", "Um gol de falta", "Vitória por 3 a 0"],
                "resposta": 0
            },
            {
                "pergunta": "Como se chama a linha que divide o campo ao meio?",
                "opcoes":   ["Linha de fundo", "Linha lateral", "Linha de meio-campo", "Linha de impedimento"],
                "resposta": 2
            },
            {
                "pergunta": "O que acontece quando a bola sai pela linha de fundo tocada por um atacante?",
                "opcoes":   ["Escanteio", "Tiro de meta", "Lateral", "Falta"],
                "resposta": 1
            },
            {
                "pergunta": "Quantos pênaltis cada time cobra numa disputa padrão?",
                "opcoes":   ["3", "4", "5", "6"],
                "resposta": 2
            },
        ]
    },

    # ── FASE 3: MAGRÃO ───────────────────────────────────
    {
        "jogador":         "Magrão",
        "clube":           "Sport",
        "imagem":          "assets/magrao.png",
        "cor_clube":       (200, 0, 0),
        "cor2":            PRETO,
        "cor_fundo":       (20, 0, 0),
        "cor_arquibancada":(160, 20, 20),
        "cor_destaque":    (255, 80, 80),
        "descricao":       "O Leão do Sport! Goleiro histórico do Leão da Ilha.",
        "perguntas": [
            {
                "pergunta": "Qual país venceu mais Copas do Mundo de futebol?",
                "opcoes":   ["Argentina", "Alemanha", "Brasil", "Itália"],
                "resposta": 2
            },
            {
                "pergunta": "Qual troféu é entregue ao campeão do mundo?",
                "opcoes":   ["Taça Libertadores", "FIFA World Cup Trophy", "Bola de Ouro", "Troféu UEFA"],
                "resposta": 1
            },
            {
                "pergunta": "Qual desses torneios é disputado por clubes sul-americanos?",
                "opcoes":   ["UEFA Champions League", "Copa Libertadores", "FA Cup", "DFB-Pokal"],
                "resposta": 1
            },
            {
                "pergunta": "O que significa 'VAR' no futebol moderno?",
                "opcoes":   ["Velocidade de Ataque Rápido", "Video Assistant Referee", "Verificação em Rede", "Árbitro Virtual"],
                "resposta": 1
            },
        ]
    },

    # ── FASE 4: NEYMAR ───────────────────────────────────
    {
        "jogador":         "Neymar",
        "clube":           "Santos",
        "imagem":          "assets/neymar.png",
        "cor_clube":       (240, 200, 0),
        "cor2":            PRETO,
        "cor_fundo":       (30, 25, 0),
        "cor_arquibancada":(160, 140, 0),
        "cor_destaque":    (255, 230, 50),
        "descricao":       "O Menino Ney! Craque que encantou o mundo pelo Santos.",
        "perguntas": [
            {
                "pergunta": "Por qual clube Neymar se tornou famoso no Brasil?",
                "opcoes":   ["Flamengo", "Corinthians", "Santos", "Grêmio"],
                "resposta": 2
            },
            {
                "pergunta": "O que é um 'gol olímpico'?",
                "opcoes":   ["Gol marcado em Olimpíadas", "Gol direto de escanteio", "Gol de bicicleta", "Gol na prorrogação"],
                "resposta": 1
            },
            {
                "pergunta": "Quantas substituições são permitidas por time na maioria das competições?",
                "opcoes":   ["3", "4", "5", "6"],
                "resposta": 2
            },
            {
                "pergunta": "Qual jogador é conhecido como 'O Fenômeno'?",
                "opcoes":   ["Ronaldinho", "Ronaldo Nazário", "Rivaldo", "Romário"],
                "resposta": 1
            },
        ]
    },

    # ── FASE 5: PELÉ ─────────────────────────────────────
    {
        "jogador":         "Pelé",
        "clube":           "Seleção Brasileira",
        "imagem":          "assets/pele.png",
        "cor_clube":       (0, 160, 60),
        "cor2":            AMARELO,
        "cor_fundo":       (0, 30, 0),
        "cor_arquibancada":(0, 110, 40),
        "cor_destaque":    DOURADO,
        "descricao":       "O Rei do Futebol! Tricampeão mundial e eterno número 10.",
        "perguntas": [
            {
                "pergunta": "Quantas Copas do Mundo Pelé conquistou com o Brasil?",
                "opcoes":   ["1", "2", "3", "4"],
                "resposta": 2
            },
            {
                "pergunta": "Em qual Copa do Mundo Pelé marcou seu primeiro gol, aos 17 anos?",
                "opcoes":   ["1950 Brasil", "1954 Suíça", "1958 Suécia", "1962 Chile"],
                "resposta": 2
            },
            {
                "pergunta": "Quantas Copas do Mundo o Brasil venceu até hoje?",
                "opcoes":   ["4", "5", "6", "3"],
                "resposta": 1
            },
            {
                "pergunta": "Como se chama o árbitro que fica na linha lateral?",
                "opcoes":   ["Árbitro central", "Auxiliar / bandeirinha", "VAR", "Supervisor"],
                "resposta": 1
            },
        ]
    },
]
