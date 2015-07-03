import distance
def ngramD(list1, list2, n=3):
	grams1 = genGram(n, list1)
	grams2 = genGram(n, list2)
	cost = distance.nlevenshtein(grams1,grams2)
	return cost

def genGram(n, clist):
	args = defineArgs(n, clist)
	grams = apply(zip, args)
	return grams

def defineArgs(n, clist):
	args = (clist,)
	for i in xrange(n):
		if i == 0:
			continue
		args += (clist[i:],)
	return args
