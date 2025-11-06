from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from ..db import db

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        nullable=True, 
        default=None
    )
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"), nullable=True)
    goal: Mapped[Optional["Goal"]] = relationship("Goal", back_populates="tasks")

    @classmethod
    def from_dict(cls, task_data):
        new_task = Task(title=task_data["title"],
                        description=task_data["description"])
        return new_task
    
    def to_dict(self):
        task_as_dict = {}
        task_as_dict["id"] = self.id
        task_as_dict["title"] = self.title
        task_as_dict["description"] = self.description
        task_as_dict["is_complete"] = self.completed_at is not None

        if getattr(self, "goal_id", None) is not None:
            task_as_dict["goal_id"] = self.goal_id

        return task_as_dict

    @classmethod
    def get_by_id(cls, task_id):
        task = db.session.get(cls, task_id)
        
        if task is None:
            return {"message": f"Task with ID {task_id} not found"}, 404
        return task, 200