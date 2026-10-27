import os
import logging
from models import db, Product, FAQ, User

logger = logging.getLogger('mysterymart.seed')

# At least 10 comprehensive, well-structured FAQs
SEED_FAQS = [
    {
        'category': 'Ordering & Unboxing',
        'question': 'How does MysteryMart work?',
        'answer': 'MysteryMart lets you select a themed category (such as Gadgets, Gaming, Fashion, or Stationery) and a price tier. Each curated box contains guaranteed items of equal or greater value than the box price, plus authentic surprise bonuses. Once your order is confirmed, our packaging team seals and dispatches your box with full tracking.'
    },
    {
        'category': 'Ordering & Unboxing',
        'question': 'What are guaranteed inclusions versus surprise items?',
        'answer': 'Every MysteryMart box has guaranteed inclusions clearly listed on the product details page before purchase (e.g., premium braided cable, tempered glass, mechanical keycaps). In addition to guaranteed essentials, each box contains mystery surprise items hand-picked from verified inventory batches.'
    },
    {
        'category': 'Ordering & Unboxing',
        'question': 'Can I return or exchange items from a mystery box?',
        'answer': 'Because mystery boxes feature surprise items, opened boxes cannot be returned for change of mind. However, if any guaranteed item arrives damaged, defective, or missing, our 100% Quality Guarantee provides an immediate replacement or store credit upon opening a support ticket.'
    },
    {
        'category': 'Shipping & Delivery',
        'question': 'How long does delivery take and how much does it cost?',
        'answer': 'Standard dispatch takes 24 hours, followed by 3-5 business days for delivery. Standard shipping is $9.99, and all orders over $99.00 qualify for completely Free Delivery across the contiguous United States.'
    },
    {
        'category': 'Shipping & Delivery',
        'question': 'How does delivery location weather impact my shipment?',
        'answer': 'MysteryMart monitors weather conditions along transit routes using our live weather forecast integration. During severe rain or snow storms, our logistics team adds secondary waterproof vacuum packaging to ensure your surprise box arrives in pristine condition.'
    },
    {
        'category': 'Payments & Security',
        'question': 'What payment methods do you support?',
        'answer': 'We support major simulated credit/debit cards (Visa, MasterCard, American Express), digital wallets, and Cash on Delivery in select zones. Note: During demonstration mode, all transactions use secure simulated payment processing—no real payment credentials are ever stored.'
    },
    {
        'category': 'Payments & Security',
        'question': 'Are the contents guaranteed to match the purchase value?',
        'answer': 'Yes! MysteryMart adheres strictly to authentic value standards. The retail market value of items inside each box is guaranteed to meet or exceed the purchase price. We never advertise inflated fictitious values or deceptive lottery jackpots.'
    },
    {
        'category': 'Support & Concierge',
        'question': 'How do I track an existing order?',
        'answer': 'You can track your order using the Order Confirmation link sent to your email, by viewing your Order History in your MysteryMart profile, or by typing your order number (e.g., MM-ORD-XXXXXXXX) into our floating AI Assistant widget.'
    },
    {
        'category': 'Support & Concierge',
        'question': 'How do I open a support ticket if I need help?',
        'answer': 'Visit our Support page or ask the floating AI Assistant on any page to open a ticket. You will receive a unique ticket reference code (such as MM-TKT-XXXXXX). You can verify and track your ticket resolution anytime using your ticket code and email.'
    },
    {
        'category': 'Technical & Error Codes',
        'question': 'What does custom error code 460 mean on MysteryMart?',
        'answer': 'HTTP 460 is an application-specific custom error code indicating an Unboxing Concurrency Exception. This occurs when two customers purchase the last remaining limited-edition box simultaneously. If you encounter 460, simply choose an alternative tier or refresh in 60 seconds.'
    },
    {
        'category': 'Technical & Error Codes',
        'question': 'What should I do if I see error 404, 429, or 500?',
        'answer': 'For 404 (Not Found), verify the URL or search our Shop catalog. For 429 (Too Many Requests), pause for 30 seconds before retrying. For 500 (Internal Server Error), our diagnostic monitoring alerts our team immediately; refresh the page or contact our AI concierge.'
    },
    {
        'category': 'Product Authenticity',
        'question': 'Are all products in MysteryMart demo boxes genuine?',
        'answer': 'All demo products displayed on MysteryMart are genuine brand-new items sourced from licensed distributors. Demo badges clearly denote demonstration test data for evaluation and platform demonstration.'
    }
]

