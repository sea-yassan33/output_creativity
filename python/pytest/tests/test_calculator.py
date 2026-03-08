import sys
sys.dont_write_bytecode = True
import pytest
from src.calculator import add, subtract, multiply, divide
# --- 基本テスト関数 ---
def test_add_positive_numbers():
  """正の数の加算"""
  result = add(3, 4)
  assert result == 7  # 期待値と比較

def test_add_negative_numbers():
  """負の数の加算"""
  assert add(-1, -2) == -3

def test_add_zero():
  """ゼロを含む加算"""
  assert add(5, 0) == 5

def test_subtract():
  assert subtract(10, 3) == 7

def test_multiply():
  assert multiply(4, 5) == 20

# ---- 基本的な parametrize ----
@pytest.mark.parametrize('a, b, expected', [
  (1, 2, 3),      # ケース1
  (-1, -2, -3),   # ケース2
  (0, 5, 5),      # ケース3
  (100, -50, 50), # ケース4
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

# ---- id でテスト名をわかりやすく ----
@pytest.mark.parametrize('a, b, expected', [
  pytest.param(10, 2, 5.0, id='正常ケース'),
  pytest.param(9, 3, 3.0, id='割り切れるケース'),
  pytest.param(1, 4, 0.25, id='小数点ケース'),
])
def test_divide_parametrized(a, b, expected):
  assert divide(a, b) == expected

# 直積（組み合わせ）を自動生成
@pytest.mark.parametrize('a', [1, 2, 3])
@pytest.mark.parametrize('b', [10, 20])
def test_multiply_combinations(a, b):
  # このテストは 3 x 2 = 6ケース実行される
  result = a * b
  assert result == a * b

# ---- 例外の発生を検証 ----
def test_divide_by_zero_raises():
  with pytest.raises(ValueError):
    divide(10, 0)

# ---- 例外メッセージも検証 ----
def test_divide_by_zero_message():
  with pytest.raises(ValueError, match='ゼロ除算は禁止です'):
    divide(10, 0)

# ---- 例外情報を取得して詳細チェック ----
def test_divide_by_zero_detail():
  with pytest.raises(ValueError) as exc_info:
    divide(10, 0)
  assert 'ゼロ除算' in str(exc_info.value)