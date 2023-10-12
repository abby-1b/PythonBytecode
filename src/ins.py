import ast

# The mappings from ast operation node to 
ast_ops: dict[type[ast.AST], str] = {
	ast.And    : "w", ast.Or      : "o",
	ast.Add    : "+", ast.Sub     : "-",
	ast.Mult   : "*", ast.Div     : "/",
	ast.MatMult: "@", ast.FloorDiv: "f",
	ast.Mod    : "%", ast.Pow     : "8",
	ast.LShift : ",", ast.RShift  : ".",
	ast.BitAnd : "&", ast.BitOr   : "|",
	ast.BitXor : "^", ast.Invert  : "~",
	ast.Not    : "!", ast.UAdd    : "#",
	ast.USub   : "x", ast.Eq      : "=",
	ast.Gt     : ">", ast.GtE     : "e",
	ast.In     : "i", ast.Is      : "b",
	ast.IsNot  : "n", ast.Lt      : "L",
	ast.LtE    : "E", ast.NotEq   : "N",
	ast.NotIn  : "I"
}

# The instructions themselves
base_ins = [
	"p v+=a",
	"s s[a[0]]=v.pop()",
	"g v+=[s[a[0]]]",

	# boolean operators
	"w z=v.pop();v+=[v.pop()and z]",
	"o z=v.pop();v+=[v.pop()or z]",

	# operators
	"+ z=v.pop();v+=[v.pop()+z]",
	"- z=v.pop();v+=[v.pop()-z]",
	"* z=v.pop();v+=[v.pop()*z]",
	"/ z=v.pop();v+=[v.pop()/z]",

	"@ z=v.pop();v+=[v.pop()@z]",
	"f z=v.pop();v+=[v.pop()//z]",
	"% z=v.pop();v+=[v.pop()%z]",
	"8 z=v.pop();v+=[v.pop()**z]",
	", z=v.pop();v+=[v.pop()<<z]",
	". z=v.pop();v+=[v.pop()>>z]",
	"& z=v.pop();v+=[v.pop()&z]",
	"| z=v.pop();v+=[v.pop()|z]",
	"^ z=v.pop();v+=[v.pop()^z]",

	# unary operators
	"~ v+=[~v.pop()]",
	"! v+=[not v.pop()]",
	"# v+=[+v.pop()]",
	"x v+=[-v.pop()]",

	# comparison operators
	"= v+=[v.pop()==v.pop()]", # `==` operator
	"> v+=[v.pop()<v.pop()]", # `>` operator
	"e v+=[v.pop()<=v.pop()]", # `>=` operator
	"i z=v.pop();v+=[v.pop()in z]", # `in` operator
	"b z=v.pop();v+=[v.pop()is z]", # `is` operator
	"n z=v.pop();v+=[v.pop()is not z]", # `is not` operator
	"L v+=[v.pop()>v.pop()]", # `<` operator
	"E v+=[v.pop()>=v.pop()]", # `<=` operator
	"N v+=[v.pop()!=v.pop()]", # `!=` operator
	"I z=v.pop();v+=[v.pop()not in z]", # `not in` operator

	"? if not v.pop():x=a[0]",
	"j x=a[0]",
	"D v+=[{a[0]:v.pop()}]",
	"c f=v.pop();k={};a=[];while v[-1]!=STP:; i=v.pop(); if i==KAG:k|=v.pop(); "
	"else:a+=[i];v.pop();v+=[f(*a[::-1],**k)]", # calls a normal function ^
	"d v+=[v.pop()]*(1+a[0])", # duplicates the topmost value n times
	"a l=[v.pop()];while l[0]>0:; l+=[v.pop()]; l[0]-=1;v+=[l[1:][::-1]]",
	# makes an array, using the first element as its length ^
	"t v+=[tuple(v.pop())]", # converts the topmost value into a tuple
	"l v+=list(v.pop())", # Deconstructs a tuple/array into its components
	"y z=v.pop();f=v.pop();v+=[z,f,z]", # turns `ab` into `bab`
	"h v+=[v.pop(),v.pop()]", # Swaps the last two values on the stack
	"S v+=[str(v.pop())]", # Stringifies the topmost value
	"v v.pop()", # Discards the topmost value
	"X z=v.pop();v+=[v.pop()[z]]", # Index into something
	"Y f=v.pop();z=v.pop();f[z]=v.pop()", # Set an index into something
]