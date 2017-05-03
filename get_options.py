import re
import sys

# Parameters: (args, short_opts="", long_opts=[])
# 	args contains the list of command line arguments, excluding the script name (ie sys.argv[1:])
#
# 	short_opts contains all singly-hyphenated, single character arguments concatenated into one string
# 	- to use options, 'a' 'b' 'f' and 'g', say, you would use short_opts="abfg"
# 	- any options requiring additional arguments should be immediately followed by ':' or '=' (both are exactly equivalent)
# 	-- for example, if 'a' and 'f' require additional options, short_opts="a:bf:g"
# 	-- when passing command line options, they can be formatted as -abfg <argument_for_a> <argument_for_f>
#	-- or just as well, -a <argument_for_a> -bf <argument_for_f> -g
#
# 	long_opts contains a list of all long options, for example ["test:", "quiet", "name="]
# 	- same rules apply for ':' and '='

# Return Values: (options, arguments)
#	options : a dict whose keys are the options passed by the user, and whose values are the arguments (if any) for each option
#		eg.		python <script_name> -h --name Fred --verbose
#		would return {'h': '', 'name': 'Fred', 'verbose':''}
#
#	arguments : a list containing the 'leftover' arguments belonging to the script
#		eg.		python <script_name> --name Fred hello.txt 300
#		would return ['hello.txt', '300']

# Note that if an argument is given where none is expected,
# it, and all following options/arguments will be returned
# with the leftover arguments

def get_options(args, short_opts="", long_opts=[]):
	# keys = option names eg. 'verbose' or 'name'
	# values = bool -- does it take an argument
	allowed_options = {}
	all_opts = list(short_opts)
	for opt in long_opts:
		# if opt ends with '=' or ':', groups will add that to all_opts
		# immediately after the option name. When we iterate through
		# all_opts backwards, this character will act as a marker
		# so we will know that option takes an argument
		all_opts += re.search(r'^([^:=]*)([:=])?$', opt).groups()

	# all_options is a reverse iterator of all_opts
	all_options = reversed(all_opts)
	for opt in all_options:
		while not opt:
			opt = all_options.next()
		if opt in [':', '=']:
			opt = all_options.next()
			allowed_options[opt] = True
		else:
			allowed_options[opt] = False

	# these will eventually be our return values
	options = {}
	leftover_args = []

	arguments = iter(args)
	single_hyphen = re.compile(r'^-([a-zA-Z]*)$')
	double_hyphen = re.compile(r'^--([^-=][^=]+)(=([^=]*))?$')
	for arg in arguments:
		double_match = re.search(double_hyphen, arg)
		if double_match:
			opt, opt_arg = (double_match.group(1), double_match.group(3))
			if opt_arg:
				if not opt in allowed_options.keys():
					raise ValueError("Invalid option: {}".format(arg))
				if allowed_options[opt]:
					options[opt] = opt_arg
				else:
					raise ValueError("No arguments allowed for --{}".format(opt))
			given_opts = [opt]
		else:
			single_match = re.search(single_hyphen, arg)
			if single_match:
				given_opts = list(single_match.group(1))
			else:
				try:
					while True:
						leftover_args.append(arg)
						arg = arguments.next()
				except StopIteration:
					break

		# if double_match, this will contain a single element
		for opt in given_opts:
			if opt in allowed_options.keys():
				if not opt in options:
					if allowed_options[opt]:
						try:
							options[opt] = arguments.next()
						except StopIteration:
							raise ValueError("No argument provided for {}".format(arg))
					else:
						options[opt] = ""
			else:
				raise ValueError("Invalid option: {}".format(arg))
	return options, leftover_args

if __name__ == '__main__':
	# this is a random set of allowed arguments useable for testing
	print get_options(sys.argv[1:], "abcd:r=", ["test:", "quiet", "name="])
