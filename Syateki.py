import os
import pygame
import random
import sys
import pygame as pg

# 初期化
pygame.init()
WIDTH, HEIGHT = 800, 600
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.display.set_caption("射的ゲーム - ベース版")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
title_font = pygame.font.SysFont("msgothic", 40)
message_font = pygame.font.SysFont("msgothic", 30)

# 画面表示に関するクラス
class ScreenManager:
    """
    ゲームのスタート画面と終了画面の描写を管理するクラス
    """
    def __init__(self,screen, WIDTH, HEIGHT, title_font, message_font):
        self.screen = screen
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.title_font = title_font
        self.message_font = message_font


        # 背景画像の読み込み
        try:
            self.start_bg_img = pygame.image.load("background.jpg").convert()
            self.start_bg_img = pygame.transform.scale(self.start_bg_img,(WIDTH,HEIGHT))
        except pygame.error as e:
            print("背景画像の読み込みエラー")
            self.start_bg_img = None
        
        try:
            self.finish_bg_img = pygame.image.load("background.jpg").convert()
            self.finish_bg_img = pygame.transform.scale(self.finish_bg_img, (WIDTH, HEIGHT))
        except pygame.error as e:
            print("背景画像の読み込みエラー")
            self.finish_bg_img = None


    def start_screen(self):
        if self.start_bg_img:
            self.screen.blit(self.start_bg_img, (0, 0))
        else:
            self.screen.fill((0,0,0)) # 黒色の画面

        title_txt = self.title_font.render("射的ゲーム",True,(0,0,0,))
        title_rect = title_txt.get_rect(center=(self.WIDTH//2,self.HEIGHT//2))
        screen.blit(title_txt,title_rect)
        
        message_text = self.message_font.render("-- スペースを押してスタート --",True,(0,0,0))
        message_rect = message_text.get_rect(center=(self.WIDTH//2,self.HEIGHT//2+40))
        screen.blit(message_text,message_rect)


    def finish_screen(self, score):
        if self.finish_bg_img:
            self.screen.blit(self.finish_bg_img, (0, 0))
        else:
            self.screen.fill((0,0,0)) # 黒色の画面

        title_txt = self.title_font.render(f"最終スコア:{score}",True,(0,0,0))
        title_rect = title_txt.get_rect(center=(self.WIDTH//2,self.HEIGHT//2))
        screen.blit(title_txt,title_rect)

        message_text = self.message_font.render("-- Rキーでリトライ --", True, (150, 150, 150))
        message_rect = message_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 60))
        self.screen.blit(message_text, message_rect)

screen_manager = ScreenManager(screen, WIDTH, HEIGHT, title_font, message_font)


# スコア
score = 0
mato_num = 10

class Mato:
    """
    的に関するクラス
    """
    img = pg.transform.scale(pg.image.load("fig/1.png").convert_alpha(), (100, 100))
    used_positions = set()

    def __init__(self, radius):
        """
        的を生成するための関数
        引数：的の半径
        visible:的に命中した際に表示を切り替えるためのもの
        """
        self.radius = radius
        self.cols = 8  # 横方向分割
        self.rows = 6  # 縦方向分割
        cell_w = WIDTH // self.cols
        cell_h = HEIGHT // self.rows

        # 使用可能な範囲
        available_positions = [
            (col, row)
            for col in range(self.cols)
            for row in range(1, self.rows)
            if (col, row) not in Mato.used_positions
        ]

        # もしすべて埋まっていたらリセット
        if not available_positions:
            Mato.used_positions.clear()
            available_positions = [
                (col, row)
                for col in range(self.cols)
                for row in range(1, self.rows)
            ]

        col, row = random.choice(available_positions)
        Mato.used_positions.add((col, row))

        self.x = col * cell_w + cell_w // 2
        self.y = row * cell_h + cell_h // 2

        self.last_update = pygame.time.get_ticks()
        self.visible = True

    def update(self):
        """
        一定時間経過したら新しい位置に移動するための関数
        """
        now = pygame.time.get_ticks()
        broke_time = now - self.last_update
        if  broke_time >= 3000:
            self.visible = True
            self.last_update = now

            cell_w = WIDTH // self.cols
            cell_h = HEIGHT // self.rows

            available_positions = [
                (col, row)
                for col in range(self.cols)
                for row in range(1, self.rows)
                if (col, row) not in Mato.used_positions
            ]

            if not available_positions:
                Mato.used_positions.clear()
                available_positions = [
                    (col, row)
                    for col in range(self.cols)
                    for row in range(1, self.rows)
                ]

            col, row = random.choice(available_positions)
            Mato.used_positions.add((col, row))

            self.x = col * cell_w + cell_w // 2
            self.y = row * cell_h + cell_h // 2

    def draw(self, surface):
        """
        的を描画する関数
        """
        if self.visible:
            mato_rect = Mato.img.get_rect(center=(self.x, self.y))
            surface.blit(Mato.img, mato_rect)


mato_list = [Mato(50) for _ in range(mato_num)]

# ゲームの状態管理
game_state = "start" # ゲームの状況


# メインループ
running = True
while running:
    screen.fill((200, 220, 255))

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # スタート画面表示
        if game_state == "start":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                score = 0
                game_state = "playing" # クリックしたらゲームの状態を変更

        # クリックで命中判定
        if game_state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for mato in mato_list:
                distance = ((mx - mato.x) ** 2 + (my - mato.y) ** 2) ** 0.5
                if distance <= mato.radius and mato.visible:  # カーソルが的の中にあったら命中とする
                    score += 1
                    mato.visible = False  # スコアを加算して的を見えなくする

        # デバック用ーーーーーーーーーーーーーーーーーーーーーーーー
        if score == 10:
            game_state = "finish"



        if game_state == "finish":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                game_state = "playing"  # r でリトライ 

    # ゲームの状態による画面表示の変化
    # スタート状態
    if game_state == "start":
        screen_manager.start_screen()  # スタート画面の表示
            
    # ゲーム進行中の状態
    elif game_state == "playing":
        screen.fill((200, 220, 255)) # 背景色（水色）
        for mato in mato_list:  # 1番最初の的の表示 game_stateがplayingになったら的を表示する
            mato.update()
            mato.draw(screen)

    # ゲーム終了状態
    elif game_state == "finish":
        screen_manager.finish_screen(score)
        

    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()