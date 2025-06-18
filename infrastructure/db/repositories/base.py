from typing import Generic, TypeVar, Type, List, Optional

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: int) -> Optional[T]:
        """Получение по первичному ключу."""
        return self.session.get(self.model, id)

    def list_all(self) -> List[T]:
        """Список всех записей."""
        return self.session.query(self.model).all()

    def add(self, instance: T) -> T:
        """Добавить и сразу зафиксировать."""
        self.session.add(instance)
        self.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        """Удалить и зафиксировать."""
        self.session.delete(instance)
        self.session.commit()
