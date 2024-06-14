# fighting_constants.py

STRIKES = {
    "Karate": {
        "Straight Right": (5, 7),
        "Straight Left": (6, 8),
        "Left Cross": (4, 6),
        "Right Cross": (4, 6),
        "Hook": (5, 7),
        "Uppercut": (6, 8),
        "Backfist": (4, 6),
        "Ridgehand": (5, 7),
        "Knifehand": (5, 7),
        "Palm Strike": (4, 6),
        "Hammerfist": (5, 7),
        "Spearhand": (6, 8),
        "Reverse Punch": (7, 9),
        "Reverse Knifehand": (7, 9),
        "Reverse Hammerfist": (7, 9),
        "Reverse Spearhand": (8, 10),
        "Reverse Backfist": (7, 9),
        "Reverse Ridgehand": (7, 9),
        "Chop": (4, 6),
        "Knee Strike": (5, 7)
    },
    "Muay-Thai": {
        "Elbow": (6, 8),
        "Knee": (5, 7),
        "Clinch": (4, 6),
        "Teep": (4, 6),
        "Low Kick": (5, 7),
        "High Kick": (6, 8),
        "Body Kick": (5, 7),
        "Uppercut": (5, 7),
        "Spinning Elbow": (7, 9),
        "Spinning Back Elbow": (7, 9),
        "Spinning Back Kick": (7, 9),
        "Flying Knee": (7, 9),
        "Flying Elbow": (7, 9),
        "Flying Kick": (7, 9),
        "Superman Punch": (7, 9),
        "Jumping Knee": (7, 9),
        "Jumping Elbow": (7, 9)
    },
    # Add other fighting styles similarly
}

BODY_PARTS = [
    "head", "chest", "left arm", "right arm", "nose", "neck", "left ear", "right ear",
    "teeth", "left leg", "right leg", "right foot", "left foot", "liver", "kidneys",
    "spine", "clavical", "left hip", "right hip", "left knee", "right knee", "solar plexus",
    "cranium", "kisser", "chin", "left shoulder", "right shoulder", "ass", "crotch", "spine", "ribs", "spinal column"
]

ACTIONS = [
    "throws", "slams", "nails", "whacks", "connects", "rips", "thuds", "crushes", "snaps", "smashes", 
    "pounds", "cracks", "hits", "drives", "lands"
]

CRITICAL_MESSAGES = [
    "Channeling the power of the Dim Mak strike,",
    "Harnessing the technique bestowed upon them by the Black Dragon Fighting Society,",
    "Channeling the Grand Master Ashida Kim,",
    "Summoning the power of Count Dante,"
]

CRITICAL_CONCLUDES = [
    "{defender} is left in a crumpled heap on the floor.",
    "{defender} is left gasping for air.",
    "{defender} is left with a broken nose.",
    "{defender} is left with a shattered rib.",
    "{defender} is left with a dislocated shoulder.",
    "{defender} is left with a broken jaw.",
    "{defender} is left with a concussion.",
    "{defender} is left with a broken leg.",
    "{defender} is left with a broken arm.",
    "{defender} is left with a broken collarbone.",
    "{defender} is left with a broken wrist.",
    "{defender} is left with a broken ankle.",
    "{defender} is left with a broken finger.",
    "{defender} is left with a broken toe.",
    "{defender} is left with a broken nose.",
    "{defender} is left with a broken rib.",
    "{defender} is left with a broken shin.",
    "{defender} is left with a broken thigh.",
    "{defender} is left with a broken kneecap.",
    "{defender} is left with a broken foot.",
    "{defender} is left with a broken hand.",
    "{defender} is cut over the eye.",
    "{defender} is left with a black eye.",
    "{defender} is left with a bloody nose.",
    "{defender} is left with a bloody lip.",
    "{defender} is left with a bloody ear.",
    "{defender} is left with a bloody mouth.",
    "{defender} is left with a bloody forehead.",
    "{defender} is left with a bloody cheek."
]
