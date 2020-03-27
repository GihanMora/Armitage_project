import clearbit
clearbit.key = 'sk_86d456666d55d0d2d86c74ccd7d6b639'

comp = clearbit.NameToDomain.find(name= 'OWNERS STRATA PLAN')
print(comp)