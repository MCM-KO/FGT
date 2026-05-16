# 菲比桌宠（FEIBI）— 使用说明

面向《鸣潮》角色「菲比」的 Windows 桌面小宠物示例。程序使用 **Python 3** + **PyQt6**：无边框置顶小窗口展示立绘，并支持：

1. **常态与随机**：资源**仅**目录 `feibi_pet/picture/`。随机动作若存在同名 **MP4**（`feibi_sing.mp4`、`feibi_sleep.mp4`、`feibi_wake.mp4`），由 `feibi_pet/random_movement_mp4.py` **优先播放**；否则使用 **PNG/JPG** 等静态图 + 弹跳。
2. **拖文件到角色上**：优先切换为 ``feibi_bitefile`` 立绘并播「吃文件」动效（无该图时用 ``feibi_eating`` 或主图）；**默认不删除、不移动**磁盘文件。
3. **用鼠标拖动角色**：整个桌宠窗口跟随光标移动。

**唯一资源目录**：`feibi_pet/picture/`。主图、随机图、咀嚼图与上述 MP4 **全部**放在此目录；程序不会从别处加载。

---

## 一、图片必须放在哪个文件夹？

**统一目录（在 Python 包内）：**

```text
<项目根>/
  feibi_pet/
    picture/
      feibi_main.png      ← 常态过度图
      feibi_eating.png    ← 可选：拖文件咀嚼（无 bitefile 时使用）
      feibi_bitefile.png  ← 拖文件到角色位置时会显示咬文件
      feibi_sing.mov      ← 唱歌动作
      feibi_sleep.mov     ← 第一版睡觉动作
      feibi_sleep_2.mov   ← 第二版睡觉动作
      feibi_wake.mov      ← 苏醒动作
```

---

## 二、主图 `feibi_main` 在逻辑上的地位

- 启动后默认显示主图；窗口客户区大小与主图像素尺寸一致。
- 随机动作图若缺失，内部会**自动退回主图**，避免空白或崩溃。
- 若主图文件也不存在，会显示程序内置的简易占位图（仅便于开发调试）；正式使用请务必放入 **`feibi_pet/picture/feibi_main.png`**。

---

## 三、安装与运行

在项目根目录（与 `main.py` 同级）执行：

```text
pip install -r requirements.txt
python main.py
```

Windows PowerShell 示例（使用本仓库虚拟环境）：

```text
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

---

## 四、可调参数（`feibi_pet/config.py`）

该文件内有**更细的中文说明**（模块顶部长注释），此处列出常用项：

| 常量 | 含义 |
|------|------|
| `RANDOM_ACTION_TICK_MS` | 每隔多少毫秒「尝试」一次是否触发随机动作 |
| `RANDOM_ACTION_CHANCE` | 每次尝试实际触发的概率（0～1） |
| `RANDOM_ACTION_COOLDOWN_MS` | 两次随机动作之间的最短间隔 |
| `ACTION_*_DISPLAY_MS` | 三种随机姿态在屏幕上的总展示时间（含开头短弹跳） |
| `EAT_ANIMATION_MS` | 吃文件动效总时长 |
| `ALWAYS_ON_TOP` | 是否总在最前 |
| `PET_DISPLAY_MAX_WIDTH` / `PET_DISPLAY_MAX_HEIGHT` | 桌宠在屏幕上的最大显示宽高（像素）；原图更大时等比缩小，像小宠物不占满屏 |

另：`resolve_random_mp4("feibi_sleep")` 仅在存在 `feibi_pet/picture/feibi_sleep.mp4` 时返回路径，用于随机动作的 MP4 分支。

图片目录常量：`PICTURE_DIR` 仅指向 **`feibi_pet/picture`**（唯一立绘目录）。

---

## 五、代码结构（便于二创）

| 路径 | 作用 |
|------|------|
| `main.py` | 启动 `QApplication`，创建窗口并设定初始位置 |
| `feibi_pet/config.py` | **包内** `picture` 路径解析与时间参数 |
| `feibi_pet/window.py` | 无边框置顶窗口、鼠标拖动、挂载调度器 |
| `feibi_pet/pet_widget.py` | 加载主图/随机图、拖放、吃文件与随机动效；若存在 mp4 则调用视频模块 |
| `feibi_pet/random_movement_mp4.py` | 随机动作 MP4：`QMediaPlayer` + `QVideoWidget`，仅读 `feibi_pet/picture/*.mp4` |
| `feibi_pet/actions.py` | 随机动作注册表与 `RandomActionScheduler` |

扩展随机动作、连接 `file_dropped` 的写法见各文件**中文注释**与上文表格。

---

## 六、注意事项

- 角色与《鸣潮》素材版权归官方所有，请遵守官方二创与分发规范。
- 桌宠为 **Tool** 类型窗口，任务栏表现因系统而异；结束进程可用任务管理器或自行加托盘菜单。

---

## 七、版本说明

- **0.2.2**：新增 `feibi_pet/random_movement_mp4.py`，随机动作可播放 `feibi_sing` / `feibi_sleep` / `feibi_wake` 的 **MP4**（与静态图同目录，优先 MP4）。
- **0.2.1**：立绘仅使用 **`feibi_pet/picture`**（含主图与 sing/sleep/wake）；不在项目根另建 `picture/`；补充中文注释与本文。
- **0.2.0**：引入 sing/sleep/wake 随机动作与中文说明初版。
