import asyncio
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("/{member_id}/run")
async def run_quote(
    member_id: int,
    db: Session = Depends(get_db),
):
    from agent.runner import run_insurance_agent
    member = db.query(models.FamilyMember).filter(
        models.FamilyMember.id == member_id
    ).first()

    if not member or not member.vehicles:
        return RedirectResponse(
            url=f"/profiles/{member_id}?error=no_vehicle",
            status_code=303
        )

    try:
        result = await run_insurance_agent(member)
        # Clean any non-ASCII characters
        result = result.encode("utf-8", "ignore").decode("utf-8")
    except Exception as e:
        result = f"Error running quote: {str(e)}"

    quote = models.Quote(member_id=member_id, result=result)
    db.add(quote)
    db.commit()

    return RedirectResponse(
        url=f"/profiles/{member_id}",
        status_code=303
    )


@router.post("/{quote_id}/delete")
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(
        models.Quote.id == quote_id
    ).first()
    member_id = quote.member_id
    db.delete(quote)
    db.commit()
    return RedirectResponse(
        url=f"/profiles/{member_id}", status_code=303
    )
