"""Corpus generation and database seeding script.
Generates a ~50-image dataset across multiple categories and seeds initial posts.
"""
import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.database import init_db, get_db
from app.services.job_worker import create_batch_job, run_batch_ingest_worker

# 50 Corpus image definitions
CORPUS_SPECS = [
    # Canines: Red Fox (5)
    {"filename": "red_fox_01.jpg", "color": (218, 85, 38), "label": "Red Fox (Vulpes vulpes)\nAutumn Forest"},
    {"filename": "red_fox_02.jpg", "color": (205, 75, 30), "label": "Red Fox Hunting\nSnow Meadow"},
    {"filename": "red_fox_03.jpg", "color": (230, 95, 45), "label": "Red Fox Close-up\nOrange Fur"},
    {"filename": "red_fox_04.jpg", "color": (210, 80, 35), "label": "Red Fox Kit\nWoodland Den"},
    {"filename": "red_fox_05.jpg", "color": (195, 70, 25), "label": "Vulpine Wild Fox\nTwilight Forest"},

    # Canines: Fennec Fox (3)
    {"filename": "fennec_fox_01.jpg", "color": (235, 205, 140), "label": "Fennec Fox (Vulpes zerda)\nDesert Dunes"},
    {"filename": "fennec_fox_02.jpg", "color": (240, 215, 155), "label": "Fennec Fox Large Ears\nSahara Sand"},
    {"filename": "fennec_fox_03.jpg", "color": (225, 195, 130), "label": "Desert Fox Kit\nNocturnal Habitat"},

    # Canines: Gray Wolf (5)
    {"filename": "gray_wolf_01.jpg", "color": (120, 125, 130), "label": "Gray Wolf (Canis lupus)\nSnowy Mountain"},
    {"filename": "gray_wolf_02.jpg", "color": (100, 105, 110), "label": "Timber Wolf Pack Leader\nPine Forest"},
    {"filename": "gray_wolf_03.jpg", "color": (140, 145, 150), "label": "Gray Wolf Howling\nWinter Twilight"},
    {"filename": "gray_wolf_04.jpg", "color": (90, 95, 100), "label": "Arctic Gray Wolf\nTundra Habitat"},
    {"filename": "gray_wolf_05.jpg", "color": (110, 115, 120), "label": "Wild Wolf Predator\nRock Outcrop"},

    # Canines: Domestic Dog (4)
    {"filename": "golden_retriever_01.jpg", "color": (220, 180, 100), "label": "Golden Retriever Dog\nSunny Park Lawn"},
    {"filename": "golden_retriever_02.jpg", "color": (230, 190, 110), "label": "Golden Retriever Puppy\nDomestic Pet"},
    {"filename": "golden_retriever_03.jpg", "color": (210, 170, 90), "label": "Domestic Dog Playing Fetch\nBackyard"},
    {"filename": "golden_retriever_04.jpg", "color": (225, 185, 105), "label": "Family Dog Collar\nGrass Field"},

    # Ursids: Grizzly Bear (4)
    {"filename": "grizzly_bear_01.jpg", "color": (105, 65, 40), "label": "Grizzly Brown Bear\nSalmon River Rapids"},
    {"filename": "grizzly_bear_02.jpg", "color": (95, 55, 30), "label": "Grizzly Bear Claws\nAlaskan Stream"},
    {"filename": "grizzly_bear_03.jpg", "color": (115, 75, 45), "label": "Ursus arctos Foraging\nAlpine Meadow"},
    {"filename": "grizzly_bear_04.jpg", "color": (85, 50, 25), "label": "Coastal Brown Bear\nForest Edge"},

    # Ursids: Polar Bear (3)
    {"filename": "polar_bear_01.jpg", "color": (230, 240, 245), "label": "Polar Bear (Ursus maritimus)\nArctic Sea Ice"},
    {"filename": "polar_bear_02.jpg", "color": (220, 235, 240), "label": "Polar Bear Swimming\nGlacial Waters"},
    {"filename": "polar_bear_03.jpg", "color": (240, 245, 250), "label": "Mother Polar Bear and Cub\nSnowbank"},

    # Ursids: Giant Panda (3)
    {"filename": "giant_panda_01.jpg", "color": (60, 60, 60), "label": "Giant Panda (Ailuropoda)\nEating Fresh Bamboo"},
    {"filename": "giant_panda_02.jpg", "color": (50, 50, 50), "label": "Panda Bear Sitting\nBamboo Forest"},
    {"filename": "giant_panda_03.jpg", "color": (70, 70, 70), "label": "Giant Panda Sanctuary\nConservation Park"},

    # Cervids: White-tailed Deer (4)
    {"filename": "white_tailed_deer_01.jpg", "color": (160, 110, 70), "label": "White-tailed Deer Buck\nMorning Meadow"},
    {"filename": "white_tailed_deer_02.jpg", "color": (150, 100, 60), "label": "Whitetail Doe and Fawn\nDeciduous Forest"},
    {"filename": "white_tailed_deer_03.jpg", "color": (170, 120, 80), "label": "Antlered Buck Grazing\nSunlit Clearing"},
    {"filename": "white_tailed_deer_04.jpg", "color": (140, 95, 55), "label": "Wild Deer Foraging\nWoodland Trail"},

    # Cervids: Elk / Moose (3)
    {"filename": "elk_01.jpg", "color": (130, 85, 50), "label": "Bull Elk (Cervus canadensis)\nBugling in Valley"},
    {"filename": "elk_02.jpg", "color": (120, 75, 40), "label": "Elk Herd Grazing\nRocky Mountain Park"},
    {"filename": "elk_03.jpg", "color": (110, 70, 35), "label": "Large Antlered Elk\nAutumn Grassland"},

    # Felines: African Lion (3)
    {"filename": "african_lion_01.jpg", "color": (210, 160, 75), "label": "African Male Lion (Panthera leo)\nSavannah Plains"},
    {"filename": "african_lion_02.jpg", "color": (200, 150, 65), "label": "Lion Pride Resting\nGolden Grassland"},
    {"filename": "african_lion_03.jpg", "color": (220, 170, 85), "label": "Lion Mane Portrait\nSerengeti National Park"},

    # Felines: Bengal Tiger (3)
    {"filename": "bengal_tiger_01.jpg", "color": (225, 115, 35), "label": "Bengal Tiger (Panthera tigris)\nJungle Grass"},
    {"filename": "bengal_tiger_02.jpg", "color": (215, 105, 25), "label": "Tiger Stalking Prey\nRainforest Stream"},
    {"filename": "bengal_tiger_03.jpg", "color": (235, 125, 45), "label": "Striped Bengal Tiger\nMangrove Forest"},

    # Birds: Bald Eagle (3)
    {"filename": "bald_eagle_01.jpg", "color": (70, 50, 40), "label": "Bald Eagle (Haliaeetus)\nPerched on Pine Branch"},
    {"filename": "bald_eagle_02.jpg", "color": (60, 45, 35), "label": "Raptor White Head\nGlacial River View"},
    {"filename": "bald_eagle_03.jpg", "color": (80, 55, 45), "label": "American Eagle In Flight\nBlue Sky"},

    # Birds: Barn Owl (3)
    {"filename": "barn_owl_01.jpg", "color": (200, 175, 145), "label": "Barn Owl (Tyto alba)\nPerched in Barn Loft"},
    {"filename": "barn_owl_02.jpg", "color": (190, 165, 135), "label": "Heart-shaped Face Owl\nNight Woodland"},
    {"filename": "barn_owl_03.jpg", "color": (210, 185, 155), "label": "Nocturnal Owl Flight\nTwilight Field"},

    # Landscapes & Tech (4)
    {"filename": "mountain_landscape_01.jpg", "color": (70, 130, 180), "label": "Alpine Mountain Peak\nCrystal Glacier Lake"},
    {"filename": "mountain_landscape_02.jpg", "color": (60, 120, 170), "label": "Rugged Mountain Range\nPine Tree Valley"},
    {"filename": "technology_datacenter_01.jpg", "color": (30, 45, 80), "label": "Enterprise Datacenter\nServer Racks & Blue LEDs"},
    {"filename": "technology_datacenter_02.jpg", "color": (25, 40, 75), "label": "Cloud Infrastructure\nNetwork Switch Cables"},

    # Low-Confidence & Ambiguous Test Fixtures (2)
    {"filename": "blurry_unknown_canine_01.jpg", "color": (130, 130, 130), "label": "BLURRY / AMBIGUOUS\nIndistinct Low-Light Animal (Conf < 0.70)"},
    {"filename": "ambiguous_silhouette_02.jpg", "color": (90, 90, 90), "label": "AMBIGUOUS SILHOUETTE\nUnclear Shape in Dense Fog (Conf < 0.70)"}
]

