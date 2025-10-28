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

# 動く的の設定
class Move_enemy(pg.sprite.Sprite):
    """
    動く的に関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("fig/hati.png")
        self.image = pg.transform.rotozoom(self.image, 0, 0.08)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
        self.vx = random.choice([-1, 1]) * random.uniform(2, 5)
        self.vy = 1
        self.speed = 0.5

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        # if check_bound(self.rect) != (True, True):
        #     self.kill()


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
    # メインループ
    running = True

    # 背景の設定
    original_bg_img = pg.image.load(f"fig/bg_2.jpg")
    bg_width = 800
    bg_height = 600
    bg_size = (bg_width, bg_height)
    bg_img = pg.transform.scale(original_bg_img, bg_size)

    enemies = pg.sprite.Group()
    enemies.add(Move_enemy())
    enemy = Move_enemy()
    effects = pg.sprite.Group()

    while running:
        screen.blit(bg_img, [0, 0])  # 背景の描画

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # クリックで命中判定
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for enemy in enemies:
                    ex, ey = enemy.rect.center
                    distance = ((mx - ex) ** 2 + (my - ey) ** 2) ** 0.5
                    if distance <= enemy.rect.width // 2:
                        print("hit")
                        effect = Attack_effect(enemy, 40)
                        effects.add(effect)                   
                        enemy.kill()
                        enemies.add(Move_enemy())
        
        for enemy in enemies:
            enemy.update()
            # check_bound() で画面外判定
            if check_bound(enemy.rect) != (True, True):
                enemy.kill() 
                enemies.add(Move_enemy())
        
        enemy.update()
        screen.blit(enemy.image, enemy.rect)
        effects.update()
        effects.draw(screen)

        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    pg.init
    main()
    pg.quit()
    sys.exit()