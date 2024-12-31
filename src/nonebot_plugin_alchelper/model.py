from datetime import datetime
from dataclasses import dataclass
from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime


@dataclass
class Record(Model):
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True, unique=True)
    source: Mapped[str] = mapped_column()
    origin: Mapped[str] = mapped_column()
    sender: Mapped[str] = mapped_column()
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __tablename__  = "alchelper_record"
