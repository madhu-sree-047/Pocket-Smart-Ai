from urllib.parse import quote_plus
from app.models.schemas import BudgetAllocation, HomeRequest, JewelryRequest, PartyRequest, RecommendationItem, RecommendationResponse

def search_url(platform: str, query: str) -> str:
    q = quote_plus(query)
    urls = {
        "Amazon": f"https://www.amazon.in/s?k={q}",
        "Flipkart": f"https://www.flipkart.com/search?q={q}",
        "IKEA": f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy": f"https://www.swiggy.com/search?query={q}",
        "Zomato": f"https://www.zomato.com/search?query={q}",
        "OYO": f"https://www.oyorooms.com/search?q={q}",
    }
    return urls.get(platform, f"https://www.google.com/search?q={q}")

def home_fallback(req: HomeRequest) -> RecommendationResponse:
    budget = req.budget
    names = req.items or ["ceiling light", "area rug", "wall art", "side table"]
    platforms = ["IKEA", "Amazon", "Flipkart", "IKEA"]
    allocations = [BudgetAllocation(category="Furniture", amount=budget*.40, percentage=40), BudgetAllocation(category="Lighting", amount=budget*.20, percentage=20), BudgetAllocation(category="Decor", amount=budget*.25, percentage=25), BudgetAllocation(category="Contingency", amount=budget*.15, percentage=15)]
    each = max(1, int((budget * .85) / len(names)))
    items = [RecommendationItem(name=n.title(), category="Home", estimated_price=each, platform=platforms[i % len(platforms)], url=search_url(platforms[i % len(platforms)], n), why_it_fits=f"A {req.style} option for a {req.room_type} that keeps the plan within budget.", quantity=max(1, req.quantities.get(n, 1))) for i,n in enumerate(names)]
    total = sum(x.estimated_price*x.quantity for x in items)
    return RecommendationResponse(title=f"{req.style.title()} {req.room_type.title()} plan", summary="A starter home-interior plan generated from the requested budget and preferences.", total_estimated_cost=total, budget_remaining=budget-total, allocations=allocations, recommendations=items, tips=["Compare dimensions before buying.", "Reserve part of the budget for delivery and installation.", "Buy large furniture only after confirming room measurements."], source="fallback")

def party_fallback(req: PartyRequest) -> RecommendationResponse:
    budget = req.budget
    allocs = [BudgetAllocation(category="Food", amount=budget*.45, percentage=45), BudgetAllocation(category="Venue", amount=budget*.25, percentage=25), BudgetAllocation(category="Decoration", amount=budget*.15, percentage=15), BudgetAllocation(category="Entertainment", amount=budget*.10, percentage=10), BudgetAllocation(category="Buffer", amount=budget*.05, percentage=5)]
    concepts = [("Food package", "Food", "Swiggy"), ("Restaurant catering", "Food", "Zomato"), ("Event venue", "Venue", "OYO"), ("Party decoration", "Decoration", "Amazon"), ("Tableware", "Decoration", "Flipkart")]
    items=[]
    for name,cat,platform in concepts:
        price = budget*{"Food":.18,"Venue":.22,"Decoration":.07}.get(cat,.05)
        items.append(RecommendationItem(name=name, category=cat, estimated_price=round(price,2), platform=platform, url=search_url(platform, f"{req.event_type} {name}"), why_it_fits=f"Scales with {req.guests} guests and the {req.event_type} format."))
    total=sum(x.estimated_price for x in items)
    return RecommendationResponse(title=f"{req.event_type.title()} plan for {req.guests} guests", summary="A balanced event budget with food, venue, decoration and buffer allocations.", total_estimated_cost=round(total,2), budget_remaining=round(budget-total,2), allocations=allocs, recommendations=items, tips=["Confirm per-person catering prices before booking.", "Keep a 5–10% contingency for last-minute needs.", "Ask venues what furniture and basic decoration are included."], source="fallback")

def jewelry_fallback(req: JewelryRequest) -> RecommendationResponse:
    budget=req.budget
    styles=[("Minimal pendant", "Amazon"), ("Stud earrings", "Flipkart"), ("Bracelet", "Amazon"), ("Statement earrings", "Flipkart")]
    items=[]
    for i,(name,platform) in enumerate(styles):
        price=budget*[.25,.18,.22,.30][i]
        items.append(RecommendationItem(name=name, category="Jewelry", estimated_price=round(price,2), platform=platform, url=search_url(platform, f"{req.style} {req.occasion} {req.metal_preference} {name}"), why_it_fits=f"Matches an {req.occasion} occasion and {req.style} style; use outfit color {req.outfit_color or 'as the visual reference' } when comparing options."))
    total=sum(x.estimated_price for x in items)
    return RecommendationResponse(title=f"{req.style.title()} jewelry shortlist", summary="A budget-conscious jewelry shortlist. An uploaded outfit image can be used by Gemini when enabled.", total_estimated_cost=round(total,2), budget_remaining=round(budget-total,2), allocations=[BudgetAllocation(category="Main piece",amount=budget*.45,percentage=45),BudgetAllocation(category="Earrings",amount=budget*.25,percentage=25),BudgetAllocation(category="Bracelet",amount=budget*.20,percentage=20),BudgetAllocation(category="Buffer",amount=budget*.10,percentage=10)], recommendations=items, tips=["Check metal purity, dimensions and return policy.", "Coordinate metal tone with other accessories.", "Treat generated prices as estimates until confirmed on the merchant site."], source="fallback")
