from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.db.models.user import User
from app.schemas.purchases import PaymentProviderResponse, PurchaseCreateRequest, PurchaseResponse, TariffResponse
from app.services.exceptions import PaymentProviderError, PaymentProviderNotFoundError, PaymentTariffNotFoundError
from app.services.purchases import PurchaseService

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("/tariffs", response_model=list[TariffResponse])
async def list_tariffs(
        session: AsyncSession = Depends(get_db_session),
) -> list:
    purchase_service = PurchaseService(session)

    return await purchase_service.list_tariffs()


@router.get("/providers", response_model=list[PaymentProviderResponse])
async def list_payment_providers(
        session: AsyncSession = Depends(get_db_session),
) -> list:
    purchase_service = PurchaseService(session)
    return await purchase_service.list_payment_providers()


@router.post("/yookassa/webhook")
async def handle_yookassa_webhook(
        payload: dict = Body(...),
        session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    async with session.begin():
        purchase_service = PurchaseService(session)
        await purchase_service.handle_yookassa_webhook(payload)

    return {"status": "ok"}


@router.post("", response_model=PurchaseResponse)
async def create_purchase(
        request: PurchaseCreateRequest,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
):
    try:
        async with session.begin():
            purchase_service = PurchaseService(session)
            purchase = await purchase_service.create_purchase(
                telegram_id=current_user.telegram_id,
                tariff_id=request.tariff_id,
                provider=request.provider,
            )
            return purchase
    except PaymentTariffNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff not found",
        )
    except PaymentProviderError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider error",
        )
    except PaymentProviderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment provider not found",
        )


@router.get("", response_model=list[PurchaseResponse])
async def list_purchases(
        limit: int = 20,
        offset: int = 0,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session),
):
    purchase_service = PurchaseService(session)

    return await purchase_service.list_user_purchases(
        telegram_id=current_user.telegram_id,
        limit=limit,
        offset=offset,
    )
