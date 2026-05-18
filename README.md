# FGT + 菲比桌宠（FEIBI）

本项目由两个部分合并而成，共用同一仓库根目录：

| 包 | 作用 |
|----|------|
| **`FGT/`** | 基于 FFmpeg 的图形化工具（主窗口、安装向导、托盘、日志等） |
| **`feibi_pet/`** | 《鸣潮》角色「菲比」Windows 桌面小宠物（独立子进程） |

独立项目互动机制：\
主程序启动桌宠后，两者通过项目根目录的 **`Interact.txt`** 通信：桌宠拖入文件 → 写入该文件 → 主程序监视并填入输入框。

主技术栈：**Python 3** + **PySide6** + **OpenCV** + **ffmpeg**

---

## 一、项目结构

```text
<项目根>/
  premain.py              # 二合一的总入口（先向导，再主界面）（实际上只需要单个宠物包的话，用不到这个）
  main.py                 # 主界面逻辑（由 premain 调用 launch_main）
  main_feibi.py           # 桌宠进程入口（可以单独使用）
  Interact.txt            # FGT ↔ 桌宠 交互文件
 （关于Interact.txt运行时读写，为了解决进程隔离的问题）
 （蒟蒻的架构能力有限，所以发现进程隔离的时候只能出此下策）
  requirements.txt        #pip的需求包
  LICENSE.txt             #许可证

  FGT/                    # 主程序包
    Graphic.py            # 主窗口
    SetupGraphic.py       # 首次安装 / 配置向导
    InterSystem.py        # 与操作系统直接交互的包，包括下载、解压、设置环境变量、快捷方式等
    paths.py              # 路径（主要是打包使用）
    config_state.py       # setup_list.txt 行号约定与修复（为了配合打包用的）
    interact_watch.py     # 监视 Interact.txt
    Configuration/
      setup_list.txt        # 配置模板（固定 4 行，见下文）
    UI/                   # Qt Designer 界面
    picture/              # 主程序用图
    WIKI/                 # 内置说明文本
    logger/               # 运行日志
    buffer/               # 临时截取照片、concat 列表等

  feibi_pet/              # 桌宠包
    config.py             # 立绘路径、随机参数、Interact.txt 位置
    window.py             # 无边框置顶窗
    pet.py                # 立绘、拖放、动画（pet的核心类）
    Media.py              # 播放器
    RandomScheduler.py    # 随机调度器
    qt_transparent.py     # 透明器
    picture/              # 桌宠立绘（唯一资源目录，见下文）
```

---

## 二、启动流程

### 开发环境

在项目根目录：

```text
pip install -r requirements.txt
python premain.py
```

- 若未完成首次配置（`setup_list.txt` 第 `[1]` 行 `ISSET` 不为 `"YES"`，且不存在 `Configuration/installed.ok`），先显示 **FGT 安装向导**；向导内点「开始」后会写入 `ISSET="YES"` 并创建 `installed.ok`，此后启动均直接进入主界面。
- 向导完成后点「开始」，同一进程进入 **FGT 主窗口**，并拉起 **桌宠子进程**，完成二者的互动。
- 若仅调试桌宠，丢弃FGT图形化界面：`python main_feibi.py`

### 打包后

```text
pyinstaller FGT.spec
```

生成 `dist/FGT.exe`（单文件）。再次运行读 **exe 同目录** 下生成的 `Configuration/setup_list.txt` 等可写文件；只读资源在解压临时目录内。


## 三、配置文件 `setup_list.txt`

路径：开发时为 `FGT/Configuration/setup_list.txt`；打包后为 **exe 同目录** `Configuration/setup_list.txt`。

**固定 4 行，按行号读写（勿删行、勿打乱顺序）：**

| 行号 | 含义 |
|------|------|
| `[0]` | 注释 `#配置文件` |
| `[1]` | `ISSET="NO"` / `"YES"` — 是否已完成首次配置 |
| `[2]` | `DEFAULT_PATH="..."` — 默认浏览路径 |
| `[3]` | `DEFAULT_PATH_S="..."` — 默认存储路径 |

程序在读写前会检查文件是否满 4 行；不足则按模板补齐，避免越界。

---

## 四、FGT 主程序（`FGT/` 包）

### 功能概要

- FFmpeg 命令图形化编辑、执行与日志实现（`Graphic.py`、`ProcessCreator.py`、`LOGGER.py`）
- 首次运行安装向导：可选下载 FFmpeg（国内镜像）、解压 zip/7z、写 PATH、桌面快捷方式（`SetupGraphic.py`、`InterSystem.py`）
- 系统托盘：关闭主窗口可隐藏到托盘；退出经挽留窗（`SonGraphic.DetainWindow`）
- 监视 `Interact.txt`：桌宠拖入文件后，主窗口取**第一个路径**填入输入并可选显示主窗（`interact_watch.py`、`Graphic.apply_interact_drop`）

