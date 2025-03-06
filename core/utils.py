# core/utils.py
from core.models import CommonInterestGroup

def assign_to_cig_bulk(farm_produce_list):
    """
    Assign each FarmProduce in farm_produce_list to an appropriate CIG,
    using a cache to reduce repeated DB queries.
    """
    # Cache structure: key = (locality_id, produce_type), value = list of dicts:
    # [{'cig': <CommonInterestGroup instance>, 'count': current_count}, ...]
    cache = {}
    
    for fp in farm_produce_list:
        locality_id = fp.farm.locality.id
        produce_type = fp.produce_type
        key = (locality_id, produce_type)
        
        if key not in cache:
            # Query existing CIGs for this locality and produce type
            cig_list = list(CommonInterestGroup.objects.filter(
                locality=fp.farm.locality, produce_type=produce_type
            ).order_by('group_number'))
            # Build cache entries with the current count (using .count() for each)
            cache[key] = [{'cig': cig, 'count': cig.farm_produces.count()} for cig in cig_list]
        
        assigned = False
        for entry in cache[key]:
            if entry['count'] < 35:
                fp.cig = entry['cig']
                entry['count'] += 1  # increment the cached count
                assigned = True
                break
        if not assigned:
            # No existing CIG has room, so create a new one.
            new_group_number = len(cache[key]) + 1
            new_cig = CommonInterestGroup.objects.create(
                locality=fp.farm.locality,
                produce_type=produce_type,
                group_number=new_group_number
            )
            fp.cig = new_cig
            cache[key].append({'cig': new_cig, 'count': 1})
        fp.save()
