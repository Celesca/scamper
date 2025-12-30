import difflib

def get_levenshtein_distance(s1, s2):
    """Simple Levenshtein distance implementation or use difflib for similarity."""
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def is_lookalike(domain, target_brand):
    """
    Checks if a domain is a lookalike of a target brand using various techniques.
    """
    domain = domain.lower()
    target = target_brand.lower()
    
    # Remove TLD for analysis
    domain_name = domain.split('.')[0]
    
    # 1. Direct containment (already handled, but good for completeness)
    if target in domain_name and domain_name != target:
        return True, "Containment"

    # 2. Similarity Ratio (Levenshtein)
    # If the domain is very similar but not identical
    similarity = get_levenshtein_distance(domain_name, target)
    if 0.7 <= similarity < 1.0:
        return True, f"High Similarity ({int(similarity*100)}%)"

    # 3. Simple replacement detection (o -> 0, l -> 1)
    replacements = {'o': '0', 'l': '1', 'i': '1', 'e': '3', 'a': '4', 's': '5', 't': '7'}
    fuzzed_target = target
    for char, rep in replacements.items():
        fuzzed_target = fuzzed_target.replace(char, rep)
        if fuzzed_target in domain_name:
            return True, "Character Replacement (Homoglyph-style)"

    # 4. Bitsquatting (Simplified: check for 1-char difference)
    if len(domain_name) == len(target):
        diff_count = sum(1 for a, b in zip(domain_name, target) if a != b)
        if diff_count == 1:
            return True, "Omission/Substitution (1-char diff)"

    return False, ""

def analyze_domain_advanced(domain, targets):
    results = []
    for target in targets:
        match, reason = is_lookalike(domain, target)
        if match:
            results.append({"target": target, "reason": reason})
    return results
