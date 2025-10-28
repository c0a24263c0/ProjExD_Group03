import os
import pygame
import random
import sys

# 初期化
pygame.init()
WIDTH, HEIGHT = 800, 600
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.display.set_caption("射的ゲーム - ベース版")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font_normal = pygame.font.SysFont(None, 40)
font_large  = pygame.font.SysFont(None, 70)
# 的の設定
target_radius = 30
target_x = random.randint(target_radius, WIDTH - target_radius)
target_y = random.randint(target_radius, HEIGHT - target_radius)

# スコア
score = 0

#制限時間
time_limit_sec = 30
time_limit_ms = time_limit_sec * 1000
start_time_ms = pygame.time.get_ticks()

#難易度lv
#diff_lv = 1


def time_desiplay_count(screen:pygame.surface, font_normal:pygame.font, font_large:pygame.font, start_time_ms:int, time_limit_ms:int)-> bool:
    """
    制限時間の表示と時間切れの判定を行う関数
    引数screen
    font
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


#def level_display(screen, font:str, start_time_ms:int, time_limit_ms:int, diff_lv):
    """
    難易度lvの表示
    20秒ごとに難易度を上げる
    """
    #current_time_ms = pygame.time.get_ticks()
    #elapsed_time_ms = current_time_ms - start_time_ms
    #remainng_time_ms = time_limit_ms - elapsed_time_ms
    #remainng_seconds = max(0, remainng_time_ms // 1000)
    #if remainng_seconds % 20 == 0:
        #diff_lv += 1
    #level_text = font.render(f"now difficult level:{diff_lv}lv", True, (0,0,0))
    #screen.blit(level_text, (WIDTH - level_text.get_width() -10, 30))
# メインループ
running = True
while running:
    screen.fill((200, 220, 255))  # 背景色（水色）

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # クリックで命中判定
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            distance = ((mx - target_x) ** 2 + (my - target_y) ** 2) ** 0.5
            if distance <= target_radius:
                score += 1
                # 的をランダムに再配置
                target_x = random.randint(target_radius, WIDTH - target_radius)
                target_y = random.randint(target_radius, HEIGHT - target_radius)

    # 的の描画
    pygame.draw.circle(screen, (255, 0, 0), (target_x, target_y), target_radius)
    pygame.draw.circle(screen, (255, 255, 255), (target_x, target_y), target_radius // 2)

    # スコア表示
    score_text = font_normal.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    count_display_time = time_desiplay_count(screen, font_normal, font_large, start_time_ms, time_limit_ms)
    if count_display_time:
        running = False
    #count_level_display = level_display(screen, font_normal, start_time_ms, time_limit_ms, diff_lv)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()