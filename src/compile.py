import ast
from variable_names import new_name
from ins import ast_ops, base_ins

# Gets a quoted string with its corresponding escapes
def str_quotes(s: str):
	return str({s})[1:-1]

# Generates bytecode from an AST node
def make_bytecode(n: ast.AST) -> list[str]:
	ret: list[str] = []

	if isinstance(n, ast.Module):
		for p in n.body:
			ret += make_bytecode(p)
			if isinstance(p, ast.Expr):
				ret += [ "v" ]

	elif isinstance(n, ast.If) or isinstance(n, ast.IfExp):
		nrm_body = [n.body] if isinstance(n, ast.IfExp) else n.body 
		nrm_else = [n.orelse] if isinstance(n, ast.IfExp) else n.orelse

		lab_name = new_name(map_idx=1)
		has_else = len(nrm_else) != 0
		lab_name_b = new_name(map_idx=1) if has_else else ""
		
		ret += make_bytecode(n.test)
		ret += [ "?" + lab_name ]
		for p in nrm_body:
			ret += make_bytecode(p)
			if isinstance(p, ast.Expr):
				ret += [ "v" ]
		if has_else: ret += [ "j" + lab_name_b ]
		ret += [ ":" + lab_name ]
		if has_else:
			for p in nrm_else:
				ret += make_bytecode(p)
				if isinstance(p, ast.Expr):
					ret += [ "v" ]
		ret += [ ":" + lab_name_b ]
	elif isinstance(n, ast.Compare):
		ret += make_bytecode(n.left)
		
		for i, (op, cp) in enumerate(zip(n.ops, n.comparators)):
			ret += make_bytecode(cp)
			if i != len(n.ops) - 1: ret += [ "y" ]
			ret += make_bytecode(op)
			if i != len(n.ops) - 1: ret += [ "h" ]
		ret += [ "w" ] * (len(n.ops) - 1)
	
	elif isinstance(n, ast.UnaryOp):
		ret += make_bytecode(n.operand)
		ret += make_bytecode(n.op)
	elif isinstance(n, ast.BinOp):
		ret += make_bytecode(n.left)
		ret += make_bytecode(n.right)
		ret += make_bytecode(n.op)
	elif type(n) in ast_ops:
		ret += ast_ops[type(n)]
	elif isinstance(n, ast.Expr):
		ret += make_bytecode(n.value)
	elif isinstance(n, ast.Call):
		# Add arguments and keyword args
		ret += [ "pSTP" ]
		for a in n.args: ret += make_bytecode(a)
		for k in n.keywords:
			ret += make_bytecode(k.value)
			if k.arg == None:
				print("WHAT? Function call keyword argument is weird")
				continue
			ret += [ "D" + str_quotes(k.arg), "pKAG" ]
		
		# Add the function call
		if isinstance(n.func, ast.Name):
			# TODO: implement user-defined functions
			ret += [ "p" + n.func.id ]
		elif isinstance(n.func, ast.Attribute):
			print("WHAT?? This is an attribute!")
		else:
			print(n.func)
			print("WHAT? There's a call to something that isn't a name")

		# Call it
		ret += [ "c" ]
	
	### ASSIGNMENT ###
	elif isinstance(n, ast.AugAssign):
		name = ""
		if isinstance(n.target, ast.Name):
			name = new_name(n.target.id)
		else:
			print(f"Non-name target found when doing `{n.op}`")
		ret += [ f'g"{name}"' ]
		ret += make_bytecode(n.value)
		ret += make_bytecode(n.op)
		ret += [ f's"{name}"' ]
	elif isinstance(n, ast.Assign):
		ret += make_bytecode(n.value)
		if len(n.targets) > 1:
			ret += [ 'd' + str(len(n.targets) - 1) ]
		for t in n.targets:
			if isinstance(t, ast.Name):
				real_name = new_name(t.id)
				ret += [ f's"{real_name}"' ]
			elif isinstance(t, ast.Tuple):
				ret += [ 'l' ]
				for e in t.elts:
					if isinstance(e, ast.Name):
						ret += [ f's"{new_name(e.id)}"' ]
					else:
						print("WHAT?")
			elif isinstance(t, ast.Subscript):
				ret += make_bytecode(t.slice)
				ret += make_bytecode(t.value)
				ret += [ "Y" ]
			else:
				print("WHAT?", t)
	
	elif isinstance(n, ast.Name):
		# Get a variable by name
		ret += [ f'g"{new_name(n.id)}"' ]
	
	### VALUES ###
	elif isinstance(n, ast.Constant):
		ret += [ 'p' + str({n.value})[1:-1] ]
	
	elif isinstance(n, ast.List):
		for e in n.elts:
			ret += make_bytecode(e)
		ret += [ "p" + str(len(n.elts)), "a" ]
	elif isinstance(n, ast.Subscript):
		ret += make_bytecode(n.value)
		ret += make_bytecode(n.slice)
		ret += [ "X" ]
	
	elif isinstance(n, ast.Tuple):
		cnt = 0
		for p in n.elts:
			cnt += 1
			ret += make_bytecode(p)
		ret += [ 'p' + str(cnt), 'a', 't' ]
	
	elif isinstance(n, ast.JoinedStr):
		for i, v in enumerate(n.values):
			ret += make_bytecode(v)
			if not (isinstance(v, ast.Constant) and isinstance(v.value, str)):
				ret += [ "S" ]
			if i > 0:
				ret += [ "+" ]
	
	elif isinstance(n, ast.FormattedValue):
		has_formatting = n.format_spec != None
		if has_formatting:
			if isinstance(n.format_spec, ast.JoinedStr) and \
				isinstance(n.format_spec.values[0], ast.Constant):
				ret += [ "p" + str_quotes("%" + n.format_spec.values[0].value) ]
			else:
				print("Weird formatting in f-string!", n.format_spec)
		ret += make_bytecode(n.value)
		if has_formatting:
			ret += [ "%" ]
	
	else:
		print(n)
		print(dir(n))
	
	# print(ret, n)
	return ret

