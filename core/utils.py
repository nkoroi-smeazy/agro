from .models import CommonInterestGroup

def assign_to_cig(farm_produce):
    locality = farm_produce.farm.locality
    produce_type = farm_produce.produce_type

    # Find existing CIGs in the locality for the given produce type
    cig_list = CommonInterestGroup.objects.filter(locality=locality, produce_type=produce_type).order_by('group_number')

    assigned = False
    for cig in cig_list:
        if cig.farm_produces.count() < 35:
            farm_produce.cig = cig
            assigned = True
            break

    if not assigned:
        new_group_number = cig_list.count() + 1
        new_cig = CommonInterestGroup.objects.create(
            locality=locality,
            produce_type=produce_type,
            group_number=new_group_number
        )
        farm_produce.cig = new_cig

    farm_produce.save()
