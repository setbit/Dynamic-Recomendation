#import heapq
from sets import Set
from collections import defaultdict
import My_heap
import random
from collections import defaultdict

rating=defaultdict()

users=[]
items=[]

file=open('train.csv','rb')
for line in file:
        line=line.strip()
        line=line.split(',')
        if line[0] not in users:
                users.append(line[0])
        if line[1] not in items:
                items.append(line[1])
file.close()
for u in  users:
        rating[u]=defaultdict(float)
        for i in items:
                rating[u][i]=0
file=open('train.csv','rb')

for line in file:
        line=line.strip()
        line=line.split(',')
        #print line
        rating[line[0]][line[1]]=int(line[2])


f=open('prediction.csv','rb')

for line in f:
        line=line.strip()
        line=line.split('\t')
        #print line
        rating[line[0]][line[1]]=float(line[2])

f.close()
file.close()

U=users
T=3
P=defaultdict(int)
willing_to_pay=defaultdict(float)
for u in U:
        willing_to_pay[u]=random.randint(10,500)
C=1
k=10
I=items
beta=0.5
Class=defaultdict(int)
Q=defaultdict(int)
for i in I:
        Class[i]=1
        P[i]=random.randint(1,1000)
        Q[i]=20
EAP=defaultdict()
ratings=rating
#user_rating_dict=defaultdict(dict)

for u in U:
        AP=defaultdict(list)
        for i in I:
                for t in range(T):
                        AP[i].append(0.0)
        EAP[u]=AP

#def EAP():
Sum=0.0
mean=defaultdict()
count=defaultdict()
for c in range(C):
        mean[c+1]=0.0
        count[c+1]=0
for i in I:
        mean[Class[i]]+=float(P[i])
        count[Class[i]]+=1.0
for c in range(C):
        mean[c+1]=float(mean[c+1])/count[c+1]
#mean=(mean/Sum)
#Sum=0.0
for u in U:
        for key,value in ratings[u].iteritems():
                if P[key]<=willing_to_pay:
                        Sum+=float(value)/float(abs(P[key]-mean[Class[key]]))
        const=float(1.0/Sum)
        for key,value in ratings[u].iteritems():
                if P[key]<=willing_to_pay:
                        EAP[u][key][0]=(float(value)*const*float(value))/float(abs(P[key]-mean[Class[key]]))

#considering adoption probility
#willing to pay is constant

def calculate_EAP(S,z,Count_item,count_reco):
        u=z[0]
        i=z[1]
        t=z[2]
        if Count_item[i]<Q[i] and count_reco[u][t]<k:
                prod=1.000
                power=0.0
                for item in S:
                        item=list(item)
                        if Class[item[1]]==Class[i] and item[0]==u:
                                if item[2]==t:
                                        if i!=item[1]:
                                                prod*=(1.00-EAP[u][item[1]][0])
                                else:
                                        prod*=(1.00-EAP[u][item[1]][0])

                prod*=math.pow(beta,power)*EAP[u][i][0]
                return prod
        else:
                return 0.0


def calculate_REVs(S,z,reco_count,item_count):
        u=z[0]
        i=z[1]
        t=z[2]
        Sum=0.0
        Sum+=calculate_EAP(S,[u,i,t],Count_item,count_reco)
        for t_ in xrange(t+1,T):
                for j in I:
                        if Class[i]==Class[j]:
                                Z=[]
                                Z.append(u)
                                Z.append(j)
                                Z.append(t_)
                                Sum+=(math.pow(beta,1.0/float(t))(1-EAP[u][i][0])-1.0)*calculate_EAP(S,Z,item_count,reco_count)
        return P[i]*Sum

def condition(z,item_count,reco_count):
        z=list(z)
        #print item_count[z[1]]
        #print z
        if item_count[z[1]][z[2]]<=Q[z[1]]-1:
                if reco_count[z[0]][z[2]]<=k-1:
                        return True
        return False

# Q={i:q|i is item and q is stock}, P={i:[val]}, AP={(u,i,t):probaility} c=item_class
# k=10, beta=0.5

def G_Greedy(U,I,T,k,Q,P,beta,C):
        S=[]
        Upper_heap=[]
        Lower_heap=defaultdict()
        reco_count=defaultdict(list)
        item_count=defaultdict(list)
        for u in U:
                for t in range(T):
                        reco_count[u].append(0)
        for i in I:
                for t in range(T):
                        item_count[i].append(0)
        # item_count
        for u in U:
                Lower_heap[u]=defaultdict(list)
                for i in I:
                        Lower_heap[u][i]=[]
        Class_set=defaultdict()
        for u in U:
                class_set=defaultdict(list)
                for c in range(C):
                        class_set[c+1]=[]
                Class_set[u]=class_set
        
        flag=defaultdict()
        for u in U:
                Flag=defaultdict(list)
                for i in I:
                        for t in range(T):
                                rev_dict={}
                                rev_dict['triplet']=[u,i,t]
                                rev_dict['value']=EAP[u][i][0]
                                Lower_heap[u][i].append(rev_dict)
                                Flag[i].append(0)
                flag[u]=Flag
        #print flag
        for u in U:
                for i in I:
                        lower_heap=My_heap.heapify(Lower_heap[u][i])
                        Upper_heap.append(My_heap.pop_heap(lower_heap))
        upper_heap=My_heap.heapify(Upper_heap)
        while len(S)<k*T*len(U) and len(upper_heap)>0:
                #print S
                Rev=My_heap.pop_heap(upper_heap)
                z=list(Rev['triplet'])
                if z[2]==0:
                        Revs=Rev['value']
                else:
                        Revs=calculate_REVs(S,z,reco_count,item_count)
                if Revs<0:
                        break
                if condition(z,item_count,reco_count):
                        #print z
                        #print flag[z[0]][z[1]][z[2]]
                        if flag[z[0]][z[1]][z[2]]<len(Class_set[z[0]][Class[z[1]]]):
                                for X in range(len(Lower_heap[z[0]][z[1]])):
                                        rev=Lower_heap[z[0]][z[1]][X]
                                        rev['value']=calculate_REVs(S,list(rev['triplet']),reco_count,item_count)
                                        Lower_heap[z[0]][z[1]][X]=rev
                                        x=list(rev['triplet'])
                                        flag[x[0]][x[1]][x[3]]=len(Class_set[x[0]][Class[x[1]]])
                                Upper_heap=[]
                                for u in U:
                                        for i in I:
                                                lower_heap=My_heap.heapify(Lower_heap[u][i])
                                                Upper_heap.append(My_heap.pop_heap(lower_heap))
                                upper_heap=My_heap.heapify(Upper_heap)
                        elif flag[z[0]][z[1]][z[2]]==len(Class_set[z[0]][Class[z[1]]]):
                                S.append(z)
                                Class_set[z[0]][z[1]].append(z)
                                My_heap.heapify(Upper_heap)
                                My_heap.pop_heap(Upper_heap)
                                reco_count[z[0]][z[2]]+=1
                                item_count[z[1]][z[2]]+=1
                else:
                        My_heap.heapify(Upper_heap)
                        My_heap.pop_heap(Upper_heap)
                        Lower_heap[z[0]][z[1]]=[]
        return S

print G_Greedy(U,I,T,k,Q,P,beta,C)
