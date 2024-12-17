import json
from typing import List
import cloudinary
from beanie import PydanticObjectId, WriteRules
from cloudinary import uploader
import cloudinary.uploader
from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form,
                     HTTPException, UploadFile, status)
from authentication import AuthHandler
from config import BaseConfig
from models import Car, UpdateCar, User
from background import create_description

auth_handler = AuthHandler()
settings = BaseConfig()
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET_KEY,
)
router = APIRouter()


@router.get("/", response_model=List[Car])
async def get_cars():
    return await Car.find_all().to_list()


@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: PydanticObjectId):
    car = await Car.get(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.post(
    "/",
    response_description="Add new car with picture",
    response_model=Car,
    status_code=status.HTTP_201_CREATED,
)
async def add_car_with_picture(
    background_tasks: BackgroundTasks,
    brand: str = Form('brand'),
    make: str = Form('make'),
    year: int = Form('year'),
    cm3: int = Form('cm3'),
    km: int = Form('km'),
    price: int = Form('price'),
    picture: UploadFile = File('picture'),
    user_data=Depends(auth_handler.auth_wrapper),
):
    cloudinary_image = cloudinary.uploader.upload(
        picture.file,
        folder="FARM2",
        crop="fill",
        width=800,
        gravity="auto"
    )
    picture_url = cloudinary_image['url']
    print(picture_url)
    print(user_data)
    json_user_data = json.loads(user_data)
    user = await User.get(json_user_data["user_id"])

    car = Car(
        brand=brand,
        make=make,
        year=year,
        cm3=cm3,
        km=km,
        price=price,
        picture_url=picture_url,
        user=user,
    )
    background_tasks.add_task(
        create_description, brand=brand, make=make, year=year, picture_url=picture_url
    )
    return await car.insert(link_rule=WriteRules.WRITE)


@router.put("/{car_id}", response_model=Car)
async def update_car(
    car_id: PydanticObjectId,
    car_data: UpdateCar
):
    car = await Car.get(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    updated_car = {
        k: v for k, v in car_data.model_dump().items() if v is not None
    }
    return await car.set(updated_car)


@router.delete("/{car_id}")
async def delete_car(car_id: PydanticObjectId):
    car = await Car.get(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    await car.delete()
