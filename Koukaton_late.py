import pygame as pg
import sys
import os
import random


# 指定条件
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# =====================
# 定数
# =====================
WIDTH, HEIGHT = 800, 450
FPS = 60
GROUND_Y = 360
GRAVITY = 1
JUMP_POWER = -18
MAX_JUMP = 3


# =====================
# 初期化
# =====================
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("こうかとん、講義に遅刻する")
clock = pg.time.Clock()
font = pg.font.SysFont(None, 32)
bg_img = pg.image.load("fig/kyanpus.jpg").convert()  #ゴール時にキャンパスの写真表示
bg_img = pg.transform.scale(bg_img, (WIDTH, HEIGHT))
gameover_bg = pg.image.load("fig/sensei_okoru.png").convert()  #ゲームオーバー時に先生が起こっている写真表示
gameover_bg = pg.transform.scale(gameover_bg, (WIDTH, HEIGHT))


# =====================
# 主人公
# =====================
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("C:/Users/Admin/Documents/ProjExD/ex4/fig/2.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect(midbottom=(150, GROUND_Y))
        self.vel_y = 0
        self.jump_count = 0

    def update(self, grounds):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        landed = False
        for g in grounds:
            if (
                self.rect.colliderect(g)
                and self.vel_y >= 0
                and self.rect.bottom - self.vel_y <= g.top
            ):
                self.rect.bottom = g.top
                self.vel_y = 0
                self.jump_count = 0
                landed = True

        # 画面下に落ちたら穴落下
        if not landed and self.rect.top > HEIGHT:
            return "fall"
        return None

    def jump(self):
        if self.jump_count < MAX_JUMP:
            self.vel_y = JUMP_POWER
            self.jump_count += 1


# =====================
# 段差
# =====================
class Step:
    def __init__(self, x):
        h = random.choice([40, 80])
        w = random.randint(80, 140)
        self.rect = pg.Rect(x, GROUND_Y - h, w, h)

    def update(self, speed):
        self.rect.x -= speed


# =====================
# 穴
# =====================
class Hole:
    def __init__(self, x):
        w = random.randint(100, 160)
        self.rect = pg.Rect(x, GROUND_Y, w, HEIGHT)

    def update(self, speed):
        self.rect.x -= speed


# =====================
# ゴール旗
# =====================
class GoalFlag:
    def __init__(self, x):
        self.pole = pg.Rect(x, GROUND_Y - 120, 10, 120)
        self.flag = pg.Rect(x + 10, GROUND_Y - 120, 50, 30)

    def update(self, speed):
        self.pole.x -= speed
        self.flag.x -= speed

    def draw(self):
        pg.draw.rect(screen, (200, 200, 200), self.pole)
        pg.draw.rect(screen, (255, 0, 0), self.flag)


# =====================
# メイン
# =====================
def main():
    stage = 1
    speed = 6
    goal_distance = 2500

    while True:
        player = Player()
        steps = []
        holes = []
        goal = GoalFlag(goal_distance)
        frame = 0
        state = "play"
        next_stage = False
        clear_screen = ClearScreen(bg_img, font)
        gameover_screen = GameOverScreen(gameover_bg, font)

        while True:
            # ---------- イベント ----------
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE and state == "play":
                        player.jump()

                    if state == "clear":
                        if event.key == pg.K_y:
                            stage += 1
                            speed += 1
                            goal_distance += 1500
                            next_stage = True
                        if event.key == pg.K_n:
                            pg.quit()
                            sys.exit()

                    if state == "gameover" and event.key == pg.K_r:
                        next_stage = True

            # ---------- ゲーム処理 ----------
            if state == "play":
                frame += 1

                if frame % 80 == 0:
                    x = WIDTH + 50
                    if random.random() < 0.5:
                        steps.append(Step(x))
                    else:
                        holes.append(Hole(x))

                for s in steps:
                    s.update(speed)
                for h in holes:
                    h.update(speed)
                goal.update(speed)

                # ===== 地面生成（穴を除外） =====
                base_grounds = [pg.Rect(0, GROUND_Y, WIDTH, HEIGHT)]

                for h in holes:
                    new_grounds = []
                    for g in base_grounds:
                        if not g.colliderect(h.rect):
                            new_grounds.append(g)
                        else:
                            if g.left < h.rect.left:
                                new_grounds.append(
                                    pg.Rect(g.left, g.top, h.rect.left - g.left, g.height)
                                )
                            if h.rect.right < g.right:
                                new_grounds.append(
                                    pg.Rect(h.rect.right, g.top, g.right - h.rect.right, g.height)
                                )
                    base_grounds = new_grounds

                grounds = base_grounds + [s.rect for s in steps]

                if player.update(grounds) == "fall":
                    state = "gameover"

                # 段差の横衝突                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                for s in steps:
                    if player.rect.colliderect(s.rect):
                        if not (player.rect.bottom <= s.rect.top + 5 and player.vel_y >= 0):
                            state = "gameover"

                # ゴール
                if player.rect.colliderect(goal.pole):
                    state = "clear"

            # ---------- 描画 ----------
            screen.fill((135, 206, 235))
            pg.draw.rect(screen, (50, 200, 50), (0, GROUND_Y, WIDTH, HEIGHT))

            for h in holes:
                pg.draw.rect(screen, (0, 0, 0), h.rect)
            for s in steps:
                pg.draw.rect(screen, (50, 200, 50), s.rect)

            goal.draw()
            screen.blit(player.image, player.rect)

            screen.blit(font.render(f"STAGE {stage}", True, (0, 0, 0)), (10, 10))

            # 半透明背景用Surface
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)   # 0=完全透明, 255=不透明（150〜180がおすすめ）
            overlay.fill((255, 255, 255))  # 白

            if state == "gameover":
                gameover_screen.draw(screen)

            elif state == "clear":
                clear_screen.draw(screen)

            pg.display.update()
            clock.tick(FPS)

            if next_stage:
                break


