import pygame
import sys
import random
import time
import os

screen_size = (700, 540)
screen = pygame.display.set_mode(screen_size)
pygame.init()
game_over_sound = pygame.mixer.Sound(os.path.join('data', 'game_over.wav'))
apple_eat_sound = pygame.mixer.Sound(os.path.join('data', 'apple_eat.wav'))
difficulty = 'Легко'
last_score = 0


class Game():
	def __init__(self):
		self.screen_size = (720, 460)
		self.screen = pygame.display.set_mode(self.screen_size)
		self.fps_controller = pygame.time.Clock()
		self.score = 0
	
	def event_loop(self, change_to):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RIGHT or event.key == ord('d'):
					change_to = "RIGHT"
				elif event.key == pygame.K_LEFT or event.key == ord('a'):
					change_to = "LEFT"
				elif event.key == pygame.K_UP or event.key == ord('w'):
					change_to = "UP"
				elif event.key == pygame.K_DOWN or event.key == ord('s'):
					change_to = "DOWN"
			elif event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		return change_to
	
	def refresh_screen(self):
		pygame.display.flip()
		if difficulty == 'Легко':
			game.fps_controller.tick(15)
		elif difficulty == 'Нормально':
			game.fps_controller.tick(25)
		else:
			game.fps_controller.tick(40)
	
	def show_score(self, choice=1):
		score_font = pygame.font.Font(None, 50)
		score_string = score_font.render(
			'Счёт: {0}'.format(self.score), True, pygame.Color('black'))
		score_rect = score_string.get_rect()
		if choice == 1:
			score_rect.midtop = (80, 10)
		else:
			score_rect.midtop = (360, 120)
		self.screen.blit(score_string, score_rect)
	
	def game_over(self):
		game_over_sound.play()
		game_over_font = pygame.font.Font(None, 100)
		game_over_string = game_over_font.render('Конец игры!', True, pygame.Color('red'))
		game_over_rect = game_over_string.get_rect()
		game_over_rect.midtop = (360, 150)
		self.screen.blit(game_over_string, game_over_rect)
		self.show_score(0)
		global last_score
		last_score = self.score
		pygame.display.flip()
		time.sleep(3)
		pygame.mixer.music.load(os.path.join('data', 'lobby_music.mp3'))
		pygame.mixer.music.play(-1)
		menu.menu_game_over()


class Snake():
	def __init__(self, snake_color):
		# позиция головы змеи и её тела
		self.snake_head_pos = [100, 50]
		# начальное тело змеи состоит из трех сегментов
		# голова змеи - первый элемент, хвост - последний
		self.snake_body = [[100, 50], [90, 50], [80, 50]]
		self.snake_color = snake_color
		# изначально движение вправо
		self.direction = "RIGHT"
		self.change_to = self.direction
	
	def direction_change(self):
		# Направление движения змеи не меняется,
		# если оно противоположно текущему
		if any((self.change_to == "RIGHT" and not self.direction == "LEFT",
		        self.change_to == "LEFT" and not self.direction == "RIGHT",
		        self.change_to == "UP" and not self.direction == "DOWN",
		        self.change_to == "DOWN" and not self.direction == "UP")):
			self.direction = self.change_to
	
	def change_head_position(self):
		if self.direction == "RIGHT":
			self.snake_head_pos[0] += 10
		elif self.direction == "LEFT":
			self.snake_head_pos[0] -= 10
		elif self.direction == "UP":
			self.snake_head_pos[1] -= 10
		elif self.direction == "DOWN":
			self.snake_head_pos[1] += 10
	
	def snake_body_change(self, score, food_pos, screen_size):
		# если вставлять просто snake_head_pos,
		# то на всех трех позициях в snake_body
		# окажется один и тот же список с одинаковыми координатами
		# и мы будем управлять змеей из одного квадрата
		self.snake_body.insert(0, list(self.snake_head_pos))
		# если змея съела яблоко
		if (self.snake_head_pos[0] == food_pos[0] and
				self.snake_head_pos[1] == food_pos[1]):
			apple_eat_sound.play()
			# яблоко появляется в случайном месте
			food_pos = [random.randrange(1, screen_size[0] / 10) * 10,
			            random.randrange(1, screen_size[1] / 10) * 10]
			score += 1
		else:
			# постоянно убираем хвост змеи,
			# иначе она будет постоянно расти
			self.snake_body.pop()
		return score, food_pos
	
	def draw_snake(self, screen, surface_color):
		screen.fill(surface_color)
		fon = pygame.transform.scale(load_image('game_background.jfif'), (720, 460))
		screen.blit(fon, (0, 0))
		for pos in self.snake_body:
			pygame.draw.rect(screen, self.snake_color, pygame.Rect(pos[0], pos[1], 10, 10))
	
	def check_for_game_over(self, game_over, screen_size):
		# проверка на то, что змея врезалась в стену
		if any((
				self.snake_head_pos[0] > screen_size[0] - 10
				or self.snake_head_pos[0] < 0,
				self.snake_head_pos[1] > screen_size[1] - 10
				or self.snake_head_pos[1] < 0
		)):
			game_over()
		for block in self.snake_body[1:]:
			# проверка на то, что первый элемент(голова) врезался в
			# любой другой элемент змеи (закольцевались)
			if (block[0] == self.snake_head_pos[0] and
					block[1] == self.snake_head_pos[1]):
				game_over()


