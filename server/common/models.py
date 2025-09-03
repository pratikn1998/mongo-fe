"""Pydantic Data models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from bson.decimal128 import Decimal128
from pydantic import BaseModel


class Decimal128Field:
    """Custom type for Decimal 128 type."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        yield cls.serialize

    @classmethod
    def validate(cls, v, field=None):
        if isinstance(v, Decimal128):
            return v
        if isinstance(v, dict) and "$numberDecimal" in v:
            return Decimal128(v["$numberDecimal"])
        if isinstance(v, (str, float, int, Decimal)):
            return Decimal128(str(v))
        print(v)
        raise TypeError("Value must be Decimal128, Decimal, str, int, or float")

    @classmethod
    def serialize(cls, v, field=None):
        if isinstance(v, Decimal128):
            return {"$numberDecimal": str(v.to_decimal())}
        return {"$numberDecimal": str(v)}
    
    
class BsonDateTimeField:
    """Custom type for Datetime field."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        yield cls.serialize

    @classmethod
    def validate(cls, v, field=None):
        # Already datetime
        if isinstance(v, datetime):
            return v
        # Extended JSON: {"$date": "..."}
        if isinstance(v, dict) and "$date" in v:
            return datetime.fromisoformat(v["$date"].replace("Z", "+00:00"))
        # Plain string
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        raise TypeError(f"{field.name if field else 'Value'} must be datetime or Extended JSON with $date")

    @classmethod
    def serialize(cls, v, field=None):
        if isinstance(v, datetime):
            return {"$date": v.isoformat().replace("+00:00", "Z")}
        return {"$date": str(v)}
    
    
class ReviewScores(BaseModel):
    """Model for review scores for an airbnb listing."""
    review_scores_accuracy: Optional[int]  = None
    review_scores_cleanliness: Optional[int]  = None
    review_scores_checkin: Optional[int] = None
    review_scores_communication: Optional[int] = None
    review_scores_location: Optional[int] = None
    review_scores_value: Optional[int] = None
    review_scores_rating: Optional[int] = None
      
      
class AirBnbListingRequest(BaseModel):
    """Model for an Airbnb listing."""
    id: str
    listing_url: str
    name: str
    summary: str
    space: str
    description: str
    neighborhood_overview: str
    notes: str
    transit: str
    access: Optional[str] = ""
    interaction: str
    house_rules: str
    property_type: str
    room_type: str
    bed_type: str
    minimum_nights: str
    maximum_nights: str
    cancellation_policy: str = "flexible"
    last_scraped: BsonDateTimeField
    calendar_last_scraped: BsonDateTimeField
    accommodates: int
    bedrooms: int
    beds: int
    number_of_reviews: int
    bathrooms: Decimal128Field
    amenities: list = []
    price: Decimal128Field
    weekly_price: Optional[Decimal128Field] = None
    monthly_price: Optional[Decimal128Field] = None
    cleaning_fee: Optional[Decimal128Field] = None
    extra_people: Decimal128Field
    guests_included: Decimal128Field
    images: dict
    host: dict
    address: dict
    availability: dict
    review_scores: Optional[ReviewScores] = None
    reviews: Optional[list]  = []
    first_review: Optional[BsonDateTimeField] = None
    last_review: Optional[BsonDateTimeField] = None
    security_deposit: Optional[Decimal128Field] = None
    
    
class AirBnbListingUpdate(BaseModel):
    """Model for updating a document in Airbnb listings."""
    name: Optional[str] = None
    amenities: list = []
    cleaning_fee: Optional[Decimal128Field] = None
    monthly_price: Optional[Decimal128Field] = None
    weekly_price: Optional[BsonDateTimeField] = None
    reviews: Optional[list]  = []
    review_scores: Optional[ReviewScores] = {}


class BatchEmbedRequest(BaseModel):
    """Batch embeddings API request."""
    batch_size: Optional[int] = 50
    
    
class SearchRequest(BaseModel):
    user_query: str