## 五、菲比桌宠（`feibi_pet/` 包）

### 功能概要

交互能力：
- 无边框置顶小窗，默认显示主图；支持鼠标拖动窗口（`window.py`、`pet.py`）
- 随机动作：读取 `feibi_sing.apng`、`feibi_sleep.apng`、`feibi_sleep_2.apng`、`feibi_wake.apng` 等，来实现随机播放
- 文件拖入事件：切换咬文件立绘；写入 `Interact.txt` 的 `DRAG_FILE="路径"`，供 FGT 读取

### 立绘目录（桌宠专用）

**唯一目录：`feibi_pet/picture/`**（程序不会从 `FGT/picture/` 加载桌宠图）

```text
feibi_pet/picture/
  feibi_main.png        # 常态主图（必需）
  feibi_common.apng     # 常态动态（可选）
  feibi_bitefile.png    # 拖文件时
  feibi_hang.png        # 悬挂等（可选）
  feibi_sing.apng       # 随机：唱歌
  feibi_sleep.apng      # 随机：睡觉
  feibi_sleep_2.apng    # 随机：睡觉 2
  feibi_wake.apng       # 随机：苏醒
```

### 可调参数（`feibi_pet/config.py`）

| 常量 | 含义                |
|------|-------------------|
| `RANDOM_TICK_MS` | 间隔器：随机判定间隔（毫秒）    |
| `RANDOM_CHANCE` | 概率器：每次判定触发概率（0～1） |
| `RANDOM_COOLDOWN_MS` | 冷静器：两次随机动作最短间隔    |
| `ON_TOP` | 是否窗口置顶            |
| `PET_MAX_W` / `PET_MAX_H` | 显示最大宽高（像素）        |


### 与主程序联动

桌宠 `dropEvent` 写入示例：

```text
DRAG_FILE="D:/media/example.mp4"
SHOW_MAIN=1
```

FGT 监视文件变化后读取 `DRAG_FILE`，将**第一个**路径填入主界面输入框。

开发态：主程序 `subprocess` 启动 `python main_feibi.py`。  
打包态：同一 `FGT.exe` 带参数 `--feibi-pet` 启动桌宠（`premain.py` 分支）。

---

## 六、`Interact.txt`

位于**项目根**（开发）或 **exe 同目录**（打包）。  
首次不存在时由程序创建/复制模板。  
桌宠只负责写入；FGT 负责监视与后续操作。

---

## 七、依赖

见 `requirements.txt`：

- PySide6
- opencv-python
- numpy

系统还需已安装 **ffmpeg**（可通过 FGT 安装向导下载，或自行配置 PATH）。\
拉取资源加速（采取GyanD 官方包，经国内 GitHub 加速镜像）\
解压 `.7z` 安装包需本机 **7-Zip**（或 `7z` 在 PATH 中）。

---

## 八、二创与版权

- 关于feibi_pet:《鸣潮》角色与相关素材一切版权归官方所有，请遵守官方二创与分发规范。
- 关于FGT:ffmpeg为Fabrice Bellard于2000年发起的开源项目，全称Fast Forward MPEG,遵守GPL/LGPL的开源协议

---

## 九、版本说明（仓库合并后）

- **合并版**：`premain.py` 统一入口；FGT 主程序 + `feibi_pet` 子进程；`Interact.txt` 联动；PyInstaller 单文件打包。
- 桌宠单包时期说明（APNG 随机、仅 `feibi_pet/picture` 等）仍适用于 **`feibi_pet/`** 目录行为，主程序以 **`FGT/`** 与本文「启动流程」「配置文件」为准。

## 十、作者有话说



整个项目用 **Python** 编写，没有任何复杂算法；甚至后端完全采用最简单的**拼接**形式  
为了方便理解，每个方法都配有中文注释



因为蒟蒻全栈 **MCM-KO** 本人的前端能力实在有限，UI有亿点点丑  
因此把 **`feibi_pet`** 与 **`FGT`** 拆成两个包：若你**只要桌宠**，拉取 `feibi_pet/` 与 `main_feibi.py` 即可。

### 关于二创桌宠

桌宠侧尽量保持 **可替换、可扩展**：

| 你想做的事 | 建议改哪里 |
|------------|------------|
| 换立绘 / 换动图 | `feibi_pet/picture/` 放资源 → `config.py` 改路径 |
| 加新的随机动作 | `config.py` 的 `RANDOM_STEMS` + 对应 `.apng` |
| 加全新交互逻辑 | 参考 `pet.py` 现有写法仿写一段即可 |

### 欢迎反馈

欢迎各位大佬对我们的结构和代码提出批评与指正！

