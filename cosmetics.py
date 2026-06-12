"""Catalog of equippable accessories sold in the shop.

Each cosmetic: id, display name, slot, price (in caps), and the art.draw_<draw>
function that renders it on the bird. One item may be equipped per slot, so the
bird can mix a hat + eyewear + neck + face + legs at once.
"""

# slot draw order is handled in art.draw_dressed_bird
COSMETICS = [
    # hats
    {"id": "party_hat", "name": "Party Hat",  "slot": "hat",  "price": 6,  "draw": "party_hat"},
    {"id": "cap_hat",   "name": "Ball Cap",   "slot": "hat",  "price": 8,  "draw": "cap_hat"},
    {"id": "top_hat",   "name": "Top Hat",    "slot": "hat",  "price": 14, "draw": "top_hat"},
    {"id": "crown",     "name": "Gold Crown", "slot": "hat",  "price": 25, "draw": "crown"},
    # eyewear
    {"id": "glasses",    "name": "Glasses",   "slot": "eyes", "price": 5,  "draw": "glasses"},
    {"id": "sunglasses", "name": "Shades",    "slot": "eyes", "price": 10, "draw": "sunglasses"},
    {"id": "goggles",    "name": "Goggles",   "slot": "eyes", "price": 12, "draw": "goggles"},
    # neck
    {"id": "bowtie", "name": "Bow Tie",     "slot": "neck", "price": 7,  "draw": "bowtie"},
    {"id": "chain",  "name": "Gold Chain",  "slot": "neck", "price": 18, "draw": "chain"},
    # face
    {"id": "mustache", "name": "Mustache",  "slot": "face", "price": 6,  "draw": "mustache"},
    # legs
    {"id": "pants", "name": "Fancy Pants",  "slot": "legs", "price": 9,  "draw": "pants"},
]

_BY_ID = {c["id"]: c for c in COSMETICS}

SLOTS = ["hat", "eyes", "neck", "face", "legs"]


def get(cid):
    """Return the cosmetic dict for an id, or None."""
    return _BY_ID.get(cid)


def equipped_list(save_data):
    """Resolve save_data['equipped'] (slot -> id) into a list of cosmetic dicts."""
    equipped = save_data.get("equipped", {}) or {}
    out = []
    for slot in SLOTS:
        cid = equipped.get(slot)
        if cid and cid in _BY_ID:
            out.append(_BY_ID[cid])
    return out
