"""
参数配置文件
（改随机频率、体型本文件）
"""



from pathlib import Path



import sys

if getattr(sys, "frozen", False):
    _BUNDLE = Path(sys._MEIPASS)
    PACKAGE_DIR = _BUNDLE / "feibi_pet"
    PICTURE_DIR = PACKAGE_DIR / "picture"
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PACKAGE_DIR = Path(__file__).resolve().parent
    PICTURE_DIR = PACKAGE_DIR / "picture"
    PROJECT_ROOT = PACKAGE_DIR.parent

INTERACT_TXT = PROJECT_ROOT / "Interact.txt"



#配置资源文件路径
CHARACTER_MAIN = PICTURE_DIR / "feibi_main.png"
CHARACTER_COMMON = PICTURE_DIR / "feibi_common.apng"
CHARACTER_BITE = PICTURE_DIR / "feibi_bitefile.png"
CHARACTER_HANG = PICTURE_DIR / "feibi_hang.png"
CHARACTER_SING_CLIP = PICTURE_DIR / "feibi_sing.apng"
CHARACTER_SLEEP_CLIP = PICTURE_DIR / "feibi_sleep.apng"
CHARACTER_SLEEP_2_CLIP = PICTURE_DIR / "feibi_sleep_2.apng"
CHARACTER_WAKE_CLIP = PICTURE_DIR / "feibi_wake.apng"

#配置随机动作列表
RANDOM_STEMS = (
    CHARACTER_SING_CLIP,
    CHARACTER_SLEEP_CLIP,
    CHARACTER_SLEEP_2_CLIP,
    CHARACTER_WAKE_CLIP,
)#随机动作列表



#随机参数配置（可修改）
RANDOM_TICK_MS = 4000#触发随即动作的间隔
RANDOM_CHANCE = 0.35#触发随即动作的概率
RANDOM_COOLDOWN_MS = 8000#上一次动作结束后需要多少秒才会继续触发随机判定



#控件与窗口参数（可修改）
ON_TOP = True#是否始终置顶
PET_MAX_W = 140#控制整个桌宠所有控件的最大宽高，不可修改，仅防止开发时爆内存
PET_MAX_H = 180