# Seed Blog Posts
SEED_POSTS = [
    {
        "id": "post_red_fox_behavior",
        "title": "The Fascinating Behavior of Red Foxes in Temperate Forests",
        "slug": "the-fascinating-behavior-of-red-foxes",
        "content": "Red foxes (Vulpes vulpes) are remarkably adaptable canines found across woodlands and forest ecosystems. With their signature orange fur, bushy white-tipped tail, and sharp hunting instincts, wild fox species thrive in diverse habitats.",
        "target_category": "animal",
        "target_subject": "red fox"
    },
    {
        "id": "post_gray_wolf_packs",
        "title": "Wild Wolves: The Social Structure of Gray Wolf Packs",
        "slug": "wild-wolves-social-structure-of-gray-wolf-packs",
        "content": "Gray wolves (Canis lupus) are apex pack predators that roam extensive wilderness territories in North America and Eurasia. Their pack hierarchy and coordinated hunting strategies represent one of the most sophisticated social structures in nature.",
        "target_category": "animal",
        "target_subject": "gray wolf"
    },
    {
        "id": "post_golden_retriever_care",
        "title": "A Complete Guide to Caring for Your Golden Retriever",
        "slug": "guide-to-caring-for-golden-retriever",
        "content": "Golden retrievers are beloved domestic dogs renowned for their friendly demeanor, loyalty, and affectionate family bond. Providing regular outdoor exercise and grooming keeps your golden canine healthy and happy.",
        "target_category": "animal",
        "target_subject": "domestic dog"
    },
    {
        "id": "post_polar_bear_sea_ice",
        "title": "Polar Bears and the Melting Arctic Sea Ice",
        "slug": "polar-bears-arctic-sea-ice",
        "content": "Polar bears (Ursus maritimus) depend directly on frozen sea ice floes in the Arctic to hunt seals and raise their young cubs. As climate change reduces ice coverage, their marine habitat faces critical challenges.",
        "target_category": "animal",
        "target_subject": "polar bear"
    },
    {
        "id": "post_grizzly_bear_salmon",
        "title": "Grizzly Bears: The Annual Salmon Run in Mountain Rivers",
        "slug": "grizzly-bears-annual-salmon-run",
        "content": "Every summer, massive grizzly brown bears (Ursus arctos) congregate along rushing Alaskan and Canadian river rapids to catch migrating wild salmon, building fat reserves before winter hibernation.",
        "target_category": "animal",
        "target_subject": "grizzly bear"
    },
    {
        "id": "post_giant_panda_conservation",
        "title": "Protecting the Giant Panda: Bamboo Forests and Sanctuaries",
        "slug": "protecting-giant-panda-bamboo-forests",
        "content": "The giant panda is an iconic conservation symbol native to mountainous bamboo forests of central China. Conservation programs have successfully expanded protected reserves to secure their future.",
        "target_category": "animal",
        "target_subject": "giant panda"
    },
    {
        "id": "post_white_tailed_deer_meadow",
        "title": "White-Tailed Deer Habitats Across North American Meadows",
        "slug": "white-tailed-deer-habitats",
        "content": "White-tailed deer are graceful cervids commonly seen grazing at dawn in grassy meadows and forest edges. The distinctive white underside of their tail flashes as a warning signal when startled.",
        "target_category": "animal",
        "target_subject": "white-tailed deer"
    },
    {
        "id": "post_bengal_tiger_jungle",
        "title": "The Elusive Bengal Tiger: Apex Predator of the Mangrove Forests",
        "slug": "elusive-bengal-tiger-apex-predator",
        "content": "Bengal tigers (Panthera tigris) are stealthy feline predators with striking orange and black striped camouflage that allows them to stalk silently through dense tropical jungles and grasslands.",
        "target_category": "animal",
        "target_subject": "bengal tiger"
    },
    {
        "id": "post_cloud_datacenter_tech",
        "title": "Architecting Scalable Cloud Infrastructure in Modern Datacenters",
        "slug": "architecting-cloud-infrastructure-datacenters",
        "content": "Modern enterprise cloud data centers house thousands of high-density server racks connected by high-speed fiber optic cables and cooling infrastructure to deliver 99.999% uptime for global services.",
        "target_category": "technology",
        "target_subject": "server rack datacenter"
    },
    {
        "id": "post_quantum_algorithms_out_of_domain",
        "title": "Theoretical Foundations of Quantum Algorithms and Superconducting Qubits",
        "slug": "quantum-algorithms-superconducting-qubits",
        "content": "Quantum computing harnesses superposition and entanglement to execute Shor and Grover algorithms across superconducting qubit hardware matrices.",
        "target_category": "science",
        "target_subject": "quantum physics"
    }
]

