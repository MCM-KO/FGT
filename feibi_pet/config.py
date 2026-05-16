"""
参数配置文件
（改随机频率、体型本文件）
"""



from pathlib import Path



PACKAGE_DIR = Path(__file__).resolve().parent#保留当前配置文件上级即包位置

PICTURE_DIR = PACKAGE_DIR / "picture"#资源位置



#配置资源文件路径
FEIBI_MAIN = PICTURE_DIR / "feibi_main.png"
FEIBI_COMMON = PICTURE_DIR / "feibi_common.apng"
FEIBI_BITE = PICTURE_DIR / "feibi_bitefile.png"
FEIBI_HANG = PICTURE_DIR / "feibi_hang.png"
FEIBI_SING_CLIP = PICTURE_DIR / "feibi_sing.apng"
FEIBI_SLEEP_CLIP = PICTURE_DIR / "feibi_sleep.apng"
FEIBI_SLEEP_2_CLIP = PICTURE_DIR / "feibi_sleep_2.apng"
FEIBI_WAKE_CLIP = PICTURE_DIR / "feibi_wake.apng"

#配置随机动作列表
RANDOM_STEMS = (
    FEIBI_SING_CLIP,
    FEIBI_SLEEP_CLIP,
    FEIBI_SLEEP_2_CLIP,
    FEIBI_WAKE_CLIP,
)#随机动作列表



#随机参数配置（可修改）
RANDOM_TICK_MS = 4000#触发随即动作的间隔
RANDOM_CHANCE = 0.35#触发随即动作的概率
RANDOM_COOLDOWN_MS = 8000#上一次动作结束后需要多少秒才会继续触发随机判定



#控件与窗口参数（可修改）
ON_TOP = True#是否始终置顶
PET_MAX_W = 140#控制整个桌宠所有控件的最大宽高，不可修改，仅防止开发时爆内存
PET_MAX_H = 180

#这里抠像的配置有待试验
# QVideoWidget 在 Windows 上常无法显示 mov 透明通道（会呈黑底）；播放走 QVideoSink + QLabel。
# 若文件自带 alpha 仍发黑：多为解码器丢掉 alpha，可把接近黑色的像素抠掉：
# None = 不抠色，仅保留帧里的 alpha；黑底常用 (0,0,0)+容差；绿幕用 (0,255,0)、TOL 设 0。
VIDEO_KEY_RGB: tuple[int, int, int] | None = None
VIDEO_KEY_TOL: int = 28

# QVideoSink 刷到 QLabel 的帧率上限（fps）
VIDEO_TARGET_FPS: float = 30.0





#尽量走openGL的驱动，避免程序崩溃对本机产生影响
# Windows：main.py 默认 AA_UseSoftwareOpenGL=开；若画面异常可设环境变量 FEIBI_SOFTWARE_OPENGL=0 试 GPU。

