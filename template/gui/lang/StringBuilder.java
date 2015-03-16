package java.lang;

public class StringBuilder implements CharSequence {
  char[] _value;
  int _count;

  public StringBuilder(String str) {
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

  public StringBuilder append(int i) {
    return append(Integer.toString(i));
  }

  public StringBuilder append(String str) {
    // TODO
    return this;
  }
}
