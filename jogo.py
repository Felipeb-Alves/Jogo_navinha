import random
import sys
import pygame

# Inicialização do Pygame
pygame.init()
pygame.font.init()

# Configurações da Tela
LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Navinha - Dificuldade Progressiva")

# Cores
BRANCO = (255, 255, 255)
PRETO = (10, 10, 30)
AZUL = (0, 150, 255)
VERMELHO = (255, 60, 60)
AMARELO = (255, 255, 0)
VERDE = (50, 205, 50)

# Relógio para controle de FPS
relogio = pygame.time.Clock()
FPS = 60

# Fonte de texto
FONTE = pygame.font.SysFont("arial", 22)
FONTE_FIM = pygame.font.SysFont("arial", 48, bold=True)


class Jogador(pygame.sprite.Sprite):

  def __init__(self):
    super().__init__()
    self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.polygon(self.image, AZUL, [(20, 0), (0, 40), (40, 40)])
    pygame.draw.polygon(self.image, AMARELO, [(20, 10), (10, 35), (30, 35)])

    self.rect = self.image.get_rect()
    self.rect.centerx = LARGURA // 2
    self.rect.bottom = ALTURA - 20
    self.velocidade = 6
    self.vidas = 3

  def update(self):
    teclas = pygame.key.get_pressed()
    if (
        teclas[pygame.K_LEFT] or teclas[pygame.K_a]
    ) and self.rect.left > 0:
      self.rect.x -= self.velocidade
    if (
        teclas[pygame.K_RIGHT] or teclas[pygame.K_d]
    ) and self.rect.right < LARGURA:
      self.rect.x += self.velocidade
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
      if self.rect.top > 0:
        self.rect.y -= self.velocidade
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
      if self.rect.bottom < ALTURA:
        self.rect.y += self.velocidade


class Tiro(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    self.image = pygame.Surface((6, 14))
    self.image.fill(AMARELO)
    self.rect = self.image.get_rect()
    self.rect.centerx = x
    self.rect.bottom = y
    self.velocidade = 10

  def update(self):
    self.rect.y -= self.velocidade
    if self.rect.bottom < 0:
      self.kill()


class Inimigo(pygame.sprite.Sprite):

  def __init__(self, velocidade_extra=0):
    super().__init__()
    self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
    pygame.draw.rect(self.image, VERMELHO, (5, 5, 25, 20), border_radius=4)
    pygame.draw.rect(self.image, BRANCO, (8, 10, 6, 6))
    pygame.draw.rect(self.image, BRANCO, (21, 10, 6, 6))

    self.rect = self.image.get_rect()
    self.rect.x = random.randint(0, LARGURA - self.rect.width)
    self.rect.y = random.randint(-100, -40)
    # Velocidade base + um bônus que aumenta com o tempo/pontos
    self.velocidade = random.randint(2, 4) + velocidade_extra

  def update(self):
    self.rect.y += self.velocidade
    # Se passar da tela, o inimigo se destrói sozinho para não acumular
    if self.rect.top > ALTURA:
      self.kill()


# Grupos de Sprites
todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()

# Instanciando o Jogador
jogador = Jogador()
todos_sprites.add(jogador)

# Variáveis do Jogo e Sistema de Spawn (Tempo)
pontos = 0
tempo_sobrevivencia = 0
rodando = True
game_over = False

# Evento customizado para criar inimigos periodicamente no Pygame
ADICIONAR_INIMIGO = pygame.USEREVENT + 1
TEMPO_SPAWN_INICIAL = 1500  # Começa gerando um inimigo a cada 1.5 segundo (1500ms)
pygame.time.set_timer(ADICIONAR_INIMIGO, TEMPO_SPAWN_INICIAL)

# Loop Principal do Jogo
while rodando:
  relogio.tick(FPS)

  for evento in pygame.event.get():
    if evento.type == pygame.QUIT:
      rodando = False

    elif evento.type == pygame.KEYDOWN:
      if evento.key == pygame.K_SPACE and not game_over:
        tiro = Tiro(jogador.rect.centerx, jogador.rect.top)
        todos_sprites.add(tiro)
        tiros.add(tiro)
      elif evento.key == pygame.K_r and game_over:
        # Reiniciar o jogo
        game_over = False
        pontos = 0
        tempo_sobrevivencia = 0
        jogador.vidas = 3
        jogador.rect.centerx = LARGURA // 2
        jogador.rect.bottom = ALTURA - 20
        # Limpa todos os tiros e inimigos antigos da tela
        for i in inimigos:
          i.kill()
        for t in tiros:
          t.kill()
        # Reseta o timer original
        pygame.time.set_timer(ADICIONAR_INIMIGO, 1500)

    elif evento.type == ADICIONAR_INIMIGO and not game_over:
      # Quanto mais pontos você faz, mais rápido os inimigos aparecem (o intervalo diminui)
      # Limite mínimo de 300ms para o jogo não ficar impossível de processar
      novo_intervalo = max(300, 1500 - (pontos * 15))
      pygame.time.set_timer(ADICIONAR_INIMIGO, int(novo_intervalo))

      # Aumenta um pouco a velocidade dos inimigos conforme a pontuação avança
      bonus_vel = pontos // 50
      inimigo = Inimigo(velocidade_extra=bonus_vel)
      todos_sprites.add(inimigo)
      inimigos.add(inimigo)

  if not game_over:
    todos_sprites.update()

    # Colisão: Tiros vs Inimigos
    colisoes_tiro_inimigo = pygame.sprite.groupcollide(
        tiros, inimigos, True, True
    )
    for colisao in colisoes_tiro_inimigo:
      pontos += 10

    # Colisão: Inimigos vs Jogador
    colisoes_jogador_inimigo = pygame.sprite.spritecollide(
        jogador, inimigos, True
    )
    for colisao in colisoes_jogador_inimigo:
      jogador.vidas -= 1
      if jogador.vidas <= 0:
        game_over = True
        pygame.time.set_timer(ADICIONAR_INIMIGO, 0)  # Para de criar inimigos

  # Renderização
  TELA.fill(PRETO)
  todos_sprites.draw(TELA)

  texto_pontos = FONTE.render(f"Pontuação: {pontos}", True, BRANCO)
  texto_vidas = FONTE.render(f"Vidas: {jogador.vidas}", True, VERDE)
  TELA.blit(texto_pontos, (15, 15))
  TELA.blit(texto_vidas, (15, 45))

  if game_over:
    superficie_fim = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    superficie_fim.fill((0, 0, 0, 180))
    TELA.blit(superficie_fim, (0, 0))

    msg_game_over = FONTE_FIM.render("FIM DE JOGO", True, VERMELHO)
    msg_reiniciar = FONTE.render(
        "Pressione 'R' para Reiniciar ou ESC para sair", True, BRANCO
    )

    TELA.blit(
        msg_game_over,
        (LARGURA // 2 - msg_game_over.get_width() // 2, ALTURA // 2 - 50),
    )
    TELA.blit(
        msg_reiniciar,
        (LARGURA // 2 - msg_reiniciar.get_width() // 2, ALTURA // 2 + 20),
    )

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_ESCAPE]:
      rodando = False

  pygame.display.flip()

pygame.quit()
sys.exit()