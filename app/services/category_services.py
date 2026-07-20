from app.schemas.category_schemas import CategoryResponse
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import category_repository
from app.core.redis import redis_client
from fastapi.encoders import jsonable_encoder

async def get_all_categories(db: AsyncSession):
    #step -1 -Check redis
    cached_categories = await redis_client.get('categories:all')
     # Step 2: If data is present in Redis, return it
    if cached_categories:
        return json.loads(cached_categories)

     # Step 3: If not present, get data from MySQL
    categories = await category_repository.get_category(db)

    category_data = [
    CategoryResponse.model_validate(category).model_dump()
    for category in categories
    ]
    json_data = jsonable_encoder(category_data)
    # Step 4: Store the data in Redis for 5 minutes
    await redis_client.set(
        'categories:all',
        json.dumps(json_data),
        ex=1800 # 5 minutes
    )

    return json_data