# Rich Mystery Box Catalog (Demo Products across 6 categories)
SEED_PRODUCTS = [
    {
        'name': 'CyberTech Gadget Mystery Box',
        'category': 'Gadget Mystery Box',
        'price': 49.99,
        'image_url': '/static/images/gadget-box.svg',
        'stock': 45,
        'box_tier': 'Explorer Edition',
        'badge': 'Bestseller',
        'rating': 4.9,
        'review_count': 64,
        'guaranteed_inclusions': '65W GaN Fast Charger; High-Speed Braided USB-C Cable (2m); Magnetic Desktop Cable Organizer; Microfiber Screen Cleaning Kit',
        'description': 'Unleash your inner technophile with the CyberTech Gadget Mystery Box. Packed with cutting-edge desk accessories, high-efficiency charging gear, and smart utility tools. Every box includes 4 guaranteed tech essentials plus 2-3 surprise tech accessories.',
        'box_condition': 'Brand New & Factory Sealed',
        'delivery_info': 'Standard Delivery in 3-5 Business Days'
    },
    {
        'name': 'Pro Gamer Battlestation Mystery Box',
        'category': 'Gaming Mystery Box',
        'price': 79.99,
        'image_url': '/static/images/gaming-box.svg',
        'stock': 30,
        'box_tier': 'Competitive Pro Tier',
        'badge': 'Hot',
        'rating': 4.8,
        'review_count': 52,
        'guaranteed_inclusions': 'RGB Extended Desk Mousepad (900x400mm); Bungee Mouse Cable Holder; Doubleshot PBT Artisan Keycaps (Set of 4); Anti-Fatigue Ergonomic Wrist Rest',
        'description': 'Level up your gaming setup! The Gaming Mystery Box contains esports-grade peripherals, aesthetic setup enhancements, and surprise gaming collectibles. Guaranteed gear value exceeds purchase price.',
        'box_condition': 'Brand New & Factory Sealed',
        'delivery_info': 'Standard Delivery in 3-5 Business Days'
    },
    {
        'name': 'Artisan Japanese Stationery Mystery Box',
        'category': 'Stationery Mystery Box',
        'price': 29.99,
        'image_url': '/static/images/stationery-box.svg',
        'stock': 60,
        'box_tier': 'Creative Studio Edition',
        'badge': 'Staff Pick',
        'rating': 4.9,
        'review_count': 41,
        'guaranteed_inclusions': '160 GSM Dot-Grid Hardcover Journal; Archival Waterproof Fineliner Pens (3-pack); Pastel Washi Tape Rolls (Set of 5); Metal Bookmark with Tassel',
        'description': 'Indulge your creative mind with handpicked stationery delights. Includes premium fountain-pen friendly paper, precision drafting pens, and decorative embellishments imported from boutique paper crafters.',
        'box_condition': 'Brand New & Factory Sealed',
        'delivery_info': 'Standard Delivery in 3-5 Business Days'
    },
    {
        'name': 'Urban Streetwear & Accessories Mystery Box',
        'category': 'Fashion Mystery Box',
        'price': 69.99,
        'image_url': '/static/images/fashion-box.svg',
        'stock': 25,
        'box_tier': 'Trendsetter Edition',
        'badge': 'Limited Edition',
        'rating': 4.7,
        'review_count': 33,
        'guaranteed_inclusions': 'Heavyweight Embroidered Beanie; Canvas Crossbody Utility Sling Bag; Hypoallergenic Stainless Steel Chain Necklace; Premium Crew Socks (2 Pairs)',
        'description': 'Curated aesthetic streetwear delivered straight to your door. Each box features contemporary minimalist fashion accessories and lifestyle wearables designed to elevate your everyday outfit.',
        'box_condition': 'Brand New & Factory Sealed',
        'delivery_info': 'Standard Delivery in 3-5 Business Days'
    },
    {
        'name': 'Glow & Glam Beauty Mystery Box',
        'category': 'Beauty & Accessories Mystery Box',
        'price': 44.99,
        'image_url': '/static/images/beauty-box.svg',
        'stock': 40,
        'box_tier': 'Self-Care Ritual Edition',
        'badge': 'Popular',
        'rating': 4.8,
        'review_count': 49,
        'guaranteed_inclusions': 'Rose Quartz Facial Roller & Gua Sha Set; Botanical Hydrating Sheet Masks (5-pack); Silk Satin Hair Scrunchies (Pack of 3); Nourishing Lip Treatment Balm',
        'description': 'The ultimate pampering experience! Discover clean skincare and wellness essentials crafted to rejuvenate and glow. Dermatologist-tested, cruelty-free beauty treats with guaranteed satisfaction.',
        'box_condition': 'Brand New & Factory Sealed',
        'delivery_info': 'Standard Delivery in 3-5 Business Days'
    },
    {
        'name': 'The Sovereign VIP Premium Mystery Box',
        'category': 'Premium Mystery Box',
        'price': 199.99,
        'image_url': '/static/images/premium-box.svg',
        'stock': 15,
        'box_tier': 'Elite Luxury Tier',
        'badge': 'Exclusive',
        'rating': 5.0,
        'review_count': 28,
        'guaranteed_inclusions': 'Active Noise-Cancelling Wireless Earbuds; RFID-Blocking Top-Grain Leather Cardholder; Precision Titanium Pocket Multitool; Engraved MysteryMart VIP Commemorative Coin',
        'description': 'The pinnacle of the mystery box experience. The Sovereign VIP Box features luxury EDC essentials, high-fidelity wireless audio, and exclusive collector memorabilia. Hand-packed in a custom matte magnetic gift case.',
        'box_condition': 'Brand New & Factory Sealed with Holographic Seal',
        'delivery_info': 'Express Insured Delivery in 2-3 Business Days'
    },
    {
        'name': 'Retro Arcade & Pop Culture Mystery Box',
        'category': 'Gaming Mystery Box',
        'price': 54.99,
        'image_url': '/static/images/gaming-box.svg',
        'stock': 35,
        'box_tier': 'Nostalgia Edition',
        'badge': 'Retro',
        'rating': 4.8,
        'review_count': 37,
        'guaranteed_inclusions': 'Mini Handheld 8-Bit Console (500 built-in games); Pixel Art Enamel Pin Set; Retro Arcade Keyring; Vintage Sound FX Soundboard',
        'description': 'Step back into the golden age of 80s and 90s arcades! Jam-packed with nostalgic retro tech, pixel collectibles, and gaming memorabilia that will bring a smile to any collector.',
        'box_condition': 'Brand New & Factory Sealed',
        'delivery_info': 'Standard Delivery in 3-5 Business Days'
    },
    {
        'name': 'Executive Minimalist Desk Mystery Box',
        'category': 'Gadget Mystery Box',
        'price': 64.99,
        'image_url': '/static/images/gadget-box.svg',
        'stock': 28,
        'box_tier': 'Productivity Edition',
        'badge': 'New',
        'rating': 4.9,
        'review_count': 21,
        'guaranteed_inclusions': 'Aluminum Laptop Riser Stand; Wireless Qi Fast Charging Mat; Weighted Metal Desk Pen with Stand; Cable Sleeve Management Kit',
        'description': 'Upgrade your work-from-home productivity. Engineered for professionals who appreciate clean lines, sleek anodized aluminum, and clutter-free desk spaces.',
        'box_condition': 'Brand New & Factory Sealed',
        'delivery_info': 'Standard Delivery in 3-5 Business Days'
    }
]


