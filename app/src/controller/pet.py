from fastapi import APIRouter, status, Request, HTTPException
from repository import pet as repository
router = APIRouter()


@router.get('/pets', status_code=status.HTTP_200_OK)
async def get_pets(request: Request):
    return repository.Pet(request.app.state.postgresql).get_pets()


@router.get('/pet/{pet_id}', status_code=status.HTTP_200_OK)
async def get_pet(request: Request, pet_id: int):
    pet = repository.Pet(request.app.state.postgresql).get_pet_by_id(pet_id)
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Pet not found')
    return {
        'pet': pet,
        'pet_habitat': repository.PetHabitat(request.app.state.postgresql).get_pet_habitat_by_pet_id(pet_id)
    }
