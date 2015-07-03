def ngram(list1, list2):
	print 'stest'

def genGram(n, clist):
	args = defineArgs(n, clist)
	grams = apply(zip, args)
	return grams

def defineArgs(n, clist):
	args = (clist,)
	for i in xrange(n):
		i = i + 1
		args += (clist[i],)
	return args
