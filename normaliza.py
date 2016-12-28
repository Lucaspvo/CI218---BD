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

######################################################

# Find all subsets closures
def find_subsets_closures(attributes_subsets, df_left, df_right, v_attr, normalization):
	
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
		
		if (normalization == "FNBC"):
			set_closure = set_of_cls - (set_of_cls - v_attr)
		else:
			set_closure = set_of_cls

		sets_of_closure.append(set_closure)
	
	return sets_of_closure

######################################################

# Find minimal candidate keys for the relation set of attributes
# according to the functional dependencies
def candidate_keys(sets_of_closure, attributes_subsets, v_attr):
	
	keys = []
	min_len = 100
	
	for idx, subset in enumerate(sets_of_closure):
	
		if not (v_attr - subset) and len(attributes_subsets[idx]) <= min_len:
	
			min_len = len(attributes_subsets[idx])
			keys.append(list(attributes_subsets[idx]))
	
	return keys

######################################################

# Normalization according to FNBC
def decompositionFNBC(v_attr, df_left, df_right, relations_resulted, node, normalization):
	
	new_attr_subsets = subsets(v_attr)
	new_sets_of_closure = find_subsets_closures(new_attr_subsets, df_left, df_right, v_attr, normalization)

	for idx, subset in enumerate(new_attr_subsets):
		
		if (subset == new_sets_of_closure[idx]) or (new_sets_of_closure[idx] == v_attr):
			pass
		else:
			
			y = new_sets_of_closure[idx] - subset
			z = v_attr - new_sets_of_closure[idx]
			r1 = subset | y
			r2 = subset | z

			if ((r1 not in relations_resulted) and (subset != r1)) or ((r2 not in relations_resulted) and (subset != r2)):

				relations_resulted.append(r1)
				relations_resulted.append(r2)
				node.l = Node(r1)
				node.r = Node(r2)
				decompositionFNBC(r1, df_left, df_right, relations_resulted, node.l, normalization)
				decompositionFNBC(r2, df_left, df_right, relations_resulted, node.r, normalization)

			break

######################################################

# Normalization according to 3FN
def decomposition3FN(df_left, df_right, normalization, v_attr, keys_org):

	# For loop to minimize DFs' right side
	len_to_be_added = []
	df_right_aux = list(df_right)

	for idx, df in enumerate(df_right_aux):
	
		if len(df) >= 2:
	
			elem_left = df_left.pop(idx)
			elem_right = df_right.pop(idx)
	
			for elem in elem_right:

				len_to_be_added.append(elem)
				df_left.append(elem_left)
				df_right.append(set(len_to_be_added))

	# For loop to minimize DFs' left side
	for idx, df in enumerate(df_left):

		exists = False

		if len(df) >= 2:

			sub_sets = subsets(df)
			df_left_aux = list(df_left)
			df_right_aux = list(df_right)
			subsets_closures = find_subsets_closures(sub_sets, df_left_aux, df_right_aux, df, normalization)

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
		subsets_closures = find_subsets_closures([df], df_left_aux, df_right_aux, df, normalization)

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

	# For loop to create a relation with the R key
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
	return relations_resulted
	
######################################################

# Function do print the results of the FNBC normalization
def print_fnbc(root, df_left, df_right, normalization, relation_name, v_attr):

	results = []

	relations_resulted = []
	relations_resulted.append(root)


	idx = 1
	
	while len(relations_resulted) > 0:

		node = relations_resulted.pop()

	
		if(node.l != None):
			if (node.l.v == v_attr):					
				print "resultado: ", relation_name
				return

			relations_resulted.append(node.l)
			keys = []
			rel_attributes_subsets = subsets(node.l.v)
			rel_sets_of_closure = find_subsets_closures(rel_attributes_subsets, df_left, df_right, node.l.v, normalization)
			keys = candidate_keys(rel_sets_of_closure, rel_attributes_subsets, node.l.v)
			print relation_name + str(idx) + '(' + ','.join(sorted(list(node.l.v))) + ')'
			
			if keys:
			
				for key in keys:
			
					print 'chave: ' + ','.join(sorted(list(key)))
				print
			
			if(node.l.l == None) and (node.l.r == None):
			
				results.append(relation_name + str(idx))
			
			idx += 1
	
	
		if(node.r != None):
			if (node.r.v == v_attr):					
				print "resultado: ", relation_name
				return
			relations_resulted.append(node.r)
			keys = []
			rel_attributes_subsets = subsets(node.r.v)
			rel_sets_of_closure = find_subsets_closures(rel_attributes_subsets, df_left, df_right, node.r.v, normalization)
			keys = candidate_keys(rel_sets_of_closure, rel_attributes_subsets, node.r.v)
			print relation_name + str(idx) + '(' + ','.join(sorted(list(node.r.v))) + ')'
			
			if keys:
			
				for key in keys:
			
					print 'chave: ' + ','.join(sorted(list(key))) 
				print
			
			if(node.r.l == None) and (node.r.r == None):
			
				results.append(relation_name + str(idx))
			
			idx += 1

		if(node.l == None) and (node.r == None) and (node.v == v_attr):
			print "resultado: ", relation_name
			return

	print "resultado: " + ','.join(results)
	return

######################################################

# Function do print the results of the 3FN normalization
def print_3fn(df_left, df_right, normalization, relation_name, v_attr, relations_resulted):

	results = []

	if (relations_resulted[0] == v_attr):
		print "resultado: ", relation_name
		return	

	for idx, relation in enumerate(relations_resulted):
		keys = []
		rel_attributes_subsets = subsets(relation)
		rel_sets_of_closure = find_subsets_closures(rel_attributes_subsets, df_left, df_right, relation, normalization)
		keys = candidate_keys(rel_sets_of_closure, rel_attributes_subsets, relation)
		print relation_name + str(idx+1) + '(' + ','.join(sorted(list(relation))) + ')'
		results.append(relation_name + str(idx+1))
	
		if keys:
	
			for key in keys:
	
				print 'chave: ' + ','.join(sorted(list(key)))

			print
	print "resultado: " + ','.join(results)
	return

######################################################

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

		elif count == 3:
			number_df = line
		else:
			try:
				df_split = line.split('->')
				df_left.append(set(df_split[0].split(',')))
				df_right.append(set(df_split[1].split(',')))
			except:
				pass
	
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
	sets_of_closure = find_subsets_closures(attributes_subsets, df_left, df_right, v_attr, normalization)
	#################################################

	# Find minimal candidate keys for the relation
	keys_org = sorted(candidate_keys(sets_of_closure, attributes_subsets, v_attr))
	##############################################

	# Print original relation attributes and its keys
	print relation_name + '(' + ','.join(sorted(list(v_attr))) + ')'
	for key in keys_org:
		print 'chave: ' + ','.join(sorted(list(key)))
	
	print
	if number_df == "0":
		print "resultado: ", relation_name
		return	
	#################################################

	# Normalize according to which form of normalization 
	# was passed at the beggining of the program
	if normalization == "FNBC":
		
		relations_resulted = []
		root = Node(v_attr)
		decompositionFNBC(v_attr, df_left, df_right, relations_resulted, root, normalization)
		print_fnbc(root, df_left, df_right, normalization, relation_name, v_attr)

	
	else:

		relations_resulted = decomposition3FN(df_left, df_right, normalization, v_attr, keys_org)
		print_3fn(df_left, df_right, normalization, relation_name, v_attr, relations_resulted)
		
	####################################################

	

if __name__ == "__main__":
	main()
