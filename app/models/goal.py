from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")

    @classmethod
    def from_dict(cls, goal_data):
        new_goal = Goal(title=goal_data["title"])
        return new_goal
    
    def to_dict(self):
        goal_as_dict = {}
        goal_as_dict["id"] = self.id
        goal_as_dict["title"] = self.title

        return goal_as_dict

