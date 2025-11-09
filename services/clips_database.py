"""
Database of infamous and iconic sports clips/moments.

Each clip has:
- keywords: list of terms that might trigger showing this clip
- title: display title
- description: brief context
- youtube_id: YouTube video ID
- timestamp: optional timestamp to start at
"""

INFAMOUS_CLIPS = {
    "kawhi_bounce": {
        "keywords": ["kawhi", "bounce", "game 7", "76ers", "raptors", "2019", "playoff shot"],
        "title": "Kawhi Leonard's Game 7 Buzzer Beater (2019)",
        "description": "Kawhi's shot bounced FOUR times on the rim before going in to beat the 76ers in Game 7. One of the most dramatic playoff moments ever.",
        "youtube_id": "ChT3ewZXTfM",
        "timestamp": None
    },
    "jr_smith_2018": {
        "keywords": ["jr smith", "j.r. smith", "2018 finals", "game 1", "finals blunder", "forgot the score", "lebron"],
        "title": "J.R. Smith's 2018 Finals Game 1 Blunder",
        "description": "With the game tied and seconds left, J.R. Smith grabbed the offensive rebound but dribbled away from the basket, seemingly forgetting the score. Cavaliers lost in overtime. LeBron's reaction says it all.",
        "youtube_id": "0SCWLyqAx-U",
        "timestamp": None
    },
    "butt_fumble": {
        "keywords": ["butt fumble", "mark sanchez", "jets", "patriots", "thanksgiving"],
        "title": "The Butt Fumble (2012)",
        "description": "Mark Sanchez ran into his own teammate's butt and fumbled on Thanksgiving. Possibly the most embarrassing play in NFL history.",
        "youtube_id": "rAp57G1hLn0",
        "timestamp": None
    },
    "28_3": {
        "keywords": ["28-3", "28 3", "falcons", "patriots", "super bowl 51", "comeback", "atlanta"],
        "title": "Patriots Overcome 28-3 Deficit - Super Bowl 51",
        "description": "The Falcons led 28-3 in the third quarter, but the Patriots completed the greatest comeback in Super Bowl history.",
        "youtube_id": "4SiUNdkIpdM",
        "timestamp": None
    },
    "malice_palace": {
        "keywords": ["malice at the palace", "ron artest", "metta world peace", "pistons", "pacers", "brawl"],
        "title": "Malice at the Palace (2004)",
        "description": "The biggest brawl in NBA history. Ron Artest (now Metta World Peace) went into the stands after a fan threw a drink at him.",
        "youtube_id": "7cTZsv42s3g",
        "timestamp": None
    },
    "zidane_headbutt": {
        "keywords": ["zidane", "headbutt", "world cup", "2006", "materazzi", "final"],
        "title": "Zidane's Headbutt - 2006 World Cup Final",
        "description": "In his final career match, Zinedine Zidane headbutted Marco Materazzi in the chest and was sent off. Italy went on to win the World Cup.",
        "youtube_id": "zAjWy7UNjEw",
        "timestamp": None
    },
    "tyree_catch": {
        "keywords": ["david tyree", "helmet catch", "super bowl 42", "giants", "patriots", "18-1"],
        "title": "David Tyree's Helmet Catch - Super Bowl 42",
        "description": "Tyree pinned the ball against his helmet while being tackled. This play helped the Giants beat the undefeated Patriots and ruin their perfect season.",
        "youtube_id": "CxiHMK_lm2s",
        "timestamp": None
    },
    "ray_allen_corner_three": {
        "keywords": ["ray allen", "corner three", "game 6", "2013 finals", "heat", "spurs"],
        "title": "Ray Allen's Game-Saving Three - 2013 Finals Game 6",
        "description": "With Miami down 3 and seconds left, Ray Allen hit the biggest three-pointer in Finals history to force overtime. Heat won the series.",
        "youtube_id": "tr6XsZVb-ZE",
        "timestamp": None
    },
    "lebron_block": {
        "keywords": ["lebron block", "the block", "2016 finals", "igoudala", "iguodala", "chase down"],
        "title": "LeBron's Block on Iguodala - 2016 Finals Game 7",
        "description": "The chase-down block that helped Cleveland win its first championship. One of the greatest defensive plays in Finals history.",
        "youtube_id": "py0-l1M_870",
        "timestamp": None
    },
    "mariano_comeback": {
        "keywords": ["mariners", "mariano rivera", "1995", "comeback", "116 wins", "refuse to lose"],
        "title": "1995 Mariners Refuse to Lose",
        "description": "Down 2-0 to the Yankees in the ALDS, the Mariners completed the comeback with Edgar Martinez's legendary double in Game 5.",
        "youtube_id": "F8SBkGpd_EE",
        "timestamp": None
    },
    "beast_quake": {
        "keywords": ["beast quake", "marshawn lynch", "seahawks", "earthquake", "saints", "2011", "beastmode"],
        "title": "Beast Quake - Marshawn Lynch (2011)",
        "description": "Marshawn Lynch's 67-yard touchdown run was so powerful it registered on a seismometer as an earthquake in Seattle.",
        "youtube_id": "xSZdntRnQVg",
        "timestamp": None
    },
    "malcolm_butler": {
        "keywords": ["malcolm butler", "interception", "super bowl 49", "seahawks", "patriots", "goal line"],
        "title": "Malcolm Butler's Super Bowl Interception",
        "description": "Instead of giving the ball to Marshawn Lynch, the Seahawks threw it. Malcolm Butler intercepted at the goal line, sealing the Patriots' win.",
        "youtube_id": "fKOLqM-LnA0",
        "timestamp": None
    },
    "fail_mary": {
        "keywords": ["fail mary", "hail mary", "seahawks", "packers", "replacement refs", "touchdown"],
        "title": "The Fail Mary (2012)",
        "description": "Replacement refs botched this call, giving the Seahawks a controversial touchdown on the final play against the Packers.",
        "youtube_id": "wXGFZkIEMK0",
        "timestamp": None
    },
    "double_doink": {
        "keywords": ["double doink", "cody parkey", "bears", "eagles", "field goal", "2019 playoffs"],
        "title": "The Double Doink",
        "description": "Cody Parkey's field goal attempt hit both the upright and crossbar before falling incomplete, ending the Bears' season.",
        "youtube_id": "vgAV7idfR7E",
        "timestamp": None
    },
    "miracle_minneapolis": {
        "keywords": ["minneapolis miracle", "stefon diggs", "vikings", "saints", "2018", "case keenum"],
        "title": "Minneapolis Miracle (2018)",
        "description": "Stefon Diggs caught the winning touchdown with no time left as the Saints safety missed the tackle. Vikings won on a walk-off TD.",
        "youtube_id": "dzRRi2QcSEM",
        "timestamp": None
    },
    "lebron_dunk_on_terry": {
        "keywords": ["lebron", "jason terry", "dunk", "poster", "celtics"],
        "title": "LeBron Posterizes Jason Terry",
        "description": "One of the most vicious dunks in playoffs history. Jason Terry tried to take a charge and immediately regretted it.",
        "youtube_id": "V-QTiByTKaI",
        "timestamp": None
    },
    "kobe_81": {
        "keywords": ["kobe", "81 points", "raptors", "2006", "scoring"],
        "title": "Kobe's 81-Point Game",
        "description": "Kobe Bryant's 81-point game against the Raptors in 2006. Second-highest scoring game in NBA history.",
        "youtube_id": "sZWEM7XWzUM",
        "timestamp": None
    },
    "jordan_last_shot": {
        "keywords": ["jordan", "last shot", "1998", "jazz", "finals", "push off"],
        "title": "Michael Jordan's Last Shot (1998 Finals)",
        "description": "MJ's final shot as a Bull. He pushed off Byron Russell and hit the championship-winning jumper.",
        "youtube_id": "vyL0FxS-F6E",
        "timestamp": None
    },
    "wide_right": {
        "keywords": ["wide right", "scott norwood", "bills", "super bowl", "1991"],
        "title": "Wide Right - Super Bowl 25",
        "description": "Scott Norwood missed a 47-yard field goal that would have won the Super Bowl for the Bills. It went wide right.",
        "youtube_id": "9GZHH5-S7-w",
        "timestamp": None
    }
}


def search_clips(query: str, max_results: int = 3) -> list[dict]:
    """
    Search for clips based on query string.

    Returns list of matching clips with their metadata.
    """
    query_lower = query.lower()
    matches = []

    for clip_id, clip_data in INFAMOUS_CLIPS.items():
        # Check if any keyword matches
        for keyword in clip_data["keywords"]:
            if keyword in query_lower:
                matches.append({
                    "clip_id": clip_id,
                    **clip_data
                })
                break

    return matches[:max_results]


def get_clip_by_id(clip_id: str) -> dict | None:
    """Get a specific clip by its ID."""
    return INFAMOUS_CLIPS.get(clip_id)


def get_all_clip_keywords() -> list[str]:
    """Get all keywords across all clips for LLM context."""
    keywords = set()
    for clip_data in INFAMOUS_CLIPS.values():
        keywords.update(clip_data["keywords"])
    return sorted(list(keywords))