# =====================
# ゴール画面クラス
# =====================
class ClearScreen:
    """
    ゴールの旗に着いた時にゴールの画面を表示するクラス
    """
    def __init__(self, bg_img: pg.Surface, font: pg.font.Font) -> None:
        """
        screen : pg.Surface描画対象となる画面
        """
        self.bg_img = bg_img
        self.font = font

    def draw(self, screen: pg.Surface) -> None:
        # 背景
        screen.blit(self.bg_img, (0, 0))

        # 半透明オーバーレイ
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))

        # 文字
        title = self.font.render(
            "Arrival at campus. Avoid being late!", True, (0, 120, 0)
        )
        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2 - 150, HEIGHT // 2 - 80))
        )

        sub = self.font.render(
            "The next day?  Y / N", True, (0, 0, 0)
        )
        screen.blit(
            sub,
            sub.get_rect(center=(WIDTH // 2 - 150, HEIGHT // 2 - 30))
        )


# =====================
# ゲームオーバー画面クラス
# =====================
class GameOverScreen:
    """
    段差に当たった時や穴に落ちたときにゲームオーバーを表示させるクラス
    """
    def __init__(self, bg_img: pg.Surface, font: pg.font.Font) -> None:
        """
        bg_img : ゲームオーバー画面の背景画像
        font : 文字描画に使用するフォント
        """
        self.bg_img = bg_img
        self.font = font

    def draw(self, screen: pg.Surface) -> None:
        # 背景
        screen.blit(self.bg_img, (0, 0))

        # 半透明オーバーレイ
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(140)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))

        # 文字
        title = self.font.render(
            "Kokaton is late.....", True, (200, 0, 0)
        )
        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        )

        retry = self.font.render(
            "R : Retry", True, (0, 0, 0)
        )
        screen.blit(
            retry,
            retry.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        )

# =====================
if __name__ == "__main__":
    main()
