from datetime import datetime
from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime


class Record(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str]
    origin: Mapped[str]
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __tablename__  = "alchelper_record"
