import fileinput
from itertools import chain, combinations

# Class created to save the relations in a binary tree 
class Node:
    
    def __init__(self, val):
        
        self.l = None
        self.r = None
        self.v = val
######################################################

# Iterate over the attributes set and create all possible combinations
# for those attributes' set
def powerset(iterable):
    
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# Create all possible subsets for the attributes' set
def subsets(s):
    
    subsets_aux = []
    subsets = map(set, powerset(s))

    for set_list in subsets:
    
    	subsets_aux.append(sorted(list(set_list)))
    
    subsets_aux = sorted(subsets_aux)
    subsets_aux.sort(key=len)

    subsets = []

    for set_list in subsets_aux:

    	subsets.append(set(set_list))

    return subsets

# Find all subsets closures
def find_subsets_closures(attributes_subsets, df_left, df_right, v_attr):
	
	sets_of_closure = []
	
	for s in attributes_subsets:
	
		set_of_cls = s
		set_of_closure_aux = set()
	
		while set_of_cls != set_of_closure_aux:
	
			idx = 0
			set_of_closure_aux = set_of_cls
	
			for df in df_left:
	
				subset_result = df - set_of_cls
				if not subset_result:
					set_of_cls = (df_right[idx] | set_of_cls)
				idx = idx + 1
	
		sets_of_closure.append(set_of_cls)
	
	return sets_of_closure

# Find minimal candidate keys for the relation set of attributes
# according to the functional dependacies
def candidate_keys(sets_of_closure, attributes_subsets, v_attr):
	
	keys = []
	min_len = 100
	
	for idx, subset in enumerate(sets_of_closure):
	
		if not (v_attr - subset) and len(attributes_subsets[idx]) <= min_len:
	
			min_len = len(attributes_subsets[idx])
			keys.append(list(attributes_subsets[idx]))
	
	return keys

# Normalization according to FNBC
def decompositionFNBC(v_attr, df_left, df_right, relations_resulted, node):
	
	new_attr_subsets = subsets(v_attr)
	new_sets_of_closure = find_subsets_closures(new_attr_subsets, df_left, df_right, v_attr)
	
	for idx, subset in enumerate(new_attr_subsets):
		
		if (subset == new_sets_of_closure[idx]) or (new_sets_of_closure[idx] == v_attr):
			pass
		else:
			
			y = new_sets_of_closure[idx] - subset
			z = v_attr - new_sets_of_closure[idx]
			r1_aux = subset | y
			r2_aux = subset | z

			if len(r1_aux) < len(r2_aux):
				r1 = r1_aux
			else:
				r1 = r2_aux

			if len(r1_aux) < len(r2_aux):
				r2 = r2_aux
			else:
				r2 = r1_aux

			if ((r1 not in relations_resulted) and (subset != r1)) or ((r2 not in relations_resulted) and (subset != r2)):
				
				relations_resulted.append(r1)
				relations_resulted.append(r2)
				node.l = Node(r1)
				node.r = Node(r2)
				decompositionFNBC(r1, df_left, df_right, relations_resulted, node.l)
				decompositionFNBC(r2, df_left, df_right, relations_resulted, node.r)

			break

