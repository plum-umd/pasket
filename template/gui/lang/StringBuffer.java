package java.lang;

public class StringBuffer {
  char[] _value;
  int _count;

  public StringBuffer(String str) {
    _value = str;
  }

  public void setCharAt(int i, char c) {
    _value[i] = c;
  }

  public String toString() {
    return _value;
  }

}
