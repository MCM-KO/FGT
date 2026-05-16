"""随机调度器"""
import random
import time
from dataclasses import dataclass
from typing import Callable
from PySide6.QtCore import QObject, QTimer

#类似于接口
Run = Callable[["Pet"], None]

#冻结数据的自动化类（类似一个map）
"""之所以不用map，是采取类的形式可拓展性极强，map局限性明显"""
@dataclass(frozen=True)
class Action:
    name: str
    run: Run


class RandTimer(QObject):
    def __init__(
        self,
        pet: "Pet",#存储桌宠实例
        *,
        tick_ms: int,#定时器
        chance: float,#概率器
        cooldown_ms: int,#冷静器
        acts: list[Action],#动作列表
    ) -> None:
        super().__init__(pet)
        self._pet = pet
        self._chance = chance
        self._cd = cooldown_ms
        self._acts = list(acts)
        self._last_end = 0
        self._last_pick: str | None = None
        self._t = QTimer(self)#定时任务调度器
        self._t.setInterval(tick_ms)
        self._t.timeout.connect(self._tick)


    def start(self) -> None:
        """开启定时任务调度器"""
        self._t.start()


    def stop(self) -> None:
        """关闭定时任务调度器"""
        self._t.stop()


    def mark_done(self) -> None:
        """一段动作完成，标志冷静器介入"""
        self._last_end = int(time.monotonic() * 1000)#计算时间戳（精度极高），用于间隔判断


    def _tick(self) -> None:
        """随机触发器"""
        #若表情正在播放，则直接返回
        if not self._acts or self._pet.is_busy():
            return
        now = int(time.monotonic() * 1000)
        #不然则返回
        if now - self._last_end < self._cd:
            return
        """生成随机数"""
        if random.random() > self._chance:
            return
        pool = self._acts
        if len(self._acts) > 1 and self._last_pick:
            alt = [a for a in self._acts if a.name != self._last_pick]
            if alt:
                pool = alt
        a = random.choice(pool)
        self._last_pick = a.name
        self._pet.begin_external_action(a.name)
        a.run(self._pet)


def default_acts() -> list[Action]:
    return [
        Action("sing", lambda p: p.play_sing()),
        Action("sleep", lambda p: p.play_sleep()),
        Action("sleep_2", lambda p: p.play_sleep_2()),
        Action("wake", lambda p: p.play_wake()),
    ]