def main():
	
	count = 1
	v_attr = []
	df_left = []
	df_right = []
	relations_resulted = []

	# Read line by line from file passed in the command line
	for line in fileinput.input():
		
		line = line.strip('\n')
		
		if line == "FNBC":
		
			normalization = line
		
		elif line == "3FN":
		
			normalization = line
		
		elif count == 2:
		
			attr_split = line.split('(')
			relation_name = attr_split[0]
			attr_split = attr_split[1].split(',')
		
			for attr in attr_split:
		
				v_attr.append(attr.split(')')[0])
		
		else:
		
			df_split = line.split('->')
			df_left.append(set(df_split[0].split(',')))
			df_right.append(set(df_split[1].split(',')))
		
		count = count + 1
		pass
	#######################################################

	# Create all subsets for the relation attributes
	attributes_subsets = subsets(v_attr)
	################################################

	# Create the relation attributes' set
	v_attr = set(v_attr)
	#####################################

	# Find the closures of each subset created before
	sets_of_closure = find_subsets_closures(attributes_subsets, df_left, df_right, v_attr)
	#################################################

	# Find minimal candidate keys for the relation
	keys_org = sorted(candidate_keys(sets_of_closure, attributes_subsets, v_attr))
	##############################################

	# Print original relation attributes and its keys
	print relation_name + '(' + ','.join(sorted(list(v_attr))) + ')'
	for key in keys_org:
		print 'chave(' + ','.join(sorted(list(key))) + ')'
	print ''
	#################################################

	# Normalize according to which form of normalization 
	# was passed at the beggining of the program
	if normalization == "FNBC":
		
		relations_resulted = []
		root = Node(v_attr)
		decompositionFNBC(v_attr, df_left, df_right, relations_resulted, root)

		results = []

		relations_resulted = []
		relations_resulted.append(root)

		idx = 1
		
		while len(relations_resulted) > 0:

			node = relations_resulted.pop()

			if(node.l != None):
				
				relations_resulted.append(node.l)
				keys = []
				rel_attributes_subsets = subsets(node.l.v)
				rel_sets_of_closure = find_subsets_closures(rel_attributes_subsets, df_left, df_right, node.l.v)
				keys = candidate_keys(rel_sets_of_closure, rel_attributes_subsets, node.l.v)
				print relation_name + str(idx) + '(' + ','.join(sorted(list(node.l.v))) + ')'
				
				if keys:
				
					for key in keys:
				
						print 'chave(' + ','.join(sorted(list(key))) + ')\n'
				
				if(node.l.l == None) and (node.l.r == None):
				
					results.append(relation_name + str(idx))
				
				idx += 1

			if(node.r != None):
				
				relations_resulted.append(node.r)
				keys = []
				rel_attributes_subsets = subsets(node.r.v)
				rel_sets_of_closure = find_subsets_closures(rel_attributes_subsets, df_left, df_right, node.r.v)
				keys = candidate_keys(rel_sets_of_closure, rel_attributes_subsets, node.r.v)
				print relation_name + str(idx) + '(' + ','.join(sorted(list(node.r.v))) + ')'
				
				if keys:
				
					for key in keys:
				
						print 'chave(' + ','.join(sorted(list(key))) + ')\n'
				
				if(node.r.l == None) and (node.r.r == None):
				
					results.append(relation_name + str(idx))
				
				idx += 1

	else:

		# For loop to minimize DFs' right side
		for idx, df in enumerate(df_right):
		
			if len(df) >= 2:
		
				elem_left = df_left.pop(idx)
				elem_right = df_right.pop(idx)
		
				for elem in elem_right:
		
					df_left.append(elem_left)
					df_right.append(set(elem))

		# For loop to minimize DFs' left side
		for idx, df in enumerate(df_left):

			exists = False

			if len(df) >= 2:

				sub_sets = subsets(df)
				df_left_aux = list(df_left)
				df_right_aux = list(df_right)
				subsets_closures = find_subsets_closures(sub_sets, df_left_aux, df_right_aux, df)

				# if df == set(['A', 'B', 'H']):

				# 	print sub_sets
				# 	print subsets_closures

				for index, closure in enumerate(subsets_closures):

					if not df_right[idx] - closure:

						for ind, df_l in enumerate(df_left):

							if df_l == sub_sets[index] and df_right[idx] == df_right[ind]:

								exists = True

						if not exists and df != sub_sets[index]:

							df_left[idx] = sub_sets[index]
							df_right[idx] = df_right[idx]

						elif exists and df != sub_sets[index]:

							df_left.pop(idx)
							df_right.pop(idx)

		# For loop to remove extras DFs'
		for idx, df in enumerate(df_left):

			df_left_aux = list(df_left)
			df_right_aux = list(df_right)
			df_left_aux.pop(idx)
			df_right_aux.pop(idx)
			subsets_closures = find_subsets_closures([df], df_left_aux, df_right_aux, df)

			if not df_right[idx] - subsets_closures[0]:

				df_left.pop(idx)
				df_right.pop(idx)

		df_left_aux = list(df_left)
		df_right_aux = list(df_right)
		relations_resulted = []
		possible_relation = set()

		# For loop to generate possible relations from the existing DFs
		for idx, df in enumerate(df_left_aux):

			for index, elem in enumerate(df_left):

				if df == elem:

					possible_relation = possible_relation | elem | df_right[index]

			if possible_relation not in relations_resulted:

				relations_resulted.append(possible_relation)

			possible_relation = set()

		# For loop to eliminate relations which its set of attributes are subset 
		# of another relation set of attributes
		for idx, relation in enumerate(relations_resulted):
			
			for index, rel in enumerate(relations_resulted):
			
				if (relation != rel) and (not relation - rel):
			
					relations_resulted.pop(idx)

		exists = False

		for idx, relation in enumerate(relations_resulted):

			for index, key in enumerate(keys_org):

				if not exists and (not set(key) - set(relation)):

					exists = True
					break

			if exists:
		
				break

		attributes = v_attr

		if not exists:

			new_relation = keys_org[0]

			for idx, relation in enumerate(relations_resulted):

				attributes = attributes - relation

			new_relation = set(new_relation) | set(attributes)
			relations_resulted.append(new_relation)

		results = []

		for idx, relation in enumerate(relations_resulted):
			keys = []
			rel_attributes_subsets = subsets(relation)
			rel_sets_of_closure = find_subsets_closures(rel_attributes_subsets, df_left, df_right, relation)
			keys = candidate_keys(rel_sets_of_closure, rel_attributes_subsets, relation)
			print relation_name + str(idx+1) + '(' + ','.join(sorted(list(relation))) + ')'
			results.append(relation_name + str(idx+1))
			
			if keys:
			
				for key in keys:
			
					print 'chave(' + ','.join(sorted(list(key))) + ')'

				print
	####################################################

	print "resultado: " + ','.join(results)

if __name__ == "__main__":
	main()
