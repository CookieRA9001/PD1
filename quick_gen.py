import random

room = {}

class Vert():
    point = 0
    level = 0
    values = []
    next_verts = []
    
    def __init__(self, points, values, level):
        self.point = points
        self.values = values
        self.level = level
        h = hash((self.point, str(self.values).strip('[]')))
        if not h in room:
            room[h] = self
            self.next_verts = []
            self.next()
        else:
            self = room[h]

    def next(self):
        if self.values[0][1] == 0:
            return
        
        for i in range(len(self.values)):
            new_points = self.point
            temp_values = self.values.copy()
            v = self.values[i]

            if v[1] == 0:
                new_points -= 1
                temp_values.pop()
            else:
                v_sum = v[0]+v[1]
                new_points += 1
                if v_sum > 6:
                    v_sum -= 6
                    new_points += 1
                
                temp_values[i] = (v_sum,0)
            
            temp_values = self.cleanup(temp_values)
            self.next_verts.append(Vert(new_points, temp_values, self.level+1))

    def cleanup(self, values):
        new_v = []
        temp = []
        for i in values:
            if i[0] > 0:
                temp.append(i[0])
            if i[1] > 0:
                temp.append(i[1])
        
        l = len(temp)
        new_v = [(temp[x*2],temp[x*2+1]) for x in range((int)(l/2))]
        if l%2 != 0:
            new_v.append((temp[l-1],0))

        return new_v
    
    def print(self):
        print(self.level, ") ", self.values, " | ", self.point)
        for v in self.next_verts:
            v.print()
n = 20
values = []
values = [(random.randint(1,6),random.randint(1,6)) for x in range((int)(n/2))]
if n%2 != 0:
    values.append((random.randint(1,6),0))

print(values)
v = Vert(0, values, 0)
v.print()
print("Stats: ", len(room))



# pairs = [(6,5),(5,0)]
# points = 2
# depth = 2
# endDeep = 4
# w = 1

# if (points + (endDeep-depth)) % 2 == 0: # beigu gājiena punktu vērtības nav pair? 
#     two_point_pair_k = 1
# else:
#     two_point_pair_k = -1

# for p in pairs:
#     pair_value = 0
#     #...
#     if p[0]+p[1] > 6:
#         pair_value += w * two_point_pair_k
    
#     print(pair_value)
        
    