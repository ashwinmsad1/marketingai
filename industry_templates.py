"""
Industry-Specific Campaign Templates
Vertical-optimized templates for high-converting campaigns across different industries
"""

import asyncio
import json
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class CampaignTemplate:
    """Campaign template data structure"""
    template_id: str
    industry: str
    name: str
    description: str
    image_prompts: List[str]
    video_prompts: List[str]
    captions: List[str]
    hashtags: List[str]
    target_audience: Dict[str, Any]
    call_to_action: List[str]
    best_times: List[str]  # Best posting times
    expected_performance: Dict[str, float]

class IndustryType(Enum):
    RESTAURANT = "restaurant"
    REAL_ESTATE = "real_estate"
    FITNESS = "fitness"
    BEAUTY = "beauty"
    AUTOMOTIVE = "automotive"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    ECOMMERCE = "ecommerce"
    TECHNOLOGY = "technology"
    FASHION = "fashion"

class IndustryTemplateEngine:
    """
    System for generating industry-specific, high-converting campaign templates
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, List[CampaignTemplate]]:
        """Initialize all industry-specific templates"""
        return {
            IndustryType.RESTAURANT.value: self._create_restaurant_templates(),
            IndustryType.REAL_ESTATE.value: self._create_real_estate_templates(),
            IndustryType.FITNESS.value: self._create_fitness_templates(),
            IndustryType.BEAUTY.value: self._create_beauty_templates(),
            IndustryType.AUTOMOTIVE.value: self._create_automotive_templates(),
            IndustryType.EDUCATION.value: self._create_education_templates(),
            IndustryType.HEALTHCARE.value: self._create_healthcare_templates(),
            IndustryType.ECOMMERCE.value: self._create_ecommerce_templates(),
            IndustryType.TECHNOLOGY.value: self._create_technology_templates(),
            IndustryType.FASHION.value: self._create_fashion_templates(),
        }
    
    def _create_restaurant_templates(self) -> List[CampaignTemplate]:
        """Create restaurant industry templates"""
        return [
            CampaignTemplate(
                template_id="restaurant_signature_dish",
                industry="restaurant",
                name="Signature Dish Showcase",
                description="Highlight your restaurant's signature dish with mouth-watering visuals",
                image_prompts=[
                    "Hyperrealistic {signature_dish} with steam rising, professional food photography lighting, garnished perfectly on white plate",
                    "Close-up of {signature_dish} being prepared by chef hands, dramatic lighting, restaurant kitchen background",
                    "Elegant plating of {signature_dish} with wine pairing, upscale restaurant ambiance, warm lighting"
                ],
                video_prompts=[
                    "Cinematic slow-motion video of {signature_dish} being plated by chef, steam rising, professional kitchen",
                    "Time-lapse of {signature_dish} preparation from ingredients to final presentation",
                    "Customer enjoying {signature_dish} with satisfied expression, cozy restaurant atmosphere"
                ],
                captions=[
                    "🍽️ Our signature {signature_dish} - crafted with love, served with pride! Book your table now 📞 {phone}",
                    "👨‍🍳 Chef's special {signature_dish} - made fresh daily with premium ingredients! Order for pickup or delivery 🚗",
                    "🌟 Why settle for ordinary when you can have extraordinary? Try our famous {signature_dish} today! #ChefSpecial"
                ],
                hashtags=["#SignatureDish", "#ChefSpecial", "#FreshDaily", "#LocalFavorite", "#FoodieParadise", "#RestaurantLife"],
                target_audience={
                    "interests": ["fine dining", "local restaurants", "gourmet food", "foodie culture"],
                    "age_range": [25, 65],
                    "location": "local_area_5_miles",
                    "behaviors": ["frequent restaurant visitors", "food and dining"]
                },
                call_to_action=["Book Now", "Order Online", "Call for Reservations", "View Menu"],
                best_times=["11:30 AM", "5:30 PM", "7:00 PM", "Weekend 1:00 PM"],
                expected_performance={"ctr": 2.8, "conversion_rate": 12.5, "engagement_rate": 4.2}
            ),
            CampaignTemplate(
                template_id="restaurant_happy_hour",
                industry="restaurant",
                name="Happy Hour Special",
                description="Drive traffic during off-peak hours with irresistible happy hour deals",
                image_prompts=[
                    "Colorful cocktails and appetizers arranged on bar counter, happy hour atmosphere, warm lighting",
                    "Friends toasting with drinks, blurred restaurant background, golden hour lighting, celebration mood",
                    "Happy hour menu board with prices, appetizing food and drinks, inviting restaurant interior"
                ],
                video_prompts=[
                    "Bartender preparing signature cocktail, smooth pouring action, happy customers in background",
                    "Group of friends enjoying happy hour, laughing and toasting, lively restaurant atmosphere",
                    "Montage of happy hour specials - drinks, appetizers, satisfied customers"
                ],
                captions=[
                    "🍻 Happy Hour Alert! 50% off appetizers & $5 cocktails! Every weekday 3-6 PM 🕒",
                    "📣 Beat the crowd! Join us for Happy Hour - great food, better prices, best company! 🎉",
                    "🥂 Why wait for Friday? Make any day special with our Happy Hour deals! Weekdays 3-6 PM"
                ],
                hashtags=["#HappyHour", "#WeekdaySpecial", "#CheapEats", "#Cocktails", "#AfterWork", "#GreatDeals"],
                target_audience={
                    "interests": ["happy hour", "cocktails", "after work dining", "local bars"],
                    "age_range": [21, 55],
                    "location": "local_area_3_miles",
                    "behaviors": ["frequent bar visitors", "social dining"]
                },
                call_to_action=["Join Us Now", "See Menu", "Book Table", "Get Directions"],
                best_times=["2:00 PM", "4:30 PM", "Monday 10 AM"],
                expected_performance={"ctr": 3.2, "conversion_rate": 18.0, "engagement_rate": 5.1}
            )
        ]
    
    def _create_real_estate_templates(self) -> List[CampaignTemplate]:
        """Create real estate industry templates"""
        return [
            CampaignTemplate(
                template_id="real_estate_luxury_listing",
                industry="real_estate",
                name="Luxury Property Showcase",
                description="Showcase high-end properties with stunning visuals that attract qualified buyers",
                image_prompts=[
                    "Luxury home exterior with perfect landscaping, golden hour lighting, professional real estate photography",
                    "Modern kitchen with granite countertops, stainless appliances, natural lighting through large windows",
                    "Master bedroom suite with elegant furnishing, walk-in closet, spa-like bathroom visible"
                ],
                video_prompts=[
                    "Cinematic walkthrough of luxury home from entrance to backyard, smooth camera movement",
                    "Drone footage of property and neighborhood, showcasing location and surroundings",
                    "Lifestyle video of family enjoying home - cooking, relaxing, entertaining"
                ],
                captions=[
                    "🏡 JUST LISTED: Stunning {property_type} in {neighborhood}! {bedrooms} bed, {bathrooms} bath, {sqft} sq ft of luxury living 💎",
                    "✨ Your dream home awaits! Premium finishes, prime location, unbeatable value. Schedule your private showing today 📅",
                    "🌟 New to Market: {property_type} that checks every box! Don't let this one slip away. Call now {phone} 📞"
                ],
                hashtags=["#JustListed", "#LuxuryHomes", "#RealEstate", "#DreamHome", "#PrimeLocation", "#NewListing"],
                target_audience={
                    "interests": ["real estate", "home buying", "luxury homes", "interior design"],
                    "age_range": [28, 65],
                    "income": ["top 25%"],
                    "behaviors": ["home buyers", "recently moved", "real estate investors"]
                },
                call_to_action=["Schedule Showing", "Get Details", "Call Agent", "Virtual Tour"],
                best_times=["10:00 AM", "2:00 PM", "6:00 PM", "Sunday 11 AM"],
                expected_performance={"ctr": 2.1, "conversion_rate": 15.8, "engagement_rate": 3.4}
            )
        ]
    
    def _create_fitness_templates(self) -> List[CampaignTemplate]:
        """Create fitness industry templates"""
        return [
            CampaignTemplate(
                template_id="fitness_transformation",
                industry="fitness",
                name="Transformation Challenge",
                description="Motivate potential members with inspiring transformation stories and challenges",
                image_prompts=[
                    "Before and after transformation photos side by side, dramatic lighting, motivational atmosphere",
                    "Person working out intensely in gym, sweat glistening, determined expression, modern equipment",
                    "Group fitness class in action, energetic instructor, participants smiling and engaged"
                ],
                video_prompts=[
                    "High-energy workout montage with upbeat music, diverse people exercising, motivational mood",
                    "Personal trainer coaching client through workout, encouraging words, visible progress",
                    "Transformation story testimonial with before/after visuals, inspiring narrative"
                ],
                captions=[
                    "💪 Ready to transform your life? Join our 30-day challenge and see what you're capable of! First week FREE 🔥",
                    "🎯 Stop making excuses, start making changes! Our proven program gets results. Book your consultation today 📞",
                    "🏋️‍♂️ Your transformation starts now! Join hundreds who've already changed their lives. What's your excuse? 💯"
                ],
                hashtags=["#Transformation", "#FitnessChallenge", "#NoExcuses", "#ResultsDriven", "#NewYouStartsNow", "#FitLife"],
                target_audience={
                    "interests": ["fitness", "weight loss", "health and wellness", "gym membership"],
                    "age_range": [18, 55],
                    "behaviors": ["interested in fitness", "health conscious", "new year resolutions"]
                },
                call_to_action=["Start Challenge", "Book Consultation", "Join Now", "Free Trial"],
                best_times=["6:00 AM", "12:00 PM", "6:00 PM", "Sunday 9 AM"],
                expected_performance={"ctr": 3.1, "conversion_rate": 8.7, "engagement_rate": 6.2}
            )
        ]
    
    def _create_beauty_templates(self) -> List[CampaignTemplate]:
        """Create beauty industry templates"""
        return [
            CampaignTemplate(
                template_id="beauty_seasonal_special",
                industry="beauty",
                name="Seasonal Beauty Special",
                description="Promote seasonal beauty services and treatments",
                image_prompts=[
                    "Before and after beauty treatment results, glowing skin, professional salon lighting",
                    "Relaxing spa environment with candles, essential oils, peaceful atmosphere",
                    "Beauty professional performing treatment, client relaxed and pampered"
                ],
                video_prompts=[
                    "Relaxing spa treatment process, soothing music, peaceful ambiance",
                    "Quick beauty tip tutorial, professional demonstrating technique",
                    "Client testimonial about amazing results, genuine satisfaction"
                ],
                captions=[
                    "✨ Glow up for {season}! Our {treatment_name} will have you looking radiant. Book now and save 25% 💫",
                    "🌸 Treat yourself to the ultimate pampering experience! You deserve to feel beautiful inside and out 💆‍♀️",
                    "💅 New season, new you! Our expert team is ready to help you shine. Limited time offer - book today! ⏰"
                ],
                hashtags=["#GlowUp", "#BeautyTreatment", "#SelfCare", "#FeelBeautiful", "#SalonLife", "#PamperYourself"],
                target_audience={
                    "interests": ["beauty services", "spa treatments", "skincare", "self-care"],
                    "age_range": [16, 65],
                    "gender": "female_primary",
                    "behaviors": ["beauty enthusiasts", "spa and salon visitors"]
                },
                call_to_action=["Book Appointment", "Call Now", "View Services", "Special Offer"],
                best_times=["10:00 AM", "2:00 PM", "7:00 PM", "Saturday 11 AM"],
                expected_performance={"ctr": 3.8, "conversion_rate": 11.2, "engagement_rate": 5.9}
            )
        ]
    
    def _create_automotive_templates(self) -> List[CampaignTemplate]:
        """Create automotive industry templates"""
        return [
            CampaignTemplate(
                template_id="automotive_new_arrival",
                industry="automotive",
                name="New Model Showcase",
                description="Showcase new vehicle arrivals with compelling visuals and offers",
                image_prompts=[
                    "Sleek new car in showroom with dramatic lighting, pristine condition, luxury appeal",
                    "Car driving on scenic highway, motion blur background, freedom and adventure theme",
                    "Interior dashboard and features highlighted, modern technology, comfort focus"
                ],
                video_prompts=[
                    "Cinematic car reveal with dramatic lighting, 360-degree rotation, stunning details",
                    "Test drive experience, smooth ride, happy customer behind wheel",
                    "Feature walkthrough highlighting technology, safety, and comfort benefits"
                ],
                captions=[
                    "🚗 NEW ARRIVAL: The {car_model} has landed! Experience luxury, performance, and innovation. Test drive today! 🏁",
                    "✨ Introducing the future of driving! {car_model} with cutting-edge features and unbeatable value 💫",
                    "🎯 Limited time offer on the new {car_model}! Special financing available. Your dream car awaits! 🔑"
                ],
                hashtags=["#NewArrival", "#TestDriveToday", "#DreamCar", "#SpecialFinancing", "#CarDealer", "#NewCar"],
                target_audience={
                    "interests": ["car shopping", "new cars", "automotive", "car financing"],
                    "age_range": [25, 65],
                    "income": ["middle to upper income"],
                    "behaviors": ["car buyers", "automotive enthusiasts", "researching vehicles"]
                },
                call_to_action=["Schedule Test Drive", "Get Quote", "View Inventory", "Special Offer"],
                best_times=["10:00 AM", "2:00 PM", "6:00 PM", "Saturday 1 PM"],
                expected_performance={"ctr": 1.9, "conversion_rate": 22.5, "engagement_rate": 2.8}
            )
        ]
    
    def _create_education_templates(self) -> List[CampaignTemplate]:
        """Create education industry templates"""
        return [
            CampaignTemplate(
                template_id="education_course_enrollment",
                industry="education",
                name="Course Enrollment Drive",
                description="Drive enrollment for courses and educational programs",
                image_prompts=[
                    "Diverse students in modern classroom, engaged in learning, bright educational environment",
                    "Student success story - graduation, achievement, proud moment",
                    "Online learning setup with laptop, books, motivated student studying"
                ],
                video_prompts=[
                    "Student testimonial about course transformation, genuine success story",
                    "Quick course preview showing curriculum highlights and benefits",
                    "Day in the life of student - learning, growing, achieving goals"
                ],
                captions=[
                    "🎓 Transform your career with our {course_name}! 95% job placement rate. Enrollment open now 📚",
                    "💡 Invest in yourself! Our {course_name} program gives you skills employers want. Apply today 🚀",
                    "📈 Ready to level up? Join thousands who've advanced their careers with our proven {course_name} program ⭐"
                ],
                hashtags=["#CareerChange", "#LearnNewSkills", "#JobPlacement", "#OnlineLearning", "#SkillsDevelopment", "#FutureReady"],
                target_audience={
                    "interests": ["education", "career development", "online learning", "skill building"],
                    "age_range": [18, 45],
                    "behaviors": ["career focused", "continuous learners", "job seekers"]
                },
                call_to_action=["Enroll Now", "Learn More", "Free Preview", "Apply Today"],
                best_times=["9:00 AM", "1:00 PM", "7:00 PM", "Sunday 10 AM"],
                expected_performance={"ctr": 2.4, "conversion_rate": 16.8, "engagement_rate": 4.1}
            )
        ]
    
    def _create_healthcare_templates(self) -> List[CampaignTemplate]:
        """Create healthcare industry templates"""
        return [
            CampaignTemplate(
                template_id="healthcare_preventive_care",
                industry="healthcare",
                name="Preventive Care Campaign",
                description="Promote preventive healthcare services and wellness checks",
                image_prompts=[
                    "Caring doctor with patient, professional medical environment, trust and comfort",
                    "Modern medical facility, clean and welcoming, state-of-the-art equipment",
                    "Happy family after health checkup, peace of mind, wellness focus"
                ],
                video_prompts=[
                    "Doctor consultation showing care and professionalism, patient comfort focus",
                    "Medical facility tour highlighting advanced equipment and caring staff",
                    "Patient testimonial about excellent care and early detection benefits"
                ],
                captions=[
                    "🏥 Your health is your wealth! Schedule your annual wellness check today. Early detection saves lives 💙",
                    "👩‍⚕️ Trusted care when you need it most. Our experienced team is here for you and your family 🩺",
                    "💚 Prevention is the best medicine! Book your health screening now. Most insurance accepted ✅"
                ],
                hashtags=["#PreventiveCare", "#HealthFirst", "#WellnessCheck", "#EarlyDetection", "#TrustedCare", "#HealthyFamily"],
                target_audience={
                    "interests": ["healthcare", "wellness", "family health", "medical services"],
                    "age_range": [25, 75],
                    "behaviors": ["health conscious", "family oriented", "insurance users"]
                },
                call_to_action=["Book Appointment", "Call Today", "Schedule Online", "Learn More"],
                best_times=["9:00 AM", "11:00 AM", "2:00 PM", "Monday 8 AM"],
                expected_performance={"ctr": 1.6, "conversion_rate": 24.2, "engagement_rate": 3.2}
            )
        ]
    
    def _create_ecommerce_templates(self) -> List[CampaignTemplate]:
        """Create ecommerce industry templates"""
        return [
            CampaignTemplate(
                template_id="ecommerce_flash_sale",
                industry="ecommerce",
                name="Flash Sale Campaign",
                description="Drive urgency and sales with limited-time offers",
                image_prompts=[
                    "Product showcase with 'SALE' overlay, attractive pricing, limited time urgency",
                    "Happy customer unboxing product, satisfaction and delight, quality focus",
                    "Before and after using product, transformation or improvement shown"
                ],
                video_prompts=[
                    "Product demonstration showing key features and benefits, compelling use case",
                    "Customer unboxing experience, genuine excitement and satisfaction",
                    "Flash sale countdown timer with featured products, urgency and scarcity"
                ],
                captions=[
                    "🚨 FLASH SALE: 50% OFF everything! Limited time only - don't miss out! Shop now 🛒",
                    "⏰ 24 HOURS ONLY: Massive savings on our bestsellers! Free shipping on orders over $50 📦",
                    "🔥 FINAL HOURS: Last chance for these incredible deals! Sale ends at midnight ⭐"
                ],
                hashtags=["#FlashSale", "#LimitedTime", "#HugeSavings", "#ShopNow", "#LastChance", "#FreeShipping"],
                target_audience={
                    "interests": ["online shopping", "deals and coupons", "product category"],
                    "age_range": [18, 55],
                    "behaviors": ["online shoppers", "deal seekers", "frequent buyers"]
                },
                call_to_action=["Shop Now", "Get Deal", "Buy Now", "Limited Time"],
                best_times=["10:00 AM", "2:00 PM", "8:00 PM", "Friday 12 PM"],
                expected_performance={"ctr": 2.3, "conversion_rate": 6.8, "engagement_rate": 4.7}
            )
        ]
    
    def _create_technology_templates(self) -> List[CampaignTemplate]:
        """Create technology industry templates"""
        return [
            CampaignTemplate(
                template_id="tech_software_demo",
                industry="technology",
                name="Software Demo Campaign",
                description="Demonstrate software capabilities and drive trial signups",
                image_prompts=[
                    "Clean software interface on modern laptop, professional workspace, productivity focus",
                    "Team collaborating using software, efficiency and teamwork highlighted",
                    "Before/after comparison showing software impact, results-driven"
                ],
                video_prompts=[
                    "Screen recording demo showing key software features, smooth workflow",
                    "Customer success story using software, measurable business impact",
                    "Quick tutorial highlighting main benefits and ease of use"
                ],
                captions=[
                    "🚀 Boost productivity by 40%! See how {software_name} transforms your workflow. Free trial available 💻",
                    "⚡ Stop wasting time on manual tasks! {software_name} automates everything. Try it free for 14 days 🎯",
                    "📈 Join 10,000+ companies already saving time and money with {software_name}. Start your free trial! ✨"
                ],
                hashtags=["#ProductivityBoost", "#FreeTrial", "#WorkflowAutomation", "#BusinessGrowth", "#SoftwareSolution", "#EfficiencyTools"],
                target_audience={
                    "interests": ["business software", "productivity tools", "automation", "technology"],
                    "age_range": [25, 55],
                    "behaviors": ["business decision makers", "software users", "tech adoption"]
                },
                call_to_action=["Start Free Trial", "Request Demo", "Learn More", "Get Started"],
                best_times=["9:00 AM", "1:00 PM", "3:00 PM", "Tuesday 10 AM"],
                expected_performance={"ctr": 2.7, "conversion_rate": 12.3, "engagement_rate": 3.9}
            )
        ]
    
    def _create_fashion_templates(self) -> List[CampaignTemplate]:
        """Create fashion industry templates"""
        return [
            CampaignTemplate(
                template_id="fashion_new_collection",
                industry="fashion",
                name="New Collection Launch",
                description="Showcase new fashion collections with style and appeal",
                image_prompts=[
                    "Model wearing new collection item, professional fashion photography, stylish pose",
                    "Flat lay of outfit coordination, trendy styling, Instagram-worthy aesthetic",
                    "Street style photo wearing collection piece, natural confidence, urban backdrop"
                ],
                video_prompts=[
                    "Fashion show style video of model wearing pieces, confident walk, music",
                    "Styling tutorial showing how to wear collection pieces, practical fashion tips",
                    "Behind-the-scenes of photoshoot, creative process, brand authenticity"
                ],
                captions=[
                    "✨ NEW DROP: Our {collection_name} is here! Limited quantities available. Shop before it's gone 👗",
                    "💫 Elevate your style with our latest {collection_name}! Trendy pieces for every occasion 🛍️",
                    "🔥 Fresh styles just landed! {collection_name} - where comfort meets chic. Free shipping over $75 📦"
                ],
                hashtags=["#NewDrop", "#FashionForward", "#StyleInspo", "#LimitedEdition", "#TrendingNow", "#FashionLover"],
                target_audience={
                    "interests": ["fashion", "style", "clothing shopping", "trends"],
                    "age_range": [16, 45],
                    "gender": "female_primary",
                    "behaviors": ["fashion shoppers", "trend followers", "brand conscious"]
                },
                call_to_action=["Shop Collection", "Get Look", "Browse Styles", "Limited Stock"],
                best_times=["11:00 AM", "3:00 PM", "7:00 PM", "Saturday 2 PM"],
                expected_performance={"ctr": 3.4, "conversion_rate": 5.9, "engagement_rate": 7.1}
            )
        ]
    
    async def get_templates_by_industry(self, industry: str) -> List[CampaignTemplate]:
        """Get all templates for specific industry"""
        return self.templates.get(industry, [])
    
    async def get_template_by_id(self, template_id: str) -> Optional[CampaignTemplate]:
        """Get specific template by ID"""
        for industry_templates in self.templates.values():
            for template in industry_templates:
                if template.template_id == template_id:
                    return template
        return None
    
    async def customize_template(self, template_id: str, customizations: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Customize template with specific business details"""
        template = await self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Apply customizations
        customized = {
            'template_id': template.template_id,
            'industry': template.industry,
            'name': template.name,
            'description': template.description,
            'customized_prompts': [],
            'customized_captions': [],
            'target_audience': template.target_audience,
            'call_to_action': template.call_to_action,
            'expected_performance': template.expected_performance
        }
        
        # Customize image prompts
        for prompt in template.image_prompts:
            customized_prompt = prompt
            for key, value in customizations.items():
                customized_prompt = customized_prompt.replace(f'{{{key}}}', str(value))
            customized['customized_prompts'].append(customized_prompt)
        
        # Customize captions
        for caption in template.captions:
            customized_caption = caption
            for key, value in customizations.items():
                customized_caption = customized_caption.replace(f'{{{key}}}', str(value))
            customized['customized_captions'].append(customized_caption)
        
        return customized
    
    async def generate_campaign_from_template(self, template_id: str, 
                                            customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete campaign from template"""
        customized_template = await self.customize_template(template_id, customizations)
        if not customized_template:
            return {'success': False, 'error': 'Template not found'}
        
        # Select random variations for campaign
        selected_prompt = random.choice(customized_template['customized_prompts'])
        selected_caption = random.choice(customized_template['customized_captions'])
        selected_cta = random.choice(customized_template['call_to_action'])
        
        return {
            'success': True,
            'campaign_config': {
                'template_id': template_id,
                'industry': customized_template['industry'],
                'image_prompt': selected_prompt,
                'caption': selected_caption,
                'call_to_action': selected_cta,
                'target_audience': customized_template['target_audience'],
                'expected_performance': customized_template['expected_performance']
            }
        }
    
    async def get_all_industries(self) -> List[str]:
        """Get list of all available industries"""
        return list(self.templates.keys())
    
    async def search_templates(self, query: str) -> List[CampaignTemplate]:
        """Search templates by keyword"""
        results = []
        query_lower = query.lower()
        
        for industry_templates in self.templates.values():
            for template in industry_templates:
                if (query_lower in template.name.lower() or 
                    query_lower in template.description.lower() or
                    query_lower in template.industry.lower()):
                    results.append(template)
        
        return results

# Helper functions for easy integration
async def get_restaurant_templates():
    """Quick access to restaurant templates"""
    engine = IndustryTemplateEngine()
    return await engine.get_templates_by_industry('restaurant')

async def get_template(template_id: str):
    """Quick template lookup"""
    engine = IndustryTemplateEngine()
    return await engine.get_template_by_id(template_id)

async def create_custom_campaign(template_id: str, business_details: Dict[str, Any]):
    """Quick campaign generation from template"""
    engine = IndustryTemplateEngine()
    return await engine.generate_campaign_from_template(template_id, business_details)

async def main():
    """Test the industry template system"""
    print("🏭 Industry-Specific Campaign Templates")
    print("=" * 45)
    
    engine = IndustryTemplateEngine()
    
    # Demo: List all industries
    industries = await engine.get_all_industries()
    print(f"📋 Available Industries: {', '.join(industries)}")
    
    # Demo: Get restaurant templates
    restaurant_templates = await engine.get_templates_by_industry('restaurant')
    print(f"\n🍽️  Restaurant Templates ({len(restaurant_templates)}):")
    for template in restaurant_templates:
        print(f"  • {template.name}: {template.description}")
    
    # Demo: Customize template
    customizations = {
        'signature_dish': 'Lobster Risotto',
        'phone': '(555) 123-4567'
    }
    
    campaign = await engine.generate_campaign_from_template(
        'restaurant_signature_dish', 
        customizations
    )
    
    print(f"\n🎯 Generated Campaign:")
    print(json.dumps(campaign, indent=2))
    
    # Demo: Search templates
    search_results = await engine.search_templates('special')
    print(f"\n🔍 Templates matching 'special': {len(search_results)}")
    for result in search_results:
        print(f"  • {result.industry}: {result.name}")

if __name__ == "__main__":
    asyncio.run(main())