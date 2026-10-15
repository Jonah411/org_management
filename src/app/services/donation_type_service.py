from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.app.models.donation_type import DonationType
from src.app.schemas.donation_type import (
    DonationTypeCreate,
    DonationTypeUpdate,
)
from src.app.repositories import donation_type_repository as repository
from src.app.core.exceptions import (
    DonationTypeNotFoundException,
    DonationTypeAlreadyExistsException,
    DonationTypeValidationException,
)


def create_donation_type(
    db: Session,
    data: DonationTypeCreate,
    admin_user_id: UUID,
) -> DonationType:
    name = data.name.strip()

    if repository.get_donation_type_by_name(db, name):
        raise DonationTypeAlreadyExistsException(
            f"Donation type '{name}' already exists"
        )

    payload = data.model_dump()
    payload["name"] = name
    payload["created_by"] = admin_user_id

    try:
        return repository.create_donation_type(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise DonationTypeAlreadyExistsException(
            f"Donation type '{name}' already exists"
        ) from exc


def get_donation_type(
    db: Session,
    donation_type_id: UUID,
) -> DonationType:
    donation_type = repository.get_donation_type_by_id(
        db,
        donation_type_id,
    )

    if donation_type is None:
        raise DonationTypeNotFoundException()

    return donation_type


def get_all_donation_types(
    db: Session,
    active_only: bool = False,
) -> list[DonationType]:
    return repository.get_all_donation_types(
        db,
        active_only=active_only,
    )


def update_donation_type(
    db: Session,
    donation_type_id: UUID,
    data: DonationTypeUpdate,
) -> DonationType:
    donation_type = get_donation_type(db, donation_type_id)

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise DonationTypeValidationException(
            "Provide at least one field to update"
        )

    if "name" in update_data:
        name = update_data["name"]

        if name is None:
            raise DonationTypeValidationException(
                "Donation type name cannot be null"
            )

        name = name.strip()

        existing = repository.get_donation_type_by_name(db, name)

        if existing and existing.id != donation_type_id:
            raise DonationTypeAlreadyExistsException(
                f"Donation type '{name}' already exists"
            )

        update_data["name"] = name

    try:
        return repository.update_donation_type(
            db,
            donation_type,
            update_data,
        )
    except IntegrityError as exc:
        db.rollback()
        raise DonationTypeAlreadyExistsException(
            "Donation type name already exists"
        ) from exc


def deactivate_donation_type(
    db: Session,
    donation_type_id: UUID,
) -> DonationType:
    donation_type = get_donation_type(db, donation_type_id)

    if not donation_type.is_active:
        raise DonationTypeValidationException(
            "Donation type is already inactive"
        )

    return repository.deactivate_donation_type(
        db,
        donation_type,
    )