def build_labels(bytecode: list[str]) -> list[str]:
	ret: list[str] = []
	labels: dict[str, int] = {}
	curr_idx = 0
	for b in bytecode:
		if b[0] == ":":
			labels[b[1:]] = curr_idx
		else:
			curr_idx += 1
	for b in bytecode:
		if b[0] in [ "?", "j" ]:
			ret += [ b[0] + str(labels[b[1:]]) ]
		elif b[0] != ":":
			ret += [ b ]
	return ret

# The things to replace in the instruction string
REPLACES: list[tuple[str, str,]] = [
	( "v+=[v.pop()", "¡" ),
	( "v.pop()", "_" ),
	( "a[0]", "`" ),
	( " v+=", "$" ),
]

### PACK THE INSTRUCTIONS! ###
def get_ins_len(instructions: list[str]):
	return len("".join(instructions))

# Compiles code into a single string, containing said code in a format similar
# to Python bytecode, but mostly version-independent.
def compile(code: str, quoted: bool = True):
	bytecode = make_bytecode(ast.parse(code, type_comments=True))
	bytecode = build_labels(bytecode)

	# bytecode.insert(4, "p'!\\n'")
	# bytecode.insert(5, "D'end'")

	# print("\n".join(bytecode))
	# exit()

	# bytecode = [ "" ]

	# Get all possible instructions
	instructions = base_ins[:]

	# Remove unused instructions
	used_ins = {}
	for b in bytecode:
		used_ins[b[0]] = 0
	instructions = [i for i in instructions if i[0] in used_ins]

	# Do replaces, skipping over ones that aren't worth it
	aggregate_replace_len = 0
	curr_ins_len = get_ins_len(instructions)
	executed_replaces: list[tuple[str, str]] = []
	for r in REPLACES:
		instructions: list[str] = [
			i.replace(r[0], r[1]) for i in instructions
		]
		new_replace_len = len(f".replace('{r[1]}','{r[0]}')")
		aggregate_replace_len += new_replace_len
		new_ins_len = get_ins_len(instructions) + aggregate_replace_len
		if new_ins_len > curr_ins_len:
			instructions: list[str] = [
				i.replace(r[1], r[0]) for i in instructions
			]
			aggregate_replace_len -= new_replace_len
			continue
		curr_ins_len = new_ins_len
		executed_replaces += [ r ]

	# Get the final instruction dict
	reverse_replaces = "".join([
		f".replace({str_quotes(r[1])},{str_quotes(r[0])})"
		for r in executed_replaces[::-1]
	]) + ".replace(';','\\n')"
	packed_ins = ",".join([f"'{a}'" for a in instructions])
	final_ins = f"h=dict(s{reverse_replaces}.split(' ',1)" \
		+ f"for s in[{packed_ins}])"

	### COMPRESS ###

	# GZIP, then put in a big integer
	from zlib import compress
	cmp_bytecode = compress("\n".join(bytecode).encode())

	### METHOD A ###

	# Encode using a charset
	big_num = int.from_bytes(cmp_bytecode)
	charset = " !#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]" \
		+ "^_`abcdefghijklmnopqrstuvwxyz{|}~¡"
	c_len = len(charset)
	final = ""
	while big_num != 0:
		final += charset[big_num % c_len]
		big_num //= c_len

	# Generate decompressor A
	decomp_a = f'__import__("zlib").decompress(sum([' \
		+ f'{len(charset)}**i*"{charset}".find(a)for i,a in enumerate("' \
		+ f'{final}")]).to_bytes({len(cmp_bytecode)})).decode().split("\\n")'

	### METHOD B ###

	# Generate decompressor B
	big_num = int.from_bytes(cmp_bytecode)
	decomp_b = f'__import__("zlib").decompress({hex(big_num)}.to_bytes(' \
		+ f'{len(cmp_bytecode)})).decode().split("\\n")'

	### METHOD C ###

	# Generate decompressor C (no compression)
	decomp_c = "[" + ",".join([str_quotes(a) for a in bytecode]) + "]"

	# Check which method is better! The heavier methods are better for larger
	# files, but smaller files usually benefit from being compressed less.
	final_decomp = min(decomp_a, decomp_b, decomp_c, key=len)

	final_code = f'q={final_decomp};STP=lambda:0;KAG=lambda:1;v=[];s={{}};x=0' \
		+ f';{final_ins}\nwhile x<len(q):x+=1;exec(f"a=[{{q[x-1][1:]}}]\\n"+h' \
		+ f'[q[x-1][0]],globals())'

	if quoted:
		return str_quotes(final_code)
	else:
		return final_code