def generate_image_file(filepath: Path, color: tuple, label: str):
    """Generates a high-quality visual test image with readable label overlay."""
    img = Image.new("RGB", (640, 480), color=color)
    draw = ImageDraw.Draw(img)
    
    # Draw geometric backdrop pattern
    for i in range(0, 640, 40):
        draw.line([(i, 0), (i, 480)], fill=(color[0] + 15, color[1] + 15, color[2] + 15), width=1)
    for j in range(0, 480, 40):
        draw.line([(0, j), (640, j)], fill=(color[0] + 15, color[1] + 15, color[2] + 15), width=1)
        
    # Draw central banner
    draw.rectangle([(40, 160), (600, 320)], fill=(20, 24, 33, 230), outline=(255, 255, 255), width=2)
    
    # Draw text
    draw.text((60, 190), label, fill=(255, 255, 255))
    draw.text((60, 280), f"File: {filepath.name} | Licensed Free Asset", fill=(180, 200, 220))
    
    img.save(filepath, "JPEG", quality=90)

def seed_all():
    """Generates images, seeds posts, and executes batch ingestion."""
    print("=== Step 1: Initializing Database Schema ===")
    init_db()
    
    print("\n=== Step 2: Generating 50-Image Corpus ===")
    settings.CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    generated_paths = []
    
    for spec in CORPUS_SPECS:
        path = settings.CORPUS_DIR / spec["filename"]
        generate_image_file(path, spec["color"], spec["label"])
        generated_paths.append(path)
        
    print(f"Generated {len(generated_paths)} image fixtures in {settings.CORPUS_DIR}")
    
    print("\n=== Step 3: Seeding Blog Posts ===")
    with get_db() as conn:
        cursor = conn.cursor()
        for p in SEED_POSTS:
            cursor.execute(
                """
                INSERT OR REPLACE INTO posts (id, title, slug, content, target_category, target_subject, created_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (p["id"], p["title"], p["slug"], p["content"], p["target_category"], p["target_subject"])
            )
    print(f"Seeded {len(SEED_POSTS)} blog posts.")

    print("\n=== Step 4: Executing Batch Ingestion Job on Corpus ===")
    job_id = create_batch_job(job_type="batch_ingest", total_items=len(generated_paths))
    run_batch_ingest_worker(job_id, generated_paths)
    print(f"Batch ingestion completed for Job ID: {job_id}")

if __name__ == "__main__":
    seed_all()
