"""Shared figure settings for the plotting scripts in Analysis/.

One place for the font ladder, tick and legend defaults, entity colours and
deterministic file output, so every committed figure follows the same rules.
Plotting only: nothing here touches a computed value.
"""
from contextlib import contextmanager
from pathlib import Path

import matplotlib
from matplotlib.colors import to_rgb

# Three font sizes by role: titles, axis labels and series names; legends and
# annotations; tick labels. Panel letters are the only larger text.
BASE, SMALL, TICK = 10, 9, 8
LETTER = 12

INK = '#222222'
GRAY = '#62676d'
LIGHT = '#d6d9dc'

# One colour per entity, reused in every figure that shows that entity.
# Parameter tiers are ordered, so they share one hue at three depths.
TIER = {'best': '#00441b', 'nominal': '#238b45', 'worst': '#74c476'}
# Design packages in the survivable-set study (Okabe-Ito, no red/green pair).
ACTION = {'realloc_only': '#0072B2', 'mechanism': '#E69F00', 'parachute': '#CC79A7'}
ACTION_NAME = {'realloc_only': 'Thrust reallocation only',
               'mechanism': 'Guard mechanism',
               'parachute': 'Parachute-like device'}
FAILURE_NAME = {'one_out': 'One rotor out',
                'partial_authority': 'Partial authority (60%)',
                'two_adjacent': 'Two adjacent rotors out',
                'two_opposite': 'Two opposite rotors out'}
# NanoBench documented motor models and the persistence comparator.
MODEL = {'cf21plus_firmware': '#0072B2', 'thrust_upgrade_firmware': '#D55E00',
         'legacy_propellers_firmware': '#009E73', 'persistence': '#333333'}
# QDrone2 channels and command directions, as chosen in PR #60.
QDRONE = {'altitude': '#2980b9', 'voltage': '#27ae60', 'reference': GRAY,
          'up': '#2980b9', 'down': '#7d3c98'}

RC = {
    'font.size': BASE, 'axes.titlesize': BASE, 'axes.labelsize': BASE,
    'legend.fontsize': SMALL, 'legend.title_fontsize': SMALL,
    'xtick.labelsize': TICK, 'ytick.labelsize': TICK,
    'figure.titlesize': BASE, 'figure.labelsize': BASE,
    'axes.titlelocation': 'left', 'axes.titleweight': 'normal', 'axes.titlepad': 6,
    'xtick.direction': 'out', 'ytick.direction': 'out',
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#80858a', 'axes.labelcolor': INK, 'text.color': INK,
    'xtick.color': INK, 'ytick.color': INK,
    'axes.grid': False, 'grid.color': LIGHT, 'grid.linewidth': .6,
    'legend.frameon': False,
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'savefig.facecolor': 'white', 'savefig.dpi': 300,
    'pdf.fonttype': 42,
}


@contextmanager
def style():
    """Apply the shared settings for the duration of one figure."""
    with matplotlib.rc_context(RC):
        yield


def tint(color, amount=.35):
    """Mix a colour with white; amount=1 keeps the colour, 0 gives white."""
    r, g, b = to_rgb(color)
    return (1 - amount + amount*r, 1 - amount + amount*g, 1 - amount + amount*b)


def panel_letter(fig, ax, letter, dx=-.06, dy=.02):
    """Bold panel letter just outside the top-left corner of an axes."""
    box = ax.get_position()
    fig.text(box.x0 + dx, box.y1 + dy, letter, fontsize=LETTER,
             fontweight='bold', ha='left', va='bottom')


def save(fig, path, formats=('png',)):
    """Write a 300-dpi PNG and any vector copies without timestamps."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        out = path.with_suffix('.' + ext)
        if ext == 'pdf':
            fig.savefig(out, metadata={'CreationDate': None, 'ModDate': None})
        else:
            fig.savefig(out, dpi=300)
