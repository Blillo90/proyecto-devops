from sqlalchemy.orm import Session
from . import models, schemas

# -------- USERS --------

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip=0, limit=100):
    return db.query(models.User).offset(skip).limit(limit).all()


# -------- TICKETS --------

def create_ticket(db: Session, ticket: schemas.TicketCreate):
    db_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        owner_id=ticket.owner_id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()


def get_tickets(db: Session, skip=0, limit=100):
    return db.query(models.Ticket).offset(skip).limit(limit).all()


def update_ticket(db: Session, ticket_id: int, ticket: schemas.TicketUpdate):
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None

    updates = ticket.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(db_ticket, key, value)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def delete_ticket(db: Session, ticket_id: int):
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None

    db.delete(db_ticket)
    db.commit()
    return db_ticket
