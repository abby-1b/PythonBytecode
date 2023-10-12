
import compile

if __name__ == "__main__":
	code = "print(1, 2, 3, sep='-', end='!\\n')"
	c = compile.compile(code, False)
	print("Produced code:")
	print(c)

	print("\nExpected output:")
	exec(code)

	print("\nOutput:")
	exec(c)