def seed_database():
    """Seed SQL database with FAQs, Products, and Demo Admin/Customer users."""
    logger.info("Starting database seeding...")

    # Seed FAQs
    if FAQ.query.count() < 10:
        logger.info("Seeding FAQs into SQL database...")
        for faq_data in SEED_FAQS:
            existing = FAQ.query.filter_by(question=faq_data['question']).first()
            if not existing:
                faq = FAQ(**faq_data)
                db.session.add(faq)
        db.session.commit()
        logger.info("Seeded %d FAQs.", FAQ.query.count())
    else:
        logger.info("FAQs already exist (%d records). Skipping.", FAQ.query.count())

    # Seed Products
    if Product.query.count() == 0:
        logger.info("Seeding Products into SQL database...")
        for prod_data in SEED_PRODUCTS:
            product = Product(**prod_data)
            db.session.add(product)
        db.session.commit()
        logger.info("Seeded %d Products.", Product.query.count())
    else:
        logger.info("Products already exist (%d records). Skipping.", Product.query.count())

    # Seed Demo Users
    if User.query.count() == 0:
        logger.info("Seeding Demo Users...")
        demo_customer = User(
            username='demouser',
            email='demo@mysterymart.com',
            role='customer'
        )
        demo_customer.set_password('MysteryMart2026!')
        db.session.add(demo_customer)

        demo_admin = User(
            username='admin',
            email='admin@mysterymart.com',
            role='admin'
        )
        demo_admin.set_password('AdminSecret2026!')
        db.session.add(demo_admin)

        db.session.commit()
        logger.info("Seeded Demo Users: demouser, admin.")

    logger.info("Database seeding completed successfully.")


if __name__ == '__main__':
    from app import create_app
    app = create_app('development')
    with app.app_context():
        db.create_all()
        seed_database()
        print(f"Database seeded successfully! FAQs: {FAQ.query.count()}, Products: {Product.query.count()}, Users: {User.query.count()}")
