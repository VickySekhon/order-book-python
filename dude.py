def func(S):
     decimal_value = 0
     for i, included in enumerate(reversed(S)):
          decimal_value += (int(included) * (2**i))
          print(f"{included}*2^{i} = {int(included) * (2**i)} (sum={decimal_value})")
     print(decimal_value)
     
     operations = 0
     while decimal_value > 0:
          if is_even(decimal_value):
               decimal_value = decimal_value / 2
          else:
               decimal_value -= 1
          operations += 1
     return operations

def is_even(S):
     return S % 2 == 0

print(func("011100"))
print("")
print(func(""))
