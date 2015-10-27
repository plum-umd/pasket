package java.lang;

public class StringBuffer implements CharSequence {
  char[] _value;
  int _count;

  public StringBuffer(String str) {
    _value = str._value;
    _count = str.length();
  }

  public char charAt(int index) {
    if (0 <= index && index < _count) return _value[index];
  }

  public int length() {
    return _count;
  }

  public String toString() {
    return new String(_value, 0, _count);
  }

  public void setCharAt(int i, char c) {
    _value[i] = c;
  }

  public StringBuffer append(int i) {
    return append(Integer.toString(i));
  }

  public StringBuffer append(String str) {
    // TODO
    return this;
  }
}
