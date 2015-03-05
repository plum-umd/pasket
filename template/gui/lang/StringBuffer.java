package java.lang;

public class StringBuffer implements CharSequence {
  char[] _value;
  int _count;

  public StringBuffer(String str) {
    _value = str;
    _count = str.length();
  }

  public int length() {
    return _count;
  }

  public String toString() {
    return _value;
  }

  public void setCharAt(int i, char c) {
    _value[i] = c;
  }

}
