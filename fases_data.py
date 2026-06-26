from constants import asset_path

from constants import *

FASES_DATA = [
    {
        "jogador":         "Kuki",
        "clube":           "Náutico",
        "imagem":          asset_path("kuki.png"),
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
            {
                "pergunta": "Qual destes é um time de futebol de Pernambuco?",
                "opcoes":   ["Flamengo", "Corinthians", "Náutico", "Grêmio"],
                "resposta": 2
            },
            {
                "pergunta": "Quantos times jogam ao mesmo tempo em uma partida de futebol?",
                "opcoes":   ["1", "2", "3", "4"],
                "resposta": 1
            },
            {
                "pergunta": "O que o goleiro usa nas mãos para segurar melhor a bola?",
                "opcoes":   ["Luvas", "Faixas", "Protetor", "Nada"],
                "resposta": 0
            },
            {
                "pergunta": "Como se chama o local onde o goleiro defende os gols?",
                "opcoes":   ["Área central", "Gol / Trave", "Linha lateral", "Escanteio"],
                "resposta": 1
            },
            {
                "pergunta": "Quantas traves (postes) tem um gol de futebol?",
                "opcoes":   ["2", "3", "4", "1"],
                "resposta": 1
            },
            {
                "pergunta": "O que acontece quando a bola entra no gol?",
                "opcoes":   ["Falta", "Escanteio", "Gol é marcado", "Lateral"],
                "resposta": 2
            },
            {
                "pergunta": "Qual é a cor da camisa do Náutico?",
                "opcoes":   ["Vermelho e preto", "Amarelo e verde", "Branco e Vermelho", "Verde"],
                "resposta": 2
            },
            {
                "pergunta": "Quantos tempos tem uma partida de futebol?",
                "opcoes":   ["1", "2", "3", "4"],
                "resposta": 1
            },
        ]
    },

    {
        "jogador":         "Caça Rato",
        "clube":           "Santa Cruz",
        "imagem":          asset_path("cacaRato.png"),
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
            {
                "pergunta": "O que é um 'escanteio'?",
                "opcoes":   ["Falta dentro da área", "Cobrança da bandeirinha", "Gol anulado", "Substituição de jogador"],
                "resposta": 1
            },
            {
                "pergunta": "Quantas substituições eram permitidas por time antes da regra moderna?",
                "opcoes":   ["2", "3", "4", "5"],
                "resposta": 1
            },
            {
                "pergunta": "O que significa 'impedimento' no futebol?",
                "opcoes":   ["Jogador expulso", "Atacante à frente do último defensor", "Falta violenta", "Bola fora de campo"],
                "resposta": 1
            },
            {
                "pergunta": "Como se chama o chute feito com a parte de trás do pé?",
                "opcoes":   ["Bicicleta", "Trivela", "Calcanhar", "Voleio"],
                "resposta": 2
            },
            {
                "pergunta": "Qual cartão o árbitro mostra para advertir um jogador?",
                "opcoes":   ["Cartão verde", "Cartão amarelo", "Cartão azul", "Cartão branco"],
                "resposta": 1
            },
            {
                "pergunta": "Qual é o apelido do Santa Cruz Futebol Clube?",
                "opcoes":   ["Timbu", "Leão", "Cobra Coral", "Tricolor"],
                "resposta": 2
            },
            {
                "pergunta": "O que é um 'gol contra'?",
                "opcoes":   ["Gol anulado pelo VAR", "Gol que o próprio jogador marca no seu gol", "Gol de pênalti", "Gol de falta direta"],
                "resposta": 1
            },
            {
                "pergunta": "Quantos metros tem a largura padrão de um gol de futebol?",
                "opcoes":   ["5,5 m", "6,4 m", "7,3 m", "8 m"],
                "resposta": 2
            },
        ]
    },

    {
        "jogador":         "Magrão",
        "clube":           "Sport",
        "imagem":          asset_path("magrao.png"),
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
            {
                "pergunta": "Em que ano foi criada a Copa do Mundo FIFA?",
                "opcoes":   ["1920", "1930", "1950", "1970"],
                "resposta": 1
            },
            {
                "pergunta": "Qual é o apelido do Sport Club do Recife?",
                "opcoes":   ["Timbu", "Cobra Coral", "Náutico", "Leão da Ilha"],
                "resposta": 3
            },
            {
                "pergunta": "Quantos jogadores participam de uma cobrança de falta na barreira mínima exigida?",
                "opcoes":   ["2", "3", "Não há mínimo obrigatório", "5"],
                "resposta": 2
            },
            {
                "pergunta": "Qual é a federação que governa o futebol mundial?",
                "opcoes":   ["UEFA", "CONMEBOL", "FIFA", "CBF"],
                "resposta": 2
            },
            {
                "pergunta": "Qual time venceu o primeiro Campeonato Brasileiro em 1987?",
                "opcoes":   ["Santos", "Sport Club do Recife", "Flamengo", "Palmeiras"],
                "resposta": 1
            },
            {
                "pergunta": "Qual é a distância mínima da barreira em uma cobrança de falta?",
                "opcoes":   ["7,32 m", "9,15 m", "11 m", "16,5 m"],
                "resposta": 1
            },
            {
                "pergunta": "Qual continente possui mais federações nacionais de futebol?",
                "opcoes":   ["Europa", "Ásia", "África", "América do Sul"],
                "resposta": 2
            },
        ]
    },

    {
        "jogador":         "Neymar",
        "clube":           "Santos",
        "imagem":          asset_path("neymar.png"),
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
                "pergunta": "Quantas substituições são permitidas por time na maioria das competições modernas?",
                "opcoes":   ["3", "4", "5", "6"],
                "resposta": 2
            },
            {
                "pergunta": "Qual jogador é conhecido como 'O Fenômeno'?",
                "opcoes":   ["Ronaldinho", "Ronaldo Nazário", "Rivaldo", "Romário"],
                "resposta": 1
            },
            {
                "pergunta": "Para qual clube europeu Neymar foi vendido pelo Barcelona em 2017?",
                "opcoes":   ["Real Madrid", "Manchester City", "Paris Saint-Germain", "Juventus"],
                "resposta": 2
            },
            {
                "pergunta": "Qual é o nome do movimento em que o jogador rola a bola por cima do adversário?",
                "opcoes":   ["Elástico", "Trivela", "Chapéu", "Pedalada"],
                "resposta": 2
            },
            {
                "pergunta": "Qual prêmio individual é dado ao melhor jogador do mundo no futebol?",
                "opcoes":   ["Chuteira de Ouro", "Bola de Ouro", "Luva de Ouro", "Capacete de Ouro"],
                "resposta": 1
            },
            {
                "pergunta": "Em que ano Neymar ganhou a Copa das Confederações com o Brasil?",
                "opcoes":   ["2009", "2011", "2013", "2015"],
                "resposta": 2
            },
            {
                "pergunta": "Qual é o nome do estádio do Santos FC?",
                "opcoes":   ["Maracanã", "Vila Belmiro", "Morumbi", "Arena Corinthians"],
                "resposta": 1
            },
            {
                "pergunta": "O que é a 'caneta' no futebol?",
                "opcoes":   ["Gol bonito", "Passar a bola pelas pernas", "Passe longo com efeito", "Bicicleta invertida"],
                "resposta": 1
            },
            {
                "pergunta": "Qual brasileiro ganhou 3 vezes consecutivas o prêmio de melhor do mundo (FIFA)?",
                "opcoes":   ["Pelé", "Ronaldo Nazário", "Ronaldinho", "Romário"],
                "resposta": 1
            },
            {
                "pergunta": "Qual é a posição em que Neymar atua predominantemente?",
                "opcoes":   ["Goleiro", "Zagueiro", "Atacante", "Volante"],
                "resposta": 2
            },
        ]
    },

    {
        "jogador":         "Pelé",
        "clube":           "Seleção Brasileira",
        "imagem":          asset_path("pele.png"),
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
            {
                "pergunta": "Em qual clube Pelé jogou a maior parte de sua carreira?",
                "opcoes":   ["Flamengo", "Santos FC", "São Paulo FC", "Corinthians"],
                "resposta": 1
            },
            {
                "pergunta": "Qual Copa do Mundo foi a única que o Brasil sediou e perdeu a final?",
                "opcoes":   ["1938", "1950", "1966", "1974"],
                "resposta": 1
            },
            {
                "pergunta": "Quantos gols oficiais Pelé marcou em sua carreira profissional (número reconhecido pelo Guinness)?",
                "opcoes":   ["643", "767", "1000", "1281"],
                "resposta": 2
            },
            {
                "pergunta": "Qual é o verdadeiro nome de Pelé?",
                "opcoes":   ["Edson Arantes", "Arthur Antunes", "Ronaldo de Assis", "Pedro Leonardo"],
                "resposta": 0
            },
            {
                "pergunta": "Em qual Copa do Mundo o Brasil teve a histórica derrota de 7x1 para a Alemanha?",
                "opcoes":   ["2006", "2010", "2014", "2018"],
                "resposta": 2
            },
            {
                "pergunta": "Qual a posição em que Pelé atuava?",
                "opcoes":   ["Goleiro", "Zagueiro", "Meia-atacante", "Lateral direito"],
                "resposta": 2
            },
            {
                "pergunta": "Em que cidade brasileira Pelé nasceu?",
                "opcoes":   ["São Paulo", "Rio de Janeiro", "Três Corações", "Santos"],
                "resposta": 2
            },
            {
                "pergunta": "Qual foi o último clube que Pelé jogou profissionalmente?",
                "opcoes":   ["Santos", "Cosmos (EUA)", "Flamengo", "Seleção Brasileira"],
                "resposta": 1
            },
        ]
    },
]
