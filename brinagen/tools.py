def unique(sequence):

    """ Returns a list of unique elements in input list. """
    
    seen = set()
    seen_add = seen.add
    return [x for x in sequence if not (x in seen or seen_add(x))]
