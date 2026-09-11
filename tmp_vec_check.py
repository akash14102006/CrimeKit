from backend.app.embeddings import DeterministicProvider
import math
p=DeterministicProvider(dim=8)
v1=p.embed('apple')
v2=p.embed('banana')
q=p.embed('apple')

def cos(a,b):
    na=math.sqrt(sum(x*x for x in a))
    nb=math.sqrt(sum(x*x for x in b))
    if na==0 or nb==0:
        return 0
    return sum(x*y for x,y in zip(a,b))/(na*nb)

print('v1',v1)
print('v2',v2)
print('q',q)
print('cos(v1,q)', cos(v1,q))
print('cos(v2,q)', cos(v2,q))
