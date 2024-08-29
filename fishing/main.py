import asyncio
import random
import time
import discord 
from redbot.core import Config, commands
from redbot.core.bot import Red

fishes = {
    "🐟 Salmon": {"rarity": 3, "weight_range": (2, 15), "price_per_lb": 10},
    "🐟 Tuna": {"rarity": 3, "weight_range": (3, 20), "price_per_lb": 15},
    "🐟 Trout": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 8},
    "🐟 Bass": {"rarity": 3, "weight_range": (2, 10), "price_per_lb": 12},
    "🐟 Catfish": {"rarity": 3, "weight_range": (5, 30), "price_per_lb": 14},
    "🐟 Mackerel": {"rarity": 3, "weight_range": (1, 4), "price_per_lb": 6},
    "🐟 Cod": {"rarity": 3, "weight_range": (3, 12), "price_per_lb": 10},
    "🐟 Sardine": {"rarity": 3, "weight_range": (0.1, 0.5), "price_per_lb": 5},
    "🐟 Grouper": {"rarity": 2, "weight_range": (5, 40), "price_per_lb": 18},
    "🐟 Snapper": {"rarity": 2, "weight_range": (2, 8), "price_per_lb": 14},
    "🐠 Swordfish": {"rarity": 1, "weight_range": (10, 70), "price_per_lb": 30},
    "🐟 Haddock": {"rarity": 3, "weight_range": (1, 3), "price_per_lb": 8},
    "🐟 Perch": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 7},
    "🐟 Herring": {"rarity": 3, "weight_range": (0.2, 1), "price_per_lb": 6},
    "🐟 Halibut": {"rarity": 2, "weight_range": (20, 200), "price_per_lb": 25},
    "🐟 Pike": {"rarity": 3, "weight_range": (3, 15), "price_per_lb": 12},
    "🐟 Carp": {"rarity": 3, "weight_range": (1, 10), "price_per_lb": 9},
    "🐠 Mahi Mahi": {"rarity": 1, "weight_range": (5, 30), "price_per_lb": 28},
    "🐟 Flounder": {"rarity": 2, "weight_range": (1, 10), "price_per_lb": 10},
    "🐟 Anchovy": {"rarity": 3, "weight_range": (0.05, 0.2), "price_per_lb": 4},
    "🐟 Rainbow Trout": {"rarity": 3, "weight_range": (1, 3), "price_per_lb": 8},
    "🐟 Whitefish": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 10},
    "🐟 Mullet": {"rarity": 3, "weight_range": (2, 7), "price_per_lb": 9},
    "🐟 Sole": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 8},
    "🐟 Redfish": {"rarity": 2, "weight_range": (2, 12), "price_per_lb": 14},
    "🐟 Bluefish": {"rarity": 2, "weight_range": (2, 15), "price_per_lb": 16},
    "🐟 Barracuda": {"rarity": 1, "weight_range": (5, 25), "price_per_lb": 22},
    "🐠 Marlin": {"rarity": 1, "weight_range": (20, 70), "price_per_lb": 35},
    "🐟 Yellowfin Tuna": {"rarity": 1, "weight_range": (30, 100), "price_per_lb": 40},
    "🐟 Kingfish": {"rarity": 2, "weight_range": (5, 50), "price_per_lb": 20},
    "🐠 Bonito": {"rarity": 2, "weight_range": (2, 12), "price_per_lb": 14},
    "🐟 Tilapia": {"rarity": 3, "weight_range": (1, 4), "price_per_lb": 6},
    "🐠 Clownfish": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 50},
    "🐟 Lionfish": {"rarity": 2, "weight_range": (1, 3), "price_per_lb": 25},
    "🐡 Pufferfish": {"rarity": 2, "weight_range": (0.5, 3.5), "price_per_lb": 1000},
    "🐟 Goby": {"rarity": 3, "weight_range": (0.1, 0.5), "price_per_lb": 15},
    "🐟 Tarpon": {"rarity": 2, "weight_range": (10, 50), "price_per_lb": 20},
    "🐠 Wahoo": {"rarity": 1, "weight_range": (10, 40), "price_per_lb": 35},
    "🐟 Blue Marlin": {"rarity": 1, "weight_range": (30, 70), "price_per_lb": 40},
    "🐟 Bonefish": {"rarity": 3, "weight_range": (2, 8), "price_per_lb": 18},
    "🐟 Sturgeon": {"rarity": 1, "weight_range": (20, 200), "price_per_lb": 50},
    "🐟 Zander": {"rarity": 2, "weight_range": (5, 15), "price_per_lb": 15},
    "🐟 Arctic Char": {"rarity": 2, "weight_range": (2, 10), "price_per_lb": 18},
    "🐠 Barramundi": {"rarity": 2, "weight_range": (5, 30), "price_per_lb": 25},
    "🐟 Black Drum": {"rarity": 2, "weight_range": (10, 50), "price_per_lb": 22},
    "🐟 Sheepshead": {"rarity": 3, "weight_range": (2, 10), "price_per_lb": 14},
    "🐟 Tautog": {"rarity": 2, "weight_range": (3, 15), "price_per_lb": 16},
    "🐟 Weakfish": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 10},
    "🐠 Moonfish": {"rarity": 4, "weight_range": (0.5, 2), "price_per_lb": 30},
    "🐠 Catla": {"rarity": 2, "weight_range": (5, 40), "price_per_lb": 20},
    "🐟 Emperor Angelfish": {"rarity": 3, "weight_range": (0.5, 1.5), "price_per_lb": 30},
    "🐠 Parrotfish": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 18},
    "🐠 Triggerfish": {"rarity": 3, "weight_range": (2, 6), "price_per_lb": 20},
    "🐟 Wrasse": {"rarity": 3, "weight_range": (1, 2), "price_per_lb": 12},
    "🐠 Damselfish": {"rarity": 3, "weight_range": (1, 2), "price_per_lb": 15},
    "🐟 Betta": {"rarity": 4, "weight_range": (1, 3), "price_per_lb": 50},
    "🐠 Koi": {"rarity": 4, "weight_range": (1, 10), "price_per_lb": 40},
    "🐟 Dragonfish": {"rarity": 1, "weight_range": (5, 20), "price_per_lb": 45},
    "🐟 Electric Eel": {"rarity": 2, "weight_range": (3, 15), "price_per_lb": 25},
    "🐠 Discus": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 30},
    "🐠 Swordtail": {"rarity": 3, "weight_range": (0.2, 0.8), "price_per_lb": 15},
    "🐟 Salmon": {"rarity": 3, "weight_range": (2, 15), "price_per_lb": 10},
    "🐟 Tuna": {"rarity": 3, "weight_range": (3, 20), "price_per_lb": 15},
    "🐟 Trout": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 8},
    "🐟 Bass": {"rarity": 3, "weight_range": (2, 10), "price_per_lb": 12},
    "🐟 Catfish": {"rarity": 3, "weight_range": (5, 30), "price_per_lb": 14},
    "🐟 Mackerel": {"rarity": 3, "weight_range": (1, 4), "price_per_lb": 6},
    "🐟 Cod": {"rarity": 3, "weight_range": (3, 12), "price_per_lb": 10},
    "🐟 Sardine": {"rarity": 3, "weight_range": (0.1, 0.5), "price_per_lb": 5},
    "🦈 Shark": {"rarity": 1, "weight_range": (50, 150), "price_per_lb": 40},
    "🐠 Swordfish": {"rarity": 1, "weight_range": (10, 70), "price_per_lb": 30},
    "🐟 Haddock": {"rarity": 3, "weight_range": (1, 3), "price_per_lb": 8},
    "🐠 Perch": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 7},
    "🐠 Herring": {"rarity": 3, "weight_range": (0.2, 1), "price_per_lb": 6},
    "🐟 Halibut": {"rarity": 2, "weight_range": (20, 200), "price_per_lb": 25},
    "🐟 Pike": {"rarity": 3, "weight_range": (3, 15), "price_per_lb": 12},
    "🐟 Carp": {"rarity": 3, "weight_range": (1, 10), "price_per_lb": 9},
    "🐠 Mahi Mahi": {"rarity": 1, "weight_range": (5, 30), "price_per_lb": 28},
    "🐟 Flounder": {"rarity": 2, "weight_range": (1, 10), "price_per_lb": 10},
    "🐟 Anchovy": {"rarity": 3, "weight_range": (0.05, 0.2), "price_per_lb": 4},
    "🐟 Rainbow Trout": {"rarity": 3, "weight_range": (1, 3), "price_per_lb": 8},
    "🐟 Whitefish": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 10},
    "🐟 Mullet": {"rarity": 3, "weight_range": (2, 7), "price_per_lb": 9},
    "🐟 Sole": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 8},
    "🐠 Redfish": {"rarity": 2, "weight_range": (2, 12), "price_per_lb": 14},
    "🐠 Bluefish": {"rarity": 2, "weight_range": (2, 15), "price_per_lb": 16},
    "🐟 Barracuda": {"rarity": 1, "weight_range": (5, 25), "price_per_lb": 22},
    "🐠 Marlin": {"rarity": 1, "weight_range": (20, 70), "price_per_lb": 35},
    "🐟 Yellowfin Tuna": {"rarity": 1, "weight_range": (30, 100), "price_per_lb": 40},
    "🐟 Kingfish": {"rarity": 2, "weight_range": (5, 50), "price_per_lb": 20},
    "🐟 Bonito": {"rarity": 2, "weight_range": (2, 12), "price_per_lb": 14},
    "🐟 Tilapia": {"rarity": 3, "weight_range": (1, 4), "price_per_lb": 6},
    "🐠 Clownfish": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 50},
    "🐟 Lionfish": {"rarity": 2, "weight_range": (1, 3), "price_per_lb": 25},
    "🐟 Pufferfish": {"rarity": 2, "weight_range": (0.5, 1.5), "price_per_lb": 30},
    "🐟 Goby": {"rarity": 3, "weight_range": (0.1, 0.5), "price_per_lb": 15},
    "🐟 Tarpon": {"rarity": 2, "weight_range": (10, 50), "price_per_lb": 20},
    "🐠 Wahoo": {"rarity": 1, "weight_range": (10, 40), "price_per_lb": 35},
    "🐠 Blue Marlin": {"rarity": 1, "weight_range": (30, 70), "price_per_lb": 40},
    "🐟 Bonefish": {"rarity": 3, "weight_range": (2, 8), "price_per_lb": 18},
    "🐟 Sturgeon": {"rarity": 1, "weight_range": (20, 200), "price_per_lb": 50},
    "🐠 Zander": {"rarity": 2, "weight_range": (5, 15), "price_per_lb": 15},
    "🐟 Arctic Char": {"rarity": 2, "weight_range": (2, 10), "price_per_lb": 18},
    "🐠 Barramundi": {"rarity": 2, "weight_range": (5, 30), "price_per_lb": 25},
    "🐟 Black Drum": {"rarity": 2, "weight_range": (10, 50), "price_per_lb": 22},
    "🐟 Sheepshead": {"rarity": 3, "weight_range": (2, 10), "price_per_lb": 14},
    "🐠 Tautog": {"rarity": 2, "weight_range": (3, 15), "price_per_lb": 16},
    "🐟 Weakfish": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 10},
    "🐠 Moonfish": {"rarity": 4, "weight_range": (0.5, 2), "price_per_lb": 30},
    "🐟 Catla": {"rarity": 2, "weight_range": (5, 40), "price_per_lb": 20},
    "🐠 Emperor Angelfish": {"rarity": 3, "weight_range": (0.5, 1.5), "price_per_lb": 30},
    "🐠 Parrotfish": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 18},
    "🐠 Triggerfish": {"rarity": 3, "weight_range": (2, 6), "price_per_lb": 20},
    "🐟 Wrasse": {"rarity": 3, "weight_range": (1, 2), "price_per_lb": 12},
    "🐠 Damselfish": {"rarity": 3, "weight_range": (1, 2), "price_per_lb": 15},
    "🐠 Betta": {"rarity": 4, "weight_range": (1, 3), "price_per_lb": 50},
    "🐟 Koi": {"rarity": 4, "weight_range": (1, 10), "price_per_lb": 40},
    "🐠 Dragonfish": {"rarity": 1, "weight_range": (5, 20), "price_per_lb": 45},
    "🐟 Electric Eel": {"rarity": 2, "weight_range": (3, 15), "price_per_lb": 25},
    "🐠 Discus": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 30},
    "🐠 Swordtail": {"rarity": 3, "weight_range": (0.2, 0.8), "price_per_lb": 15},
    "🐟 Grunt": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 7},
    "🐠 Ladyfish": {"rarity": 3, "weight_range": (1, 4), "price_per_lb": 10},
    "🐟 Hogfish": {"rarity": 2, "weight_range": (2, 8), "price_per_lb": 15},
    "🐠 Needlefish": {"rarity": 3, "weight_range": (0.5, 1.5), "price_per_lb": 8},
    "🐟 Scad": {"rarity": 3, "weight_range": (0.5, 2), "price_per_lb": 9},
    "🐠 Mahi Mahi (Dorado)": {"rarity": 1, "weight_range": (5, 30), "price_per_lb": 25},
    "🐟 Amberjack": {"rarity": 2, "weight_range": (10, 50), "price_per_lb": 18},
    "🐠 Pompano": {"rarity": 2, "weight_range": (1, 8), "price_per_lb": 15},
    "🐠 Spotted Seatrout": {"rarity": 3, "weight_range": (1, 6), "price_per_lb": 12},
    "🐟 Croaker": {"rarity": 3, "weight_range": (0.5, 3), "price_per_lb": 7},
    "🐠 Cobia": {"rarity": 2, "weight_range": (10, 40), "price_per_lb": 22},
    "🐟 Grouper (Gag)": {"rarity": 2, "weight_range": (5, 40), "price_per_lb": 20},
    "🐟 Jack Crevalle": {"rarity": 3, "weight_range": (5, 20), "price_per_lb": 12},
    "🐟 Spanish Mackerel": {"rarity": 3, "weight_range": (1, 5), "price_per_lb": 10},
    "🐟 Skipjack Tuna": {"rarity": 2, "weight_range": (3, 10), "price_per_lb": 20},
    "🐠 Tilefish": {"rarity": 2, "weight_range": (2, 10), "price_per_lb": 16},
    "🐟 Spearfish": {"rarity": 1, "weight_range": (20, 50), "price_per_lb": 35},
    "🐟 Blackfin Tuna": {"rarity": 2, "weight_range": (10, 50), "price_per_lb": 25},
    "🦈 Bonnethead Shark": {"rarity": 1, "weight_range": (30, 350), "price_per_lb": 30},
    "🐟 Goliath Grouper": {"rarity": 1, "weight_range": (50, 500), "price_per_lb": 50},
    "🐠 Mangrove Snapper": {"rarity": 3, "weight_range": (2, 10), "price_per_lb": 14},
    "🐠 Vermilion Snapper": {"rarity": 3, "weight_range": (1, 4), "price_per_lb": 12},
    "🐟 King Mackerel": {"rarity": 2, "weight_range": (5, 40), "price_per_lb": 20},
    "🦈 Sandbar Shark": {"rarity": 1, "weight_range": (50, 200), "price_per_lb": 40},
    "🐠 Golden Tilefish": {"rarity": 2, "weight_range": (5, 20), "price_per_lb": 22},
    "🦈 Hammerhead Shark": {"rarity": 1, "weight_range": (50, 500), "price_per_lb": 50},
    "🦈 Great White Shark": {"rarity": 1, "weight_range": (350, 1700), "price_per_lb": 60},
    "🦈 Greenland Shark": {"rarity": 1, "weight_range": (500, 2200), "price_per_lb": 50},
    "🦈 Tiger Shark": {"rarity": 1, "weight_range": (300, 1200), "price_per_lb": 45},
    "🦈 Nurse Shark": {"rarity": 1, "weight_range": (50, 700), "price_per_lb": 40},
    "🦈 Lemon Shark": {"rarity": 1, "weight_range": (50, 250), "price_per_lb": 30},
    "🦈 Black Tipped Shark": {"rarity": 2, "weight_range": (25, 250), "price_per_lb": 30},
    "🦈 White Tipped Shark": {"rarity": 2, "weight_range": (25, 180), "price_per_lb": 30},
    "🦈 Bull Shark": {"rarity": 1, "weight_range": (50, 290), "price_per_lb": 40},
    "🐟 Barramundi": {"rarity": 2, "weight_range": (5, 30), "price_per_lb": 25},
    # Funny Items
    "🧦 Old Sock": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "🥤 Soda Can": {"rarity": 5, "weight_range": (0.2, 0.5), "price_per_lb": 0},
    "🚲 Rusty Bicycle": {"rarity": 5, "weight_range": (10, 15), "price_per_lb": 15},
    "📦 Mystery Box": {"rarity": 4, "weight_range": (1, 5), "price_per_lb": 250},
    "🎣 Fisherman's Hat": {"rarity": 4, "weight_range": (0.3, 0.7), "price_per_lb": 25},
    "🐠 Goldfish": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 50},
    "💡 Light Bulb": {"rarity": 5, "weight_range": (0.1, 0.3), "price_per_lb": 0},
    "🔑 Skeleton Key": {"rarity": 4, "weight_range": (0.2, 0.5), "price_per_lb": 50},
    "🐢 Teenage Mutant Ninja Turtle": {"rarity": 1, "weight_range": (10, 200), "price_per_lb": 100},
    "🍕 Slice of Pizza": {"rarity": 5, "weight_range": (0.3, 0.5), "price_per_lb": 0},
    "💎 Shiny Rock": {"rarity": 2, "weight_range": (0.1, 10), "price_per_lb": 2500},
    "🎲 Dice": {"rarity": 5, "weight_range": (0.05, 0.2), "price_per_lb": 0},
    "📜 Old Map": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 500},
    "🎸 Miniature Guitar": {"rarity": 4, "weight_range": (0.5, 1), "price_per_lb": 1000},
    "🔋 Dead Battery": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "📎 Paperclip": {"rarity": 5, "weight_range": (0.01, 0.05), "price_per_lb": 0},
    "🧸 Teddy Bear": {"rarity": 4, "weight_range": (0.5, 1), "price_per_lb": 0},
    "🍄 Mushroom": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 0},
    "🐕 Dog Toy": {"rarity": 5, "weight_range": (0.2, 0.5), "price_per_lb": 0},
    "🧻 Toilet Paper Roll": {"rarity": 5, "weight_range": (0.1, 0.3), "price_per_lb": 0},
    "📱 Old Cellphone": {"rarity": 4, "weight_range": (0.3, 0.7), "price_per_lb": 1000},
    "🧂 Salt Shaker": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "📅 Calendar from 2001": {"rarity": 5, "weight_range": (0.2, 0.5), "price_per_lb": 0},
    "🍏 Half-Eaten Apple": {"rarity": 5, "weight_range": (0.2, 0.4), "price_per_lb": 0},
    "👓 Broken Glasses": {"rarity": 5, "weight_range": (0.1, 0.3), "price_per_lb": 0},
    "🔨 Tiny Hammer": {"rarity": 4, "weight_range": (0.2, 0.5), "price_per_lb": 500},
    "🕹️ Retro Game Controller": {"rarity": 4, "weight_range": (0.3, 0.6), "price_per_lb": 2000},
    "🍺 Empty Beer Bottle": {"rarity": 5, "weight_range": (0.3, 0.6), "price_per_lb": 0},
    "🎒 Lost Backpack": {"rarity": 4, "weight_range": (2, 5), "price_per_lb": 1000},
    "🧤 Lost Glove": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "🍌 Banana Peel": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "🎈 Deflated Balloon": {"rarity": 5, "weight_range": (0.05, 0.1), "price_per_lb": 0},
    "📚 Waterlogged Book": {"rarity": 4, "weight_range": (1, 3), "price_per_lb": 0},
    "📚 An Old Porno Mag": {"rarity": 4, "weight_range": (1, 3), "price_per_lb": 0},
    "🎯 Dartboard": {"rarity": 4, "weight_range": (2, 4), "price_per_lb": 0},
    "🧩 Puzzle Piece": {"rarity": 5, "weight_range": (0.01, 0.03), "price_per_lb": 0},
    "📀 Slurms' Debut EP": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 1000},
    "📀 Nickelback CD": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "📀 Windows Millenium Edition CD": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "🍂 Leaf": {"rarity": 5, "weight_range": (0.01, 0.03), "price_per_lb": 0},
    "🧃 Juice Box": {"rarity": 5, "weight_range": (0.2, 0.4), "price_per_lb": 0},
    "🎨 Paint Can": {"rarity": 4, "weight_range": (1, 5), "price_per_lb": 0},
    "👞 Single Shoe": {"rarity": 5, "weight_range": (0.5, 1.5), "price_per_lb": 0},
    "📷 Disposable Camera": {"rarity": 4, "weight_range": (0.2, 0.5), "price_per_lb": 0},
    "🎁 Gift Box": {"rarity": 4, "weight_range": (0.5, 1.5), "price_per_lb": 1000},
    "🛠️ Wrench": {"rarity": 4, "weight_range": (0.5, 1), "price_per_lb": 0},
    "🎤 Microphone": {"rarity": 4, "weight_range": (0.3, 0.6), "price_per_lb": 1000},
    "🎭 Theater Mask": {"rarity": 4, "weight_range": (0.5, 1), "price_per_lb": 0},
    "💼 Briefcase": {"rarity": 4, "weight_range": (2, 5), "price_per_lb": 1000},
    "🎥 Film Reel": {"rarity": 4, "weight_range": (1, 3), "price_per_lb": 1000},
    "🎮 Game Cartridge": {"rarity": 4, "weight_range": (0.2, 0.5), "price_per_lb": 1000},
    "🎻 Violin": {"rarity": 3, "weight_range": (2, 5), "price_per_lb": 2500},
    "🕶️ Sunglasses": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 1000},
    "🎧 Headphones": {"rarity": 4, "weight_range": (0.3, 0.6), "price_per_lb": 1000},
    "🧢 Baseball Cap": {"rarity": 4, "weight_range": (0.2, 0.4), "price_per_lb": 0},
    "🍭 Lollipop": {"rarity": 5, "weight_range": (0.05, 0.1), "price_per_lb": 0},
    "🕰️ Pocket Watch": {"rarity": 4, "weight_range": (0.3, 0.5), "price_per_lb": 5000},
    "🦖 Toy Dinosaur": {"rarity": 5, "weight_range": (0.3, 0.6), "price_per_lb": 500},
    "📌 Thumbtack": {"rarity": 5, "weight_range": (0.01, 0.02), "price_per_lb": 0},
    "🎳 Bowling Pin": {"rarity": 4, "weight_range": (1, 2), "price_per_lb": 0},
    "🧯 Fire Extinguisher": {"rarity": 4, "weight_range": (2, 5), "price_per_lb": 0},
    "🏀 Basketball": {"rarity": 4, "weight_range": (0.5, 1), "price_per_lb": 0},
    "🚬 Cigarette Butt": {"rarity": 5, "weight_range": (0.01, 0.05), "price_per_lb": 0},
    "📼 'Straight to the A' VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 'A Bakers Dozen' VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 'Fresh Fucked Co-Eds' VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 'Oh No! Hes in My Ass!' VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 'Some awkward home made porn VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 'Ass-assins' VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 'Tridget the Midget VHS' Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 Blown Out Buttholes VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 '1 In The Pink, 1 In The Stink' VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "📼 'Ass Pirates of The Caribbean' VHS Tape": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 2500},
    "🌵 Tiny Cactus": {"rarity": 5, "weight_range": (0.2, 0.4), "price_per_lb": 0},
    "🍩 Donut with a Bite": {"rarity": 5, "weight_range": (0.2, 0.3), "price_per_lb": 0},
    "🎈 Balloon Animal": {"rarity": 4, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "🧼 Soap Bar": {"rarity": 5, "weight_range": (0.3, 0.5), "price_per_lb": 0},
    "🦴 Dinosaur Bone Replica": {"rarity": 3, "weight_range": (5, 10), "price_per_lb": 500},
    "🍀 Four-Leaf Clover": {"rarity": 4, "weight_range": (0.01, 0.02), "price_per_lb": 1000},
    "🚂 Toy Train": {"rarity": 4, "weight_range": (1, 2), "price_per_lb": 1000},
    "🍫 Chocolate Coin": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "🪁 Kite String": {"rarity": 5, "weight_range": (0.05, 0.1), "price_per_lb": 0},
    "🛹 Finger Skateboard": {"rarity": 5, "weight_range": (0.1, 0.2), "price_per_lb": 0},
    "🎒 Action Figure": {"rarity": 4, "weight_range": (0.2, 0.5), "price_per_lb": 500},
    "📂 Old Tax Documents": {"rarity": 5, "weight_range": (0.5, 1), "price_per_lb": 0},
    "📂 UGH's Personal Files": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Pricey's Medical Files": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Dime's Love Letters": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Angel's Journal Entries": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 UGH's Personal Files": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Copy of Dolores' DM's": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Catlady's Printed Text Messages": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Britney's Visa Application to Australia": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Caeleb's Research Papers": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 Nugs' Tax Returns": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📂 UGH's Personal Files": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "📚 Tang's Interior Design Book": {"rarity": 1, "weight_range": (0.5, 1), "price_per_lb": 5000},
    "🪕 Tiny Banjo": {"rarity": 3, "weight_range": (1, 2), "price_per_lb": 1000},
    "🧩 Missing Puzzle Piece": {"rarity": 5, "weight_range": (0.01, 0.02), "price_per_lb": 0},
    "🥇 Participation Trophy": {"rarity": 4, "weight_range": (0.3, 0.5), "price_per_lb": 0},
    "🚀 Rocket Ship Toy": {"rarity": 4, "weight_range": (0.5, 2), "price_per_lb": 1000},
    "🕵️‍♂️ Detective Badge": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 1000},
    "🐍 Rubber Snake": {"rarity": 5, "weight_range": (0.3, 0.5), "price_per_lb": 0},
    "👑 Plastic Crown": {"rarity": 4, "weight_range": (0.2, 0.4), "price_per_lb": 0},
    "🎩 Tiny Top Hat": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 0},
    "🍌 Squishy Banana": {"rarity": 5, "weight_range": (0.2, 0.4), "price_per_lb": 0},
    "🕶️ Spy Glasses": {"rarity": 4, "weight_range": (0.1, 0.3), "price_per_lb": 0},
    "💿 Duke Nukem 3D CD-ROM": {"rarity": 1, "weight_range": (0.1, 0.2), "price_per_lb": 2000},
    "🧪 Potion Bottle": {"rarity": 4, "weight_range": (0.3, 0.5), "price_per_lb": 500},
    "🦷 Fake Tooth": {"rarity": 5, "weight_range": (0.01, 0.02), "price_per_lb": 0},
    "🦸‍♂️ Superhero Cape": {"rarity": 4, "weight_range": (0.3, 0.6), "price_per_lb": 0},
    "🦴 Skeleton Arm": {"rarity": 1, "weight_range": (2, 3), "price_per_lb": 1000},
    "🦶 Severed Foot": {"rarity": 1, "weight_range": (3, 4), "price_per_lb": 2000},
    "🖐️ Disembodied Hand": {"rarity": 1, "weight_range": (2, 3), "price_per_lb": 1500},
    "🦷 Loose Tooth": {"rarity": 1, "weight_range": (0.05, 0.1), "price_per_lb": 500},
    "👂 Ear with an Earring": {"rarity": 1, "weight_range": (0.3, 0.5), "price_per_lb": 1200},
    "🦴 Rib Bone": {"rarity": 1, "weight_range": (1, 2), "price_per_lb": 800},
    "🦿 Prosthetic Leg": {"rarity": 4, "weight_range": (5, 10), "price_per_lb": 2500},
    "👁️ Eyeball": {"rarity": 1, "weight_range": (0.2, 0.3), "price_per_lb": 2000},
    "🧠 Brain in a Jar": {"rarity": 1, "weight_range": (3, 5), "price_per_lb": 5000},
    "🦴 Spine Segment": {"rarity": 1, "weight_range": (1, 2), "price_per_lb": 1000},
    "🦷 Gold Tooth": {"rarity": 1, "weight_range": (0.1, 0.2), "price_per_lb": 3000},
    "🦾 Bionic Arm": {"rarity": 1, "weight_range": (10, 15), "price_per_lb": 5000},
    "👃 Nose": {"rarity": 1, "weight_range": (0.2, 0.4), "price_per_lb": 1200},
    "👄 Pair of Lips": {"rarity": 3, "weight_range": (0.1, 0.2), "price_per_lb": 1000},
    }


class Fishing(commands.Cog):
    """Fishing"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234634604982350987318903467567890)
        self.config.register_user(caught_fish={}, largest_catch={"weight": 0, "fish": ""})

    def calculate_catch_chance(self, time_difference):
        # Define the catch chance based on the time difference
        min_time_difference = random.randrange(1, 5)
        max_time_difference = 10
        min_catch_chance = random.random()
        max_catch_chance = random.randrange(int(min_catch_chance * 100), 100) / 100

        # Map the time difference to a catch chance within the defined range
        normalized_time_difference = (time_difference - min_time_difference) / (
            max_time_difference - min_time_difference
        )
        catch_chance = (
            max_catch_chance - min_catch_chance
        ) * normalized_time_difference + min_catch_chance

        return abs(catch_chance)

    @commands.command(name="cast")
    async def cast(self, ctx: commands.Context):
        """Cast your line into the water."""
        message = await ctx.send(
            "You cast your line into the water. Click the 🎣 reaction to catch a fish."
        )
        
        wait_time = random.uniform(1, 4)
        await asyncio.sleep(wait_time)
        
        t1 = time.time()
        await ctx.message.add_reaction("🎣")

        try:
            await self.bot.wait_for(
                "reaction_add",
                check=lambda r, u: r.message.id == ctx.message.id
                and u.id == ctx.author.id
                and str(r.emoji) == "🎣",
                timeout=10,
            )

        except asyncio.TimeoutError:
            await ctx.message.clear_reactions()
            await message.edit(content="You didn't catch anything.")
            return

        t2 = time.time()
        diff = t2 - t1

        await ctx.message.clear_reactions()

        ch = self.calculate_catch_chance(diff)
        rand = random.random()

        if ch > rand:
            fish = random.choices(list(fishes.items()), weights=[f['rarity'] for f in fishes.values()])[0]
            rarity = "Common" if fish[1]['rarity'] == 3 else "Uncommon" if fish[1]['rarity'] == 2 else "Rare"
            weight = round(random.uniform(*fish[1]['weight_range']), 2)
            await self.add_fish_to_inventory(ctx.author, fish[0], weight)
            await message.edit(
                content=f"You caught a {fish[0]} weighing {weight} lbs! It is **{rarity}** and took you {diff:.2f} seconds to catch."
            )

        else:
            await message.edit(content="You didn't catch anything.")
        
    async def add_fish_to_inventory(self, user, fish, weight):
            user_fish = await self.config.user(user).caught_fish()
            if fish in user_fish:
                user_fish[fish].append(weight)
            else:
                user_fish[fish] = [weight]
            await self.config.user(user).caught_fish.set(user_fish)
            await self.update_largest_catch(user, fish, weight)
    
    async def update_largest_catch(self, user, fish, weight):
        largest_catch = await self.config.user(user).largest_catch()
        if weight > largest_catch["weight"]:
            await self.config.user(user).largest_catch.set({"weight": weight, "fish": fish})
    
    @commands.command(name="sellfish")
    async def sell_fish(self, ctx: commands.Context):
        """Sell all your fish for credits."""
        user_fish = await self.config.user(ctx.author).caught_fish()
        if not user_fish:
            await ctx.send("You don't have any fish to sell.")
            return

        total_credits = 0
        for fish, weights in user_fish.items():
            price_per_lb = fishes[fish]['price_per_lb']
            for weight in weights:
                credits = price_per_lb * weight
                total_credits += credits

        # Inform the user of the total credits earned
        await ctx.send(f"You sold your fish for {total_credits:.2f} bux!")

        # Clear the inventory after selling
        await self.config.user(ctx.author).caught_fish.set({})
        
    @commands.command(name="fishinventory", aliases=["myfish"])
    async def fish_inventory(self, ctx: commands.Context):
        """Check the fish currently in your inventory."""
        user_fish = await self.config.user(ctx.author).caught_fish()

        if not user_fish:
            await ctx.send("You don't have any fish in your inventory.")
            return

        inventory_message = "Your Current Fish Inventory:\n"
        for fish, weights in user_fish.items():
            total_weight = sum(weights)
            inventory_message += f"{fish}: {len(weights)} fish, Total weight: {total_weight:.2f} lbs\n"

        await ctx.send(inventory_message)
        
    @commands.command(name="fishing_leaderboard", aliases=["topfish"])
    async def leaderboard(self, ctx: commands.Context):
        """Show the leaderboard of the largest catches."""
        all_users = await self.config.all_users()
        leaderboard = []

        for user_id, data in all_users.items():
            if data["largest_catch"]["weight"] > 0:
                user = self.bot.get_user(user_id)
                if user:
                    leaderboard.append((user.name, data["largest_catch"]["fish"], data["largest_catch"]["weight"]))

        leaderboard = sorted(leaderboard, key=lambda x: x[2], reverse=True)[:10]

        if not leaderboard:
            await ctx.send("No fish have been caught yet.")
            return

        embed = discord.Embed(
            title="🏆 Largest Fish Caught Leaderboard 🏆",
            color=discord.Color.purple()
        )

        for idx, (user, fish, weight) in enumerate(leaderboard, 1):
            embed.add_field(
                name=f"{idx}. {user}",
                value=f"{fish} - {weight:.2f} lbs",
                inline=False
            )

        await ctx.send(embed=embed)