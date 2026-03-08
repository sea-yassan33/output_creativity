import sys
sys.dont_write_bytecode = True
def add(a, b):
  """2つの数を足す"""
  return a + b

def subtract(a, b):
  """aからbを引く"""
  return a - b

def multiply(a, b):
  """2つの数を掛ける"""
  return a * b

def divide(a, b):
  """aをbで割る"""
  if b == 0:
    raise ValueError("ゼロ除算は禁止です")
  return a / b