class Apple():
	def __init__(self, apple_color, screen_size):
		self.apple_color = apple_color
		self.apple_size_x = 10
		self.apple_size_y = 10
		self.apple_pos = [random.randrange(1, screen_size[0] / 10) * 10,
		                  random.randrange(1, screen_size[1] / 10) * 10]
	
	def draw_apple(self, play_surface):
		pygame.draw.rect(
			play_surface, self.apple_color, pygame.Rect(
				self.apple_pos[0], self.apple_pos[1],
				self.apple_size_x, self.apple_size_y))


def load_image(name, color_key=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error as message:
		print('Не могу загрузить изображение:', name)
		raise SystemExit(message)
	if color_key is not None:
		if color_key == -1:
			color_key = image.get_at((0, 0))
		image.set_colorkey(color_key)
	else:
		image = image.convert_alpha()
	return image


def terminate():
	pygame.quit()
	sys.exit()


class Menu():
	def __init__(self):
		self.results = dict()
	def start_screen(self):
		screen = pygame.display.set_mode(screen_size)
		pygame.display.set_caption('Змейка')
		intro_text = ["Змейка!", "",
		              "Начать игру",
		              "Рекорды",
		              "Выйти"]
		fon = pygame.transform.scale(load_image('fon.jpg'), (700, 540))
		screen.blit(fon, (0, 0))
		font = pygame.font.Font(None, 100)
		text_coord = 50
		lines_coords = []
		for line in intro_text:
			string_rendered = font.render(line, 1, pygame.Color('black'))
			intro_rect = string_rendered.get_rect()
			text_coord += 10
			intro_rect.top = text_coord
			intro_rect.x = 10
			text_coord += intro_rect.height
			screen.blit(string_rendered, intro_rect)
			lines_coords.append(intro_rect)
		while True:
			mouse = pygame.mouse.get_pos()
			if 410 > mouse[0] > 15 and 275 > mouse[1] > 225:
				screen.blit(font.render(intro_text[2], 1, pygame.Color('white')), lines_coords[2])
			else:
				screen.blit(font.render(intro_text[2], 1, pygame.Color('black')), lines_coords[2])
			
			if 322 > mouse[0] > 15 and 370 > mouse[1] > 304:
				screen.blit(font.render(intro_text[3], 1, pygame.Color('white')), lines_coords[3])
			else:
				screen.blit(font.render(intro_text[3], 1, pygame.Color('black')), lines_coords[3])
			
			if 225 > mouse[0] > 15 and 435 > mouse[1] > 385:
				screen.blit(font.render(intro_text[4], 1, pygame.Color('white')), lines_coords[4])
			else:
				screen.blit(font.render(intro_text[4], 1, pygame.Color('black')), lines_coords[4])
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					terminate()
				elif event.type == pygame.MOUSEBUTTONDOWN and 410 > mouse[0] > 15 and 275 > mouse[1] > 225:
					self.difficulty()
				elif event.type == pygame.MOUSEBUTTONDOWN and 322 > mouse[0] > 15 and 370 > mouse[1] > 304:
					self.leaderboard()
				elif event.type == pygame.MOUSEBUTTONDOWN and 225 > mouse[0] > 15 and 435 > mouse[1] > 385:
					terminate()
			pygame.display.flip()
	
	def leaderboard(self):
		fon = pygame.transform.scale(load_image('fon.jpg'), (700, 540))
		screen.blit(fon, (0, 0))
		font = pygame.font.Font(None, 30)
		text_coord = 50
		string_menu = pygame.font.Font(None, 80).render("Главное меню", 1, pygame.Color('black'))
		screen.blit(string_menu, (250, 450))
		count = 1
		for line in {k: v for k, v in sorted(self.results.items(), key=lambda item: item[1], reverse=True)}:
			string_rendered = font.render(str(count) + ')' + ' ' + line, 1, pygame.Color('black'))
			count += 1
			intro_rect = string_rendered.get_rect()
			text_coord += 10
			intro_rect.top = text_coord
			intro_rect.x = 10
			text_coord += intro_rect.height
			screen.blit(string_rendered, intro_rect)
		
		while True:
			mouse = pygame.mouse.get_pos()
			if 685 > mouse[0] > 255 and 500 > mouse[1] > 455:
				screen.blit(pygame.font.Font(None, 80).render("Главное меню", 1, pygame.Color('white')), (250, 450))
			else:
				screen.blit(pygame.font.Font(None, 80).render("Главное меню", 1, pygame.Color('black')), (250, 450))
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					terminate()
				elif event.type == pygame.MOUSEBUTTONDOWN and 685 > mouse[0] > 255 and 500 > mouse[1] > 455:
					self.start_screen()
			pygame.display.flip()
			
	def menu_game_over(self):
		screen = pygame.display.set_mode(screen_size)
		fon = pygame.transform.scale(load_image('fon.jpg'), (700, 540))
		screen.blit(fon, (0, 0))
		game_over_font = pygame.font.Font(None, 72)
		game_over_string = game_over_font.render('Конец игры!', True, pygame.Color('red'))
		game_over_rect = game_over_string.get_rect()
		game_over_rect.midtop = (360, 15)
		screen.blit(game_over_string, game_over_rect)
		score_font = pygame.font.Font(None, 50)
		score_string = score_font.render(
			'Счёт: {0}'.format(last_score), True, pygame.Color('black'))
		score_rect = score_string.get_rect()
		score_rect.midtop = (360, 80)
		screen.blit(score_string, score_rect)
		font = pygame.font.Font(None, 80)
		
		string_menu = font.render("Главное меню", 1, pygame.Color('black'))
		screen.blit(string_menu, (250, 450))
		
		screen.blit(pygame.font.Font(None, 50).render("Сохранить результат:", 1, pygame.Color('black')), (0, 200))
		screen.blit(pygame.font.Font(None, 50).render("(Введите имя и нажмите Enter)", 1, pygame.Color('black')), (0, 250))
		input_box = pygame.Rect(380, 200, 140, 32)
		color_inactive = pygame.Color('black')
		color_active = pygame.Color('white')
		color = color_inactive
		active = False
		text = ''
		
		while True:
			mouse = pygame.mouse.get_pos()
			if 685 > mouse[0] > 255 and 500 > mouse[1] > 455:
				screen.blit(font.render("Главное меню", 1, pygame.Color('white')), (250, 450))
			else:
				screen.blit(font.render("Главное меню", 1, pygame.Color('black')), (250, 450))
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					terminate()
				if event.type == pygame.MOUSEBUTTONDOWN:
					if input_box.collidepoint(event.pos):
						# Toggle the active variable.
						active = not active
					else:
						active = False
					color = color_active if active else color_inactive
				if event.type == pygame.KEYDOWN:
					if active:
						if event.key == pygame.K_RETURN:
							result = '{0}: {1} очков - Сложность: {2}'.format(text, last_score, difficulty)
							self.results[result] = last_score
							text = ''
							self.start_screen()
						elif event.key == pygame.K_BACKSPACE:
							text = text[:-1]
						else:
							text += event.unicode
				if event.type == pygame.MOUSEBUTTONDOWN and 685 > mouse[0] > 255 and 500 > mouse[1] > 455:
					self.start_screen()
			txt_surface = pygame.font.Font(None, 32).render(text, True, color)
			width = 310
			input_box.w = width
			screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
			pygame.draw.rect(screen, color, input_box, 2)
			
			pygame.display.flip()
	
	def difficulty(self):
		difficulty_text = ["Выберите сложность:", "",
		                   "Легко",
		                   "Нормально",
		                   "Сложно"]
		fon = pygame.transform.scale(load_image('fon.jpg'), (700, 540))
		screen.blit(fon, (0, 0))
		font = pygame.font.Font(None, 90)
		text_coord = 50
		lines_coords = []
		string_menu = font.render("Главное меню", 1, pygame.Color('black'))
		screen.blit(string_menu, (250, 450))
		for line in difficulty_text:
			string_rendered = font.render(line, 1, pygame.Color('black'))
			intro_rect = string_rendered.get_rect()
			text_coord += 10
			intro_rect.top = text_coord
			intro_rect.x = 10
			text_coord += intro_rect.height
			screen.blit(string_rendered, intro_rect)
			lines_coords.append(intro_rect)
		
		while True:
			mouse = pygame.mouse.get_pos()
			if 186 > mouse[0] > 13 and 255 > mouse[1] > 210:
				screen.blit(font.render(difficulty_text[2], 1, pygame.Color('white')), lines_coords[2])
			else:
				screen.blit(font.render(difficulty_text[2], 1, pygame.Color('black')), lines_coords[2])
			
			if 345 > mouse[0] > 15 and 340 > mouse[1] > 282:
				screen.blit(font.render(difficulty_text[3], 1, pygame.Color('white')), lines_coords[3])
			else:
				screen.blit(font.render(difficulty_text[3], 1, pygame.Color('black')), lines_coords[3])
			
			if 250 > mouse[0] > 15 and 400 > mouse[1] > 355:
				screen.blit(font.render(difficulty_text[4], 1, pygame.Color('white')), lines_coords[4])
			else:
				screen.blit(font.render(difficulty_text[4], 1, pygame.Color('black')), lines_coords[4])
			
			if 685 > mouse[0] > 255 and 500 > mouse[1] > 455:
				screen.blit(font.render("Главное меню", 1, pygame.Color('white')), (250, 450))
			else:
				screen.blit(font.render("Главное меню", 1, pygame.Color('black')), (250, 450))
			
			flag = False
			global difficulty
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					terminate()
				elif event.type == pygame.MOUSEBUTTONDOWN and 265 > mouse[0] > 15 and 255 > mouse[1] > 210:
					difficulty = 'Легко'
					flag = True
				elif event.type == pygame.MOUSEBUTTONDOWN and 345 > mouse[0] > 15 and 340 > mouse[1] > 282:
					difficulty = 'Нормально'
					flag = True
				elif event.type == pygame.MOUSEBUTTONDOWN and 250 > mouse[0] > 15 and 400 > mouse[1] > 355:
					difficulty = 'Сложно'
					flag = True
				elif event.type == pygame.MOUSEBUTTONDOWN and 685 > mouse[0] > 255 and 500 > mouse[1] > 455:
					self.start_screen()
				
				if flag:
					pygame.mixer.music.stop()
					game = Game()
					snake = Snake(pygame.Color('blue'))
					while True:
						snake.change_to = game.event_loop(snake.change_to)
						snake.direction_change()
						snake.change_head_position()
						game.score, apple.apple_pos = snake.snake_body_change(
							game.score, apple.apple_pos, game.screen_size)
						snake.draw_snake(game.screen, pygame.Color('white'))
						apple.draw_apple(game.screen)
						snake.check_for_game_over(game.game_over, game.screen_size)
						game.show_score()
						game.refresh_screen()
			pygame.display.flip()


menu = Menu()
game = Game()
apple = Apple(pygame.Color('red'), game.screen_size)
running = True
clock = pygame.time.Clock()
pygame.mixer.music.load(os.path.join('data', 'lobby_music.mp3'))
pygame.mixer.music.play(-1)
menu.start_screen()
