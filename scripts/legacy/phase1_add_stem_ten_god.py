"""Phase 1: Add stem_ten_god to Pillar class and all constructions in bazi_engine.py"""

from pathlib import Path
import re

p = Path('D:/shuntian/src/tongshu/engines/bazi_engine.py')
content = p.read_text(encoding='utf-8')

# Helper function to add ten_god to Pillar construction
def add_ten_god_to_pillar(match):
    """Add stem_ten_god parameter to Pillar() calls."""
    text = match.group(0)
    # Check if already has stem_ten_god
    if 'stem_ten_god' in text:
        return text
    
    # Extract arguments
    args = text[text.index('(')+1:text.index(')')]
    args = [a.strip() for a in args.split(',') if a.strip()]
    
    if len(args) >= 2:
        # Add stem_ten_god as third argument
        return f"Pillar({', '.join(args)}, _ten_god(day_master, {args[0]}))"
    return text

# Strategy: 
# 1. For year_p, month_p, day_p, hour_p - we know day_master at construction time
# 2. For luck_pillars - we also know day_master

# First, let's handle the _compute_with_sxtwl method
# Find day_master before pillar construction
# The day_master is four_pillars["day"].heavenly_stem which is computed after day_p

# Actually, let's use a different approach: 
# Compute stem_ten_god after all pillars are created, then replace them

print("Phase 1: Adding stem_ten_god to Pillar constructions...")

# Count occurrences
pillar_count = content.count('Pillar(')
print(f"Found {pillar_count} Pillar() constructions")

# Let's patch specific locations where we know day_master
# Pattern 1: year_p = Pillar(..., ...) followed by computing other pillars
# Pattern 2: day_p = Pillar(..., ...) - day_master known
# Pattern 3: luck_pillars loop

# For now, let's add a helper function and patch the key locations

# Add helper function after _ten_god definition
helper_func = '''

def _pillar_with_ten_god(day_master: str, stem: str, branch: str) -> Pillar:
    """Create a Pillar with pre-computed stem_ten_god."""
    return Pillar(stem, branch, _ten_god(day_master, stem))
'''

# Insert after the _ten_god function definition (around line 370)
insert_pos = content.find('_GENERATES = {')
if insert_pos > 0:
    content = content[:insert_pos] + helper_func + '\n' + content[insert_pos:]
    print("Added _pillar_with_ten_god helper function")

# Now patch all Pillar() constructions to use the helper
# We need to do this carefully by finding the right context

# Strategy: Replace Pillar(stem, branch) with _pillar_with_ten_god(day_master, stem, branch)
# But we need to know day_master at each location

# Let's use targeted replacements based on context

# Case 1: year_p = Pillar(...)
content = re.sub(
    r'year_p = Pillar\(([^)]+)\)',
    r'year_p = _pillar_with_ten_god(four_pillars["day"].heavenly_stem, \1)',
    content
)

# Case 2: month_p = Pillar(...)
content = re.sub(
    r'month_p = Pillar\(([^)]+)\)',
    r'month_p = _pillar_with_ten_god(four_pillars["day"].heavenly_stem, \1)',
    content
)

# Case 3: day_p = Pillar(...)
content = re.sub(
    r'day_p = Pillar\(([^)]+)\)',
    r'day_p = _pillar_with_ten_god(four_pillars["day"].heavenly_stem, \1)',
    content
)

# Case 4: hour_p = Pillar(...)
content = re.sub(
    r'hour_p = Pillar\(([^)]+)\)',
    r'hour_p = _pillar_with_ten_god(four_pillars["day"].heavenly_stem, \1)',
    content
)

# Case 5: four_pillars["day"] = Pillar(...)
content = re.sub(
    r'four_pillars\["day"\] = Pillar\(([^)]+)\)',
    r'four_pillars["day"] = _pillar_with_ten_god(four_pillars["day"].heavenly_stem, \1)',
    content
)

# Case 6: four_pillars["hour"] = Pillar(...)
content = re.sub(
    r'four_pillars\["hour"\] = Pillar\(([^)]+)\)',
    r'four_pillars["hour"] = _pillar_with_ten_god(four_pillars["day"].heavenly_stem, \1)',
    content
)

# Case 7: luck pillar loop
content = re.sub(
    r'lp = Pillar\(([^)]+)\)',
    r'lp = _pillar_with_ten_god(chart.day_master, \1)',
    content
)

# Case 8: four_pillars["month"] = Pillar(...)
content = re.sub(
    r'four_pillars\["month"\] = Pillar\(([^)]+)\)',
    r'four_pillars["month"] = _pillar_with_ten_god(four_pillars["day"].heavenly_stem, \1)',
    content
)

# Verify changes
new_pillar_count = content.count('_pillar_with_ten_god(')
old_pillar_count = content.count('Pillar(') - content.count('_pillar_with_ten_god(')

print(f"Added {new_pillar_count} calls to _pillar_with_ten_god")
print(f"Remaining direct Pillar() calls: {old_pillar_count}")

# Write back
p.write_text(content, encoding='utf-8')
print("Phase 1 completed successfully!")
