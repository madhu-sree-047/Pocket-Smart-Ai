import json
from typing import Any
from pydantic import BaseModel
from app.config import get_settings
from app.models.schemas import HomeRequest, PartyRequest, JewelryRequest, RecommendationResponse
from app.services.recommendations import home_fallback, party_fallback, jewelry_fallback

class GeminiService:
    def __init__(self):
        s=get_settings(); self.settings=s
        self.client=None
        self.types=None
        if s.gemini_enabled and s.gemini_api_key:
            try:
                from google import genai
                from google.genai import types
                self.client=genai.Client(api_key=s.gemini_api_key)
                self.types=types
            except ImportError:
                self.client=None

    def _generate(self, prompt: str, image: tuple[bytes,str] | None = None) -> RecommendationResponse:
        if not self.client:
            raise RuntimeError("Gemini is not configured")
        contents: list[Any] = [prompt]
        if image:
            data,mime=image
            contents.append(self.types.Part.from_bytes(data=data, mime_type=mime))
        response=self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=contents,
            config=self.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RecommendationResponse.model_json_schema(),
                temperature=0.4,
            ),
        )
        return RecommendationResponse.model_validate_json(response.text)

    def home(self, req: HomeRequest) -> RecommendationResponse:
        prompt=f"""You are PocketSmart AI's home interior budget planner. Create practical, budget-aware recommendations for India. Never claim live inventory or exact current prices. Use estimated prices and search links. Budget INR {req.budget}. Room: {req.room_type}. Style: {req.style}. Items: {req.items}. Quantities: {req.quantities}. Notes: {req.notes}. Return only JSON matching the supplied schema. Keep total estimated cost at or below the budget whenever possible. Platforms should be Amazon, Flipkart, or IKEA."""
        try: r=self._generate(prompt); r.source="gemini"; return r
        except Exception: return home_fallback(req)

    def party(self, req: PartyRequest) -> RecommendationResponse:
        prompt=f"""You are PocketSmart AI's party budget planner for India. Build a practical event plan. Budget INR {req.budget}; guests {req.guests}; event {req.event_type}; venue {req.venue}; city {req.city}; food preference {req.food_preference}; notes {req.notes}. Use estimated prices, never claim live availability, and use merchant search links. Platforms may include Swiggy, Zomato, OYO, Amazon and Flipkart. Return only the supplied JSON schema and keep total estimated cost within budget."""
        try: r=self._generate(prompt); r.source="gemini"; return r
        except Exception: return party_fallback(req)

    def jewelry(self, req: JewelryRequest, image: tuple[bytes,str] | None = None) -> RecommendationResponse:
        prompt=f"""You are PocketSmart AI's jewelry stylist. Recommend jewelry within INR {req.budget} for occasion {req.occasion}, style {req.style}, outfit color {req.outfit_color}, metal preference {req.metal_preference}, notes {req.notes}. If an image is supplied, use it only to describe visible color/style coordination; do not infer sensitive traits. Use estimated prices and merchant search links. Platforms may include Amazon and Flipkart. Return only the supplied JSON schema and keep total estimated cost within budget."""
        try: r=self._generate(prompt,image); r.source="gemini"; return r
        except Exception: return jewelry_fallback(req)
