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

font_normal = pygame.font.SysFont(None, 40)
font_large  = pygame.font.SysFont(None, 70)
# 的の設定
target_radius = 30
target_x = random.randint(target_radius, WIDTH - target_radius)
target_y = random.randint(target_radius, HEIGHT - target_radius)

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def time_desiplay_count(screen:pygame.surface, font_normal:pygame.font, font_large:pygame.font, start_time_ms:int, time_limit_ms:int)-> bool:
    """
    制限時間の表示と時間切れの判定を行う関数
    引数screen pygameのsurface
    font pygameのfont
    start_time_ms (int)ゲーム開始の時間(ミリセカンド)
    time_limit_ms (int)制限時間(ミリセカンド)
    """
    current_time_ms = pygame.time.get_ticks()
    # 経過時間を計算
    elapsed_time_ms = current_time_ms - start_time_ms
    # 残り時間を計算
    remaining_time_ms = time_limit_ms - elapsed_time_ms
    # 残り時間を計算し、表示用に整数に変換
    remaining_seconds = max(0, remaining_time_ms // 1000)
    # 残り時間のテキストを作成(10秒以内になったら赤文字になる)
    if remaining_seconds <= 10:
        timer_text = font_large.render(f"time: {remaining_seconds}s", True, (255, 0, 0))
    else:
        timer_text = font_normal.render(f"time: {remaining_seconds}s", True, (0, 0, 0))
    # テキストを画面の右上に描画
    screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 10))
    # 時間切れの判定
    return remaining_time_ms <= 0


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



# 動く的の設定
class Move_enemy(pg.sprite.Sprite):
    """
    動く的に関するクラス
    """
    image = pg.image.load("fig/hati.png")
    image = pg.transform.rotozoom(image, 0, 0.08)

    def __init__(self):
        super().__init__()
        self.vx = random.choice([-1, 1]) * random.uniform(2, 6)
        self.vy = 1
        if self.vx < 0: # 向き変更
            self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
        self.speed = 0.5

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
    

class Attack_effect(pg.sprite.Sprite):
    """
    エフェクトに関するクラス
    """
    def __init__(self, obj: "Move_enemy", effect_time: int):
        """
        的が壊れるエフェクトを生成
        引数1 obj : 壊れる的
        引数2 effect_time : 壊れる時間
        """
        super().__init__()
        img = pg.image.load(f"fig/effect_1.gif")
        img = pg.transform.scale(img, (img.get_width()*2, img.get_height()*2))
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.effect_time = effect_time
        

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.effect_time -= 1
        self.image = self.imgs[self.effect_time//10%2]
        if self.effect_time < 0:
            self.kill()


def main():
    screen_manager = ScreenManager(screen, WIDTH, HEIGHT, title_font, message_font)
    # スコア
    score = 0
    mato_num = 10
    #制限時間
    time_limit_sec = 60
    time_limit_ms = time_limit_sec * 1000
    start_time_ms = pygame.time.get_ticks()
    # ゲームの状態管理
    game_state = "start" # ゲームの状況
    mato_list = [Mato(50) for _ in range(mato_num)]

    original_bg_img = pg.image.load(f"fig/bg_2.jpg")
    bg_width = 800
    bg_height = 600
    bg_size = (bg_width, bg_height)
    bg_img = pg.transform.scale(original_bg_img, bg_size)

    # メインループ
    running = True

    enemies = pg.sprite.Group()
    enemies.add(Move_enemy())
    enemy = Move_enemy()
    effects = pg.sprite.Group()

    while running:
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
                mx, my = pg.mouse.get_pos()

                # 的の命中判定
                for mato in mato_list:
                    distance = ((mx - mato.x) ** 2 + (my - mato.y) ** 2) ** 0.5
                    if distance <= mato.radius and mato.visible:  # カーソルが的の中にあったら命中とする
                        score += 10
                        mato.visible = False  # スコアを加算して的を見えなくする

                # 動く的の命中判定
                for enemy in enemies:
                    ex, ey = enemy.rect.center
                    distance = ((mx - ex) ** 2 + (my - ey) ** 2) ** 0.5
                    if distance <= enemy.rect.width // 2:
                        # print(score)
                        score += 30
                        effect = Attack_effect(enemy, 40)
                        effects.add(effect)                   
                        enemy.kill()
                        enemies.add(Move_enemy())

            # デバック用ーーーーーーーーーーーーーーーーーーーーーーーー
            if score >= 100:
                game_state = "finish"

            if game_state == "finish":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    score = 0
                    game_state = "playing"  # r でリトライ 
                    time_limit_sec = 60
                    time_limit_ms = time_limit_sec * 1000
                    start_time_ms = pygame.time.get_ticks()
            for enemy in enemies:
                enemy.update()
                # check_bound() で画面外判定
                if check_bound(enemy.rect) != (True, True):
                    enemy.kill() 
                    enemies.add(Move_enemy())
        


            # ゲームの状態による画面表示の変化
            # スタート状態
        if game_state == "start":
            screen_manager.start_screen()  # スタート画面の表示    
        # ゲーム進行中の状態
        elif game_state == "playing":
            # 背景の設定
            screen.blit(bg_img, [0, 0])
            count_display_time = time_desiplay_count(screen, font_normal, font_large, start_time_ms, time_limit_ms)
            for mato in mato_list:  # 1番最初の的の表示 game_stateがplayingになったら的を表示する
                mato.update()
                mato.draw(screen)

            enemy.update()
            screen.blit(enemy.image, enemy.rect)
            #ゲーム終了
            if count_display_time == True:
                game_state ="finish"

        # ゲーム終了状態
        elif game_state == "finish": 
            screen_manager.finish_screen(score)
            time_limit_sec = 60
            time_limit_ms = time_limit_sec * 1000
            start_time_ms = pygame.time.get_ticks()


        effects.update()
        effects.draw(screen)

        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    pg.init
    main()
    pg.quit()
    sys.